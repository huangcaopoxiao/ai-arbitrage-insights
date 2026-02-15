# 曹皇 - Docker 使用指南 (Colima 版) 👑

## 为什么选择 Colima？

Mac Mini 资源有限，Colima 比 Docker Desktop **轻量 90%**：
- ✅ 内存占用：~500MB vs ~4GB
- ✅ 无 GUI，纯命令行
- ✅ 无需 sudo 密码
- ✅ 完美支持 ARM64 (Apple Silicon)
- ✅ 与 Docker CLI 100% 兼容

---

## 安装步骤

```bash
# 1. 运行曹皇安装脚本
cd ~/.openclaw/workspace
bash scripts/install_docker.sh

# 2. 或者手动安装
brew install colima docker docker-compose
```

---

## 基本操作

### 启动/停止
```bash
colima start              # 启动 (默认 2CPU/4GB内存/20GB磁盘)
colima start --cpu 4 --memory 8   # 自定义资源
colima stop               # 停止
colima status             # 查看状态
```

### Docker 命令 (与标准 Docker 完全一致)
```bash
docker ps                 # 查看运行中容器
docker images             # 查看镜像
docker run hello-world    # 测试
docker run -it ubuntu bash # 运行 Ubuntu
```

### Docker Compose
```bash
docker-compose up -d      # 后台启动
docker-compose down       # 停止
```

---

## 曹皇推荐配置

```bash
# 为 Mac Mini 优化的启动配置
colima start \
  --cpu 2 \
  --memory 4 \
  --disk 20 \
  --arch aarch64 \
  --vm-type vz \
  --mount-type virtiofs
```

---

## 故障排除

### Colima 无法启动
```bash
colima delete    # 删除旧实例
colima start     # 重新创建
```

### Docker 命令报错
```bash
# 确保 Colima 正在运行
colima status

# 如果显示 stopped，先启动
colima start
```

### 权限问题
```bash
# 检查 Docker socket
ls -la ~/.colima/default/docker.sock

# 重新配置
colima stop
colima start
```

---

## 与曹皇项目集成

```bash
# 启动监控系统的容器化版本
cd ~/.openclaw/workspace
docker build -t caohuang-monitor .
docker run -d \
  --name arbitrage-monitor \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  caohuang-monitor
```

---

*零成本基础设施，为盈利而生。* 👑
