# ssh_config.py

DEFAULT_USER = "boss"
DEFAULT_KEY_PATH = "/home/boss/.ssh/h100_cluster.pem"

# 所有节点使用相同的用户和密钥
SSH_CONFIG = {
    f"abcd{i:02d}": {
        "host": f"abcd{i:02d}",
        "user": DEFAULT_USER,
        "key_path": DEFAULT_KEY_PATH
    } for i in range(1, 51)
}
