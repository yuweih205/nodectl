# nodectl: H100 节点调度工具（支持 GPU 状态感知）

一个运行在跳板机上的智能调度器，支持 GPU 状态探测 + SSH 启动训练任务。

---

## 🔧 安装

```bash
pip install .
```

---

## 🚀 使用方法

### 启动训练任务（自动探测GPU空闲节点）

```bash
nodectl \
  --num_nodes 4 \
  --workdir /mnt/train/qwen \
  --run_cmd "bash run.sh"
```

### 查询当前GPU空闲节点

```bash
nodectl --query available
```

### 查询 SSH 启动失败的节点（会被标记为不可用）

```bash
nodectl --query unavailable
```

---

## 📁 文件结构

```
nodectl/
├── main.py             # CLI 主入口
├── scheduler.py        # 调度逻辑，基于 GPU 空闲情况筛选节点
├── ssh_runner.py       # paramiko SSH 启动容器任务
├── gpu_probe.py        # 异步 nvidia-smi 查询空闲节点
├── ssh_config.py       # 集中管理 SSH 用户/密钥信息
├── state_tracker.py    # 标记 SSH 启动失败节点
├── config.py           # 节点名配置（abcd01-50）
├── __init__.py
```

---

## ✅ 特性

- ✅ 支持 SSH 统一密钥连接
- ✅ 自动探测 GPU 空闲状态（基于 `nvidia-smi`）
- ✅ 失败节点标记 + 可查询
- ✅ CLI 接口清晰、友好

---

## 🧪 测试

```bash
python3 -m unittest discover tests/
```

---

## 📌 TODO

- [ ] 支持 GPU 利用率策略配置（如允许 2 卡空闲也可用）
- [ ] SQLite 持久记录任务状态
- [ ] 多用户标签 / 使用组隔离
- [ ] Web UI 面板可视化调度日志

## 如果提示找不到node.json
export NODECTL_CONFIG=/xxxx/path/to/nodes.json

## 🧙‍♀️ wandb 自动登录支持
请先在跳板机执行
export WANDB_API_KEY=你的WandB密钥

⚠️ 使用限制与注意事项
本工具适用于如下场景：
- 用户较少（推荐 ≤5 人）；
- 大多数用户通过统一 CLI 脚本启动任务；
- 启动任务前会扫描 GPU 利用率；
- 节点管理权限集中在跳板机。

❌ 不适用于：
- 多用户频繁并发提交任务；
- 需要资源锁、抢占、配额管理的情况；
- 大型训练调度（建议使用 Ray、Slurm、Kube 等平台）；


