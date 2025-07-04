import threading
from .gpu_probe import probe_available_nodes
from .ssh_runner import run_ssh_command
from .state_tracker import mark_node_unavailable

def schedule_nodes(num_nodes, image_dir, run_cmd):
    print("🔍 正在探测可用节点（基于 GPU 空闲情况）...")
    available_nodes = probe_available_nodes()

    if num_nodes > len(available_nodes):
        print(f"❌ 当前GPU空闲节点不足（请求 {num_nodes}，可用 {len(available_nodes)}）")
        return

    selected_nodes = available_nodes[:num_nodes]
    print(f"🎯 分配节点: {selected_nodes}")

    threads = []
    for node in selected_nodes:
        t = threading.Thread(
            target=run_and_monitor,
            args=(node, image_dir, run_cmd),
            daemon=True
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("✅ 所有任务启动尝试完成")


def run_and_monitor(node, image_dir, run_cmd):
    print(f"[{node}] ⏳ 启动中...")
    ok = run_ssh_command(node, image_dir, run_cmd)
    if ok:
        print(f"[{node}] ✅ 启动成功")
    else:
        print(f"[{node}] ❌ 启动失败，已标记为不可用")
        mark_node_unavailable(node)
