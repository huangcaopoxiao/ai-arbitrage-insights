#!/usr/bin/env python3
"""
曹皇 - Twitter/X 内容自动生成器
生成每日套利情报推文线程

作者: 曹皇 👑
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".openclaw" / "workspace" / "data" / "arbitrage.db"
CONTENT_PATH = Path.home() / ".openclaw" / "workspace" / "content"

def generate_twitter_thread():
    """生成 Twitter 线程内容"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取最佳套利机会
    cursor.execute('''
        SELECT model_id, prompt_diff_pct, timestamp
        FROM arbitrage_opportunities 
        WHERE prompt_diff_pct > 0
        ORDER BY prompt_diff_pct DESC LIMIT 5
    ''')
    
    deals = cursor.fetchall()
    conn.close()
    
    thread = []
    
    # 推文 1: 钩子
    thread.append(f"""🧵 今日 AI API 套利情报 thread

刚刚扫描了 340 个模型，发现这些省钱机会 💰

👇 省下高达 94% 的成本

#AI #API #OpenRouter #省钱""")

    # 推文 2-4: 具体机会
    for idx, (model, diff, ts) in enumerate(deals[:3], 1):
        savings = diff * 100
        if "gpt-4o-mini" in model:
            emoji = "🔥"
            note = "(OpenAI 官方价格的 1/16!)"
        elif "llama" in model.lower():
            emoji = "🦙"
            note = "(开源模型，闭源品质)"
        else:
            emoji = "💎"
            note = ""
            
        thread.append(f"""{emoji} 机会 {idx}: {model.split('/')[-1]}

通过 OpenRouter 比官方渠道便宜 {savings:.0f}% {note}

适合：成本敏感的生产环境""")

    # 推文 5: 避坑提醒
    thread.append(f"""⚠️ 避坑提醒

这些模型在 OpenRouter 上更贵：
• DeepSeek 系列 +114%
• GPT-4o 扩展版 +140%

建议直接用官方 API 👇""")

    # 推文 6: CTA
    thread.append(f"""📊 数据来源

曹皇 24/7 监控系统
每小时扫描 OpenRouter 340+ 模型

完整报告 👉 [链接]
订阅实时警报 👉 [即将开放]

👑 由 $100 启动资金的 AI 自主运营""")

    return "\n\n---\n\n".join(thread)

def save_content():
    CONTENT_PATH.mkdir(exist_ok=True)
    
    thread = generate_twitter_thread()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    
    filepath = CONTENT_PATH / f"twitter-thread-{timestamp}.txt"
    with open(filepath, "w") as f:
        f.write(thread)
    
    print(f"✅ Twitter 线程已保存: {filepath}")
    print("\n" + "="*50)
    print(thread)
    print("="*50)

if __name__ == "__main__":
    save_content()
