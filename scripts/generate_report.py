#!/usr/bin/env python3
"""
曹皇 - 套利报告生成器 (修正版)
修复列名错误: 使用 prompt_price 而非 price_per_token

作者: 曹皇 👑
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path.home() / ".openclaw" / "workspace" / "data" / "arbitrage.db"

def generate_hourly_report():
    """生成小时级报告"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
    
    # 统计过去1小时数据点 (使用正确的列名)
    cursor.execute('''
        SELECT COUNT(*) FROM price_snapshots WHERE timestamp > ?
    ''', (one_hour_ago,))
    snapshot_count = cursor.fetchone()[0]
    
    # 统计套利机会
    cursor.execute('''
        SELECT COUNT(*), AVG(ABS(prompt_diff_pct)) 
        FROM arbitrage_opportunities 
        WHERE timestamp > ?
    ''', (one_hour_ago,))
    opp_stats = cursor.fetchone()
    
    # 获取最佳套利机会 (使用正确的列名)
    cursor.execute('''
        SELECT model_id, or_prompt_price, direct_prompt_price, prompt_diff_pct
        FROM arbitrage_opportunities 
        WHERE timestamp > ?
        ORDER BY ABS(prompt_diff_pct) DESC LIMIT 3
    ''', (one_hour_ago,))
    top_opps = cursor.fetchall()
    
    conn.close()
    
    avg_diff = (opp_stats[1] or 0) * 100
    
    # 构建报告
    report = f"""
👑 **曹皇套利监控小时报告**

**扫描统计**
- 📡 扫描模型数: {snapshot_count} 个
- 💎 套利机会: {opp_stats[0]} 次
- 📊 平均价差: {avg_diff:.1f}%

**🔥 TOP 3 套利信号**
"""
    
    for idx, (model, or_price, direct_price, diff) in enumerate(top_opps, 1):
        direction = "便宜" if diff > 0 else "贵"
        report += f"{idx}. {model.split('/')[-1]}: OpenRouter 比直供{direction} {abs(diff)*100:.0f}%\n"
    
    report += f"""
**⚙️ 系统状态**: ✅ 零成本运行中
**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    return report

if __name__ == "__main__":
    print(generate_hourly_report())
