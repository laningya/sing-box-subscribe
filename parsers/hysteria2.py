import re
from urllib.parse import urlparse, parse_qs, unquote

import tool


def _parse_port_ranges(value):
    ranges = []
    for item in value.split(','):
        match = re.fullmatch(r'([0-9]{1,5})(?:\s*[-:]\s*([0-9]{1,5}))?', item.strip())
        if not match:
            return []
        start = int(match[1])
        end = int(match[2]) if match[2] else start
        if not 1 <= start <= end <= 65535:
            return []
        ranges.append(f'{start}:{end}')
    return ranges


def parse(data):
    server_info = urlparse(data)
    query = parse_qs(server_info.query)
    netquery = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in query.items()
    )
    authority = server_info.netloc.rsplit('@', 1)[-1]
    address = re.fullmatch(r'(\[[^\]]+\]|[^:\[\]]+)(?::(.*))?', authority)
    if not address:
        return None
    host, port_spec = address.groups()
    port_spec = (port_spec or '443').strip()

    # Prefer the subscription's hopping range over its advertised single port.
    server_ports = _parse_port_ranges(','.join(query.get('mport', [])))
    if server_ports:
        port_options = {'server_ports': server_ports, 'hop_interval': '30s'}
    else:
        server_ports = _parse_port_ranges(port_spec)
        if not server_ports:
            return None
        if port_spec.isdecimal():
            port_options = {'server_port': int(port_spec)}
        else:
            port_options = {'server_ports': server_ports, 'hop_interval': '30s'}

    node = {
        'tag': unquote(server_info.fragment) or tool.genName()+'_hysteria2',
        'type': 'hysteria2',
        'server': host.strip('[]'),
        **port_options,
        "password": netquery['auth'] if netquery.get('auth') else server_info.netloc.split("@")[0].rsplit(":", 1)[-1],
        'up_mbps': int(re.search(r'\d+', netquery.get('upmbps', '10')).group()),
        'down_mbps': int(re.search(r'\d+', netquery.get('downmbps', '100')).group()),
        'tls': {
            'enabled': True,
            'server_name': netquery.get('sni', netquery.get('peer', '')),
            'insecure': False
        }
    }
    if netquery.get('insecure') in ['1', 'true'] or netquery.get('allowInsecure') == '1':
        node['tls']['insecure'] = True
    if node['tls']['server_name'] == '':
        del node['tls']['server_name']
        node['tls']['insecure'] = True
    node['tls']['alpn'] = (netquery.get('alpn') or "h3").strip('{}').split(',')
    if netquery.get('obfs', '') not in ['none', '']:
        node['obfs'] = {
            'type': netquery['obfs'],
            'password': netquery['obfs-password'],
        }
    return (node)
