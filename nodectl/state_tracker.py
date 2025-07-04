from .config import get_all_nodes
from .gpu_probe import probe_available_nodes
from .manual_blocker import load_manual_block
from typing import List

# 内存状态持久化（记录 SSH 启动失败节点）
UNAVAILABLE = set()

def mark_node_unavailable(node: str):
    UNAVAILABLE.add(node)

def reset_unavailable_nodes():
    UNAVAILABLE.clear()

def get_available_nodes() -> List[str]:
    """真实可调度节点 = 探测为GPU空闲 & 不在手动禁用列表 & 未启动失败"""
    all_nodes = set(get_all_nodes())
    available = set(probe_available_nodes())
    manual_block = load_manual_block()

    final = available - manual_block - UNAVAILABLE
    return sorted(final)

def get_unavailable_nodes() -> List[str]:
    """剩余所有节点中未被视为可调度的就是不可用的"""
    all_nodes = set(get_all_nodes())
    available = set(get_available_nodes())
    return sorted(all_nodes - available)

def print_available_nodes():
    nodes = get_available_nodes()
    print(f"✅ 当前可用节点（{len(nodes)}台）:")
    for n in nodes:
        print(f"  - {n}")

def print_unavailable_nodes():
    nodes = get_unavailable_nodes()
    print(f"❌ 当前不可用节点（{len(nodes)}台）:")
    for n in nodes:
        print(f"  - {n}")
