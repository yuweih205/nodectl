# nodectl/config.py

import json
import os
import re
from pathlib import Path

# 默认节点配置文件路径，可通过环境变量 NODECTL_CONFIG 修改
NODE_FILE = (
    os.environ.get("NODECTL_CONFIG")
    or os.path.join(os.path.dirname(__file__), "../nodes.json")
)

IP_PATTERN = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
HOST_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]+$")

def _is_valid_node(name: str) -> bool:
    return bool(IP_PATTERN.match(name) or HOST_PATTERN.match(name))

def load_nodes():
    if not os.path.exists(NODE_FILE):
        raise FileNotFoundError(f"节点配置文件不存在: {NODE_FILE}")

    with open(NODE_FILE) as f:
        data = json.load(f)
        nodes = data.get("nodes", [])
        valid_nodes = [n.strip() for n in nodes if _is_valid_node(n.strip())]
        return sorted(valid_nodes)

def get_all_nodes():
    """热更新接口：每次调用都重新读取节点文件"""
    return load_nodes()

