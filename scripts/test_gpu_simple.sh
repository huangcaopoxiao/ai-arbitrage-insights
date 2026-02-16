#!/bin/bash
# 简单显卡监控测试

cd ~/.openclaw/workspace

echo "🚀 开始测试显卡监控..."
echo "当前时间: $(date)"

# 检查数据库
echo "📊 检查数据库..."
sqlite3 data/gpu_prices.db "SELECT COUNT(*) as 总记录数 FROM gpu_prices;"
sqlite3 data/gpu_prices.db "SELECT gpu_name, price, source, timestamp FROM gpu_prices ORDER BY timestamp DESC LIMIT 3;"

echo "✅ 测试完成"