#!/bin/bash

# 定义目标路径
CONFIG_DIR=~
CONFIG_FILE=config.json
BACKUP_FILE=bak
DOWNLOAD_URL=""

# 检查目标文件夹是否存在
if [ ! -d "$CONFIG_DIR" ]; then
    echo "目标文件夹 $CONFIG_DIR 不存在，创建中..."
    mkdir -p "$CONFIG_DIR"
fi

# 检查目标文件是否存在
if [ -f "$CONFIG_DIR/$CONFIG_FILE" ]; then
    # 重命名文件
    mv "$CONFIG_DIR/$CONFIG_FILE" "$CONFIG_DIR/$BACKUP_FILE"
    echo "文件已成功重命名为 $BACKUP_FILE"
else
    echo "未找到 $CONFIG_FILE 文件，无需重命名"
fi

# 下载新的 config.json 文件
echo "开始下载新的 $CONFIG_FILE 文件..."
wget -O "$CONFIG_DIR/$CONFIG_FILE" "$DOWNLOAD_URL"

# 检查下载结果
if [ $? -eq 0 ]; then
    echo "新的 $CONFIG_FILE 文件已成功下载至 $CONFIG_DIR"
else
    echo "下载失败，请检查 URL 或网络连接"
fi
