import argparse
from .scheduler import schedule_nodes
from .state_tracker import (
    print_available_nodes, print_unavailable_nodes, reset_unavailable_nodes
)
from .manual_blocker import add_manual_block, remove_manual_block

def main():
    parser = argparse.ArgumentParser(description="H100 节点调度器")
    parser.add_argument("--num-nodes", "-n", type=int, help="要使用的节点数量")
    parser.add_argument("--workdir", type=str, help="训练任务的工作目录")
    parser.add_argument("--image_name", type=str, help="Docker 镜像名称")
    parser.add_argument("--run_cmd", type=str, help="容器内执行的命令")
    parser.add_argument("--run_script", help="跳板机上的本地脚本路径，远程复制后执行")
    parser.add_argument("--query", choices=["available", "unavailable"], help="查询节点状态")
    parser.add_argument("--reset-unavailable", action="store_true", help="重置失败节点状态") 
    parser.add_argument("--clear-manual-unavailable", action="store_true", help="清除所有手动标记的不可用节点")
    parser.add_argument("--mark-unavailable", type=str, help="手动标记节点为不可用")
    parser.add_argument("--unmark", type=str, help="取消手动禁用的节点")

    args = parser.parse_args()

    # 优先处理状态类指令
    if args.mark_unavailable:
        add_manual_block(args.mark_unavailable)
        print(f"✅ 节点 {args.mark_unavailable} 已手动标记为不可用")
        return

    if args.unmark:
        remove_manual_block(args.unmark)
        print(f"✅ 节点 {args.unmark} 已从手动不可用列表移除")
        return

    if args.query:
        if args.query == "available":
            print_available_nodes()
        else:
            print_unavailable_nodes()
        return

    if args.reset_unavailable:
        reset_unavailable_nodes()
        print("🔁 已重置所有失败节点状态")
        return

    if args.clear_manual_unavailable:
        from .manual_blocker import save_manual_block
        save_manual_block(set())
        print("🧹 已清除所有手动标记的不可用节点")
        return

    if args.run_cmd:
        if not args.workdir or not args.image_name:
            print("❌ 使用 --run_cmd 时，必须同时指定 --workdir 和 --image_name")
            return
        print(f"🚀 准备调度 {args.num_nodes} 台节点执行命令")
        schedule_nodes(
            num_nodes=args.num_nodes,
            image_dir=args.workdir,
            image_name=args.image_name,
            run_cmd=args.run_cmd,
            run_script=None,
        )
    elif args.run_script:
        print(f"🚀 准备调度 {args.num_nodes} 台节点执行脚本")
        schedule_nodes(
            num_nodes=args.num_nodes,
            image_dir=None,
            image_name=None,
            run_cmd=None,
            run_script=args.run_script,
        )
    else:
        print("❌ 参数不完整。必须至少指定 --run_cmd 或 --run_script 之一")
        return


if __name__ == "__main__":
    main()
