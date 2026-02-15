# 曹皇 - 套利监控系统容器化配置 👑
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY scripts/ ./scripts/
COPY data/ ./data/

# 创建日志目录
RUN mkdir -p logs

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV DOCKER_ENV=true

# 默认命令：运行监控
CMD ["python", "scripts/openrouter_arbitrage.py"]
