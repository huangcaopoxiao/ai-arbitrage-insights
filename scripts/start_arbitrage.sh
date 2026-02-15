#!/bin/bash
# 曹皇 - 套利监控系统启动脚本 👑

cd "$(dirname "$0")/.."
source venv/bin/activate

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 启动监控 (每 10 分钟扫描)
python scripts/openrouter_arbitrage.py >> logs/arbitrage_daemon.log 2>&1 &
echo $! > .arbitrage.pid

echo "曹皇套利监控系统已启动 (PID: $(cat .arbitrage.pid))"
