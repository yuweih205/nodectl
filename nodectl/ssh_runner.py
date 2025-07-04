import subprocess
import time
import os

def run_ssh_command(node, image_dir, run_cmd=None, run_script=None):
    """
    支持两种方式：
    1. run_cmd：直接远程执行命令
    2. run_script：本地脚本上传后在远程执行
    都支持自动注入 WANDB_API_KEY
    """
    api_key = os.getenv("WANDB_API_KEY")
    wandb_env = f"export WANDB_API_KEY={api_key} && " if api_key else ""

    ssh_cmd = ""

    if run_cmd:
        # 注入 wandb 登录
        full_cmd = f"{wandb_env}{run_cmd}"
        ssh_cmd = (
            f'ssh {node} "cd {image_dir} && nohup {full_cmd} > output.log 2>&1 &"'
        )

    elif run_script:
        remote_script = f"/tmp/remote_script_{int(time.time())}.sh"
        scp_cmd = f"scp {run_script} {node}:{remote_script}"
        try:
            subprocess.check_call(scp_cmd, shell=True)
        except subprocess.CalledProcessError:
            print(f"[ERROR] 上传脚本失败: {node}")
            return False

        # 注入 wandb 登录
        full_cmd = f"{wandb_env}bash {remote_script}"

        ssh_cmd = (
            f'ssh {node} "cd {image_dir} && chmod +x {remote_script} && '
            f'nohup {full_cmd} > output.log 2>&1 &"'
        )

    else:
        raise ValueError("必须指定 run_cmd 或 run_script")

    try:
        subprocess.check_call(ssh_cmd, shell=True)
        return True
    except subprocess.CalledProcessError:
        print(f"[ERROR] 执行远程命令失败: {node}")
        return False
