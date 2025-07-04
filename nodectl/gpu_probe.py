import asyncio
from datetime import datetime
from typing import List
from ipaddress import IPv4Address
from .config import get_all_nodes
from .manual_blocker import load_manual_block

nodes = get_all_nodes()

GPU_EMPTY_THRESHOLD_MB = 50
EXPECTED_GPU_COUNT = 8
NVIDIA_SMI_CMD = "nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits"

class GPUStatus:
    def __init__(self, host: str, memory_usage: List[float]):
        self.host = host
        self.memory_usage = memory_usage
        self.timestamp = datetime.now()

    @property
    def ip_number(self) -> int:
        return int(IPv4Address(self.host))

    @property
    def is_available(self) -> bool:
        return (
            len(self.memory_usage) == EXPECTED_GPU_COUNT and
            all(mem <= GPU_EMPTY_THRESHOLD_MB for mem in self.memory_usage)
        )

async def query_gpu(host: str) -> GPUStatus:
    try:
        cmd = f"ssh {host} '{NVIDIA_SMI_CMD}'"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        if proc.returncode == 0:
            memory = [float(x.strip()) for x in stdout.decode().strip().splitlines()]
        else:
            memory = []
    except Exception:
        memory = []
    return GPUStatus(host, memory)

def probe_available_nodes() -> List[str]:
    """同步入口：探测所有 GPU 空闲节点"""
    return asyncio.run(_probe_available_nodes())

async def _probe_available_nodes() -> List[str]:
    manual_block = load_manual_block()
    tasks = [query_gpu(n) for n in get_all_nodes() if n not in manual_block]
    results = await asyncio.gather(*tasks)
    available = [r.host for r in results if r.is_available]
    available.sort(key=lambda h: int(IPv4Address(h)))
    return available

def print_unavailable_nodes():
    all_nodes = get_all_nodes()
    available = set(probe_available_nodes())
    unavailable = sorted(n for n in all_nodes if n not in available)

    print(f"❌ 当前不可用节点（{len(unavailable)}台）:")
    for n in unavailable:
        print(f"  - {n}")
