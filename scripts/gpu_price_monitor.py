#!/usr/bin/env python3
"""
曹皇 - 显卡价格监控系统 v1.0 👑
监控 RTX 4090/4080/4070 Ti Super 价格，降价即通知

数据源:
- Amazon US
- Newegg
- Best Buy (API)

作者: 曹皇
"""

import requests
import sqlite3
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass

# 配置
DB_PATH = Path.home() / ".openclaw" / "workspace" / "data" / "gpu_prices.db"
ALERT_THRESHOLD = 0.05  # 5%降价触发通知
MONITOR_INTERVAL = 30  # 30分钟

# 监控目标
GPU_TARGETS = [
    {
        "name": "RTX 4090",
        "amazon_url": "https://www.amazon.com/s?k=nvidia+rtx+4090",
        "newegg_url": "https://www.newegg.com/p/pl?d=rtx+4090",
        "target_price": 1600,  # USD
    },
    {
        "name": "RTX 4080 Super", 
        "amazon_url": "https://www.amazon.com/s?k=nvidia+rtx+4080+super",
        "newegg_url": "https://www.newegg.com/p/pl?d=rtx+4080+super",
        "target_price": 1000,
    },
    {
        "name": "RTX 4070 Ti Super",
        "amazon_url": "https://www.amazon.com/s?k=nvidia+rtx+4070+ti+super", 
        "newegg_url": "https://www.newegg.com/p/pl?d=rtx+4070+ti+super",
        "target_price": 800,
    }
]

@dataclass
class PriceData:
    gpu_name: str
    source: str
    price: float
    currency: str
    timestamp: datetime
    url: str
    in_stock: bool

class GPUPriceMonitor:
    def __init__(self):
        self.init_db()
        
    def init_db(self):
        """初始化数据库"""
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gpu_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gpu_name TEXT NOT NULL,
                source TEXT NOT NULL,
                price REAL,
                currency TEXT DEFAULT 'USD',
                in_stock INTEGER DEFAULT 1,
                url TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gpu_name TEXT NOT NULL,
                old_price REAL,
                new_price REAL,
                drop_percent REAL,
                source TEXT,
                timestamp TEXT NOT NULL,
                notified INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def fetch_amazon_price(self, gpu_name, url):
        """抓取 Amazon 价格 (简化版，实际需要反爬处理)"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            # 注意：实际抓取需要更复杂的反爬处理
            # 这里先用模拟数据演示逻辑
            return None
        except Exception as e:
            print(f"Amazon抓取失败: {e}")
            return None
    
    def fetch_newegg_price(self, gpu_name, url):
        """抓取 Newegg 价格"""
        try:
            # 简化版实现
            return None
        except Exception as e:
            print(f"Newegg抓取失败: {e}")
            return None
    
    def add_manual_price(self, gpu_name, source, price, url=""):
        """手动添加价格记录（用于测试）"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO gpu_prices (gpu_name, source, price, url, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (gpu_name, source, price, url, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        print(f"✅ 记录价格: {gpu_name} @ {source} = ${price}")
    
    def check_price_drops(self):
        """检查价格下降"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        alerts = []
        
        for gpu in GPU_TARGETS:
            # 获取最近两次价格记录
            cursor.execute('''
                SELECT price, source, timestamp FROM gpu_prices 
                WHERE gpu_name = ? 
                ORDER BY timestamp DESC LIMIT 2
            ''', (gpu['name'],))
            
            rows = cursor.fetchall()
            if len(rows) >= 2:
                new_price, source, new_time = rows[0]
                old_price, _, old_time = rows[1]
                
                if old_price > 0:
                    drop_percent = (old_price - new_price) / old_price
                    
                    if drop_percent >= ALERT_THRESHOLD:
                        alert = {
                            'gpu_name': gpu['name'],
                            'old_price': old_price,
                            'new_price': new_price,
                            'drop_percent': drop_percent * 100,
                            'source': source,
                            'timestamp': datetime.now()
                        }
                        alerts.append(alert)
                        
                        # 保存alert
                        cursor.execute('''
                            INSERT INTO price_alerts 
                            (gpu_name, old_price, new_price, drop_percent, source, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (gpu['name'], old_price, new_price, drop_percent, source, 
                              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return alerts
    
    def generate_alert_message(self, alerts):
        """生成告警消息"""
        if not alerts:
            return None
        
        msg = f"🔥 **曹皇显卡降价警报** ({datetime.now().strftime('%m/%d %H:%M')})\n\n"
        
        for alert in alerts:
            msg += f"💎 **{alert['gpu_name']}**\n"
            msg += f"   💰 ${alert['old_price']:.0f} → ${alert['new_price']:.0f}\n"
            msg += f"   📉 降价 {alert['drop_percent']:.1f}%\n"
            msg += f"   🏪 {alert['source']}\n\n"
        
        msg += "⚡ 限时优惠，手慢无！\n"
        msg += "📊 更多监控: https://huangcaopoxiao.github.io/ai-arbitrage-insights/\n"
        msg += "👑 曹皇监控"
        
        return msg
    
    def run(self):
        """主运行循环"""
        print("👑 曹皇显卡监控系统启动")
        print(f"监控目标: {len(GPU_TARGETS)} 款显卡")
        print(f"降价阈值: {ALERT_THRESHOLD*100}%")
        print("-" * 40)
        
        # 模拟初始数据（实际运行时从网页抓取）
        # 这里添加测试数据演示逻辑
        
        alerts = self.check_price_drops()
        if alerts:
            msg = self.generate_alert_message(alerts)
            print(msg)
            return msg
        else:
            print("📊 暂无降价信号")
            return None

if __name__ == "__main__":
    import sys
    
    monitor = GPUPriceMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 添加测试数据模拟降价
        monitor.add_manual_price("RTX 4090", "Amazon", 1800)
        monitor.add_manual_price("RTX 4090", "Amazon", 1650)  # 降价8.3%
        monitor.run()
    else:
        monitor.run()
