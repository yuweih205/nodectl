import argparse
from .scheduler import schedule_nodes
from .state_tracker import print_available_nodes, print_unavailable_nodes,reset_unavailable_nodes
from .manual_blocker import add_manual_block, remove_manual_block


def main():
    parser = argparse.ArgumentParser(description="H100 节点调度器")
    parser.add_argument("--workdir", type=str, help="训练任务的工作目录")
    parser.add_argument("--image_name", type=str, help="Docker 镜像名称")
    parser.add_argument("--run_cmd", type=str, help="容器内执行的命令")
    parser.add_argument("--query", choices=["available", "unavailable"], help="查询节点状态")
    parser.add_argument("--reset-unavailable", action="store_true", help="重置失败节点状态") 
    parser.add_argument("--clear-manual-unavailable", action="store_true", help="清除所有手动标记的不可用节点")
    parser.add_argument("--mark-unavailable", type=str, help="手动标记节点为不可用")
    parser.add_argument("--unmark", type=str, help="取消手动禁用的节点")
    parser.add_argument('--run_script', help="跳板机上的本地脚本路径，远程复制后执行")

    args = parser.parse_args()

    # 是否执行任务（非查询/非标记/非清除操作）
    is_launch = (
        not args.query
        and not args.mark_unavailable
        and not args.unmark
        and not args.reset_unavailable
        and not args.clear_manual_unavailable
    )

    # 仅在启动任务时要求 run_cmd 或 run_script
    if is_launch:
        if args.run_cmd and args.run_script:
            raise ValueError("只能同时指定 --run_cmd 或 --run_script 中的一个")
        if not args.run_cmd and not args.run_script:
            raise ValueError("必须指定 --run_cmd 或 --run_script")

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

    if not args.num_nodes or not args.image_dir or not args.run_cmd:
        print("❌ 请提供 --num_nodes, --image_dir 和 --run_cmd 参数")
        return
    elif args.workdir and args.image_name and args.run_cmd:
        schedule_nodes(args.workdir, args.image_name, args.run_cmd)

    #schedule_nodes(args.num_nodes, args.image_dir, args.run_cmd)


if __name__ == "__main__":
    main()
