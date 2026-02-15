#!/bin/bash
# 曹皇 - Phase 1 自动化内容发布系统 👑
# 每小时自动生成报告和社交媒体内容

cd "$(dirname "$0")/.."
source venv/bin/activate

echo "🚀 曹皇 Phase 1 内容生产线启动..."
echo "时间: $(date)"

# 1. 运行套利监控
echo "📊 扫描 OpenRouter 价格..."
python scripts/openrouter_arbitrage.py

# 2. 生成报告
echo "📝 生成情报报告..."
REPORT_NUM=$(ls -1 reports/report-*.md 2>/dev/null | wc -l | tr -d ' ')
REPORT_NUM=$((REPORT_NUM + 1))
python3 << EOF > reports/report-$(printf "%03d" $REPORT_NUM).md
import sqlite3
from datetime import datetime
conn = sqlite3.connect('data/arbitrage.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM price_snapshots WHERE timestamp > datetime("now", "-1 hour")')
count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM arbitrage_opportunities WHERE timestamp > datetime("now", "-1 hour")')
opps = cursor.fetchone()[0]
print(f"# 曹皇情报报告 #{REPORT_NUM:03d}")
print(f"**时间:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"**数据点:** {count} 条 | **套利机会:** {opps} 次")
print("\n---\n")
print("*曹皇自主生成* 👑")
conn.close()
EOF

# 3. 生成 Twitter 内容
echo "🐦 生成 Twitter 线程..."
python scripts/generate_twitter.py

# 4. 更新网站时间戳
sed -i '' "s/最后更新：.*$/最后更新：$(date '+%Y-%m-%d %H:%M EST')/" docs/index.html

echo "✅ Phase 1 内容生产完成"
echo "报告: reports/report-$(printf "%03d" $REPORT_NUM).md"
echo "Twitter: content/twitter-thread-*.txt"
