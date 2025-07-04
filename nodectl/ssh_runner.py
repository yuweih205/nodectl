import subprocess
import os
import time

KEY_PATH = "/home/boss/.ssh/h100_cluster.pem"
USER = "boss"

def build_ssh_cmd(base_cmd: str, node: str) -> list:
    """构建带或不带密钥的 ssh/scp 命令前缀"""
    if os.path.exists(KEY_PATH):
        return [base_cmd, "-i", KEY_PATH, f"{USER}@{node}"]
    else:
        return [base_cmd, f"{USER}@{node}"]

def run_script_remotely(node, image_dir, run_cmd=None, run_script=None, verbose=False):
    try:
        run_script = os.path.abspath(run_script) if run_script else None
        image_dir = image_dir or "~"  # ✅ 如果未提供 workdir，则使用 home 目录

        remote_script_path = f"/tmp/remote_script_{int(time.time())}.sh"

        # 上传本地脚本
        if run_script:
            scp_cmd = [
                "scp", "-i", KEY_PATH, run_script,
                f"{USER}@{node}:{remote_script_path}"
            ]
            scp_result = subprocess.run(scp_cmd, capture_output=True, text=True)
            if scp_result.returncode != 0:
                return False, "", f"SCP 失败: {scp_result.stderr}"
            print(f"[{node}] ✅ 脚本已复制完成为 {remote_script_path}")
            
        # 构造远程执行命令
        if run_script:
            remote_cmd = f"cd {image_dir} && chmod +x {remote_script_path} && bash {remote_script_path}"
        elif run_cmd:
            remote_cmd = f"cd {image_dir} && {run_cmd}"
        else:
            return False, "", "必须指定 run_cmd 或 run_script"

        # 执行 SSH 命令
        ssh_cmd = build_ssh_cmd("ssh", node) + [remote_cmd]
        
        if verbose:
            # 实时显示输出
            proc = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                print(f"[{node}] {line}", end="")
            proc.wait()
            return proc.returncode == 0, "", ""
        else:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr

    except Exception as e:
        return False, "", f"异常错误: {str(e)}"
