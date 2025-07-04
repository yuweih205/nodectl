import threading
from .gpu_probe import probe_available_nodes
from .ssh_runner import run_script_remotely
from .state_tracker import mark_node_unavailable
from .manual_blocker import load_manual_block
import random

def schedule_nodes(num_nodes, image_dir=None, image_name=None, run_cmd=None, run_script=None):
    print("🔍 正在探测可用节点（基于 GPU 空闲情况 + 手动屏蔽）...")
    available_nodes = probe_available_nodes()
    manual_blocked = load_manual_block()
    filtered_nodes = [n for n in available_nodes if n not in manual_blocked]

    if num_nodes > len(filtered_nodes):
        print(f"❌ 当前GPU空闲且未屏蔽的节点不足（请求 {num_nodes}，可用 {len(filtered_nodes)}）")
        return

    selected_nodes = filtered_nodes[:num_nodes]
    print(f"🎯 分配节点: {selected_nodes}")

    verbose_node = random.choice(selected_nodes)
    print(f"📺 将实时展示节点 {verbose_node} 的输出\n")

    threads = []
    for node in selected_nodes:
        t = threading.Thread(
            target=run_and_monitor,
            args=(node, image_dir, run_cmd, run_script),
            daemon=True
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("✅ 所有任务启动尝试完成")

def run_and_monitor(node, image_dir, run_cmd=None, run_script=None, verbose=False):
    print(f"[{node}] ⏳ 启动中...")
    success, stdout, stderr = run_script_remotely(node, image_dir, run_cmd, run_script)

    if success:
        print(f"[{node}] ✅ 启动成功")
        if stdout.strip():
            print(f"[{node}] STDOUT:\n{stdout.strip()}")
        if stderr.strip():
            print(f"[{node}] ⚠️ STDERR:\n{stderr.strip()}")
    else:
        print(f"[{node}] ❌ 启动失败")
        if stderr.strip():
            print(f"[{node}] ❌ 错误信息:\n{stderr.strip()}")
        mark_node_unavailable(node)
