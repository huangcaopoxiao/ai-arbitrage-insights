#!/usr/bin/env python3
"""
曹皇 - AI API 套利监控核心
OpenRouter 实时价格差监控系统 v1.0

功能：
- 监控 OpenRouter 各模型实时价格
- 对比直接提供商 vs OpenRouter 价差
- 识别套利机会 (价差 > 阈值时触发)
- 记录到本地 SQLite，生成小时级报告

作者: 曹皇 👑
"""

import requests
import sqlite3
import json
import time
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict
from pathlib import Path

# === 配置区 ===
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/models"
PRICE_DIFF_THRESHOLD = 0.15  # 15% 价差触发记录
DB_PATH = Path.home() / ".openclaw" / "workspace" / "data" / "arbitrage.db"
LOG_PATH = Path.home() / ".openclaw" / "workspace" / "logs" / "arbitrage.log"

# 直接提供商参考价 (USD per 1M tokens) - 需定期更新
DIRECT_PRICING = {
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "claude-3-5-sonnet": {"prompt": 3.00, "completion": 15.00},
    "claude-3-haiku": {"prompt": 0.25, "completion": 1.25},
    "gemini-1.5-pro": {"prompt": 3.50, "completion": 10.50},
    "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    "llama-3.1-405b": {"prompt": 2.80, "completion": 2.80},
    "llama-3.1-70b": {"prompt": 0.90, "completion": 0.90},
    "deepseek-chat": {"prompt": 0.14, "completion": 0.28},
    "deepseek-coder": {"prompt": 0.14, "completion": 0.28},
}

@dataclass
class ModelPrice:
    model_id: str
    name: str
    provider: str
    prompt_price: float  # per 1M tokens
    completion_price: float
    timestamp: datetime

class ArbitrageMonitor:
    def __init__(self):
        self.ensure_dirs()
        self.init_db()
        
    def ensure_dirs(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
    def init_db(self):
        """初始化 SQLite 数据库"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT NOT NULL,
                provider TEXT,
                prompt_price REAL,
                completion_price REAL,
                timestamp TEXT NOT NULL,
                source TEXT DEFAULT 'openrouter'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id TEXT NOT NULL,
                or_prompt_price REAL,
                or_completion_price REAL,
                direct_prompt_price REAL,
                direct_completion_price REAL,
                prompt_diff_pct REAL,
                completion_diff_pct REAL,
                timestamp TEXT NOT NULL,
                acted_upon INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
        
    def log(self, message: str, level: str = "INFO"):
        """写入日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        with open(LOG_PATH, "a") as f:
            f.write(log_line)
        print(log_line.strip())
        
    def fetch_openrouter_prices(self) -> List[ModelPrice]:
        """从 OpenRouter 获取实时价格"""
        try:
            response = requests.get(OPENROUTER_API_URL, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            prices = []
            for model in data.get("data", []):
                model_id = model.get("id", "")
                pricing = model.get("pricing", {})
                
                # 转换价格为 per 1M tokens
                prompt_price = float(pricing.get("prompt", 0)) * 1_000_000
                completion_price = float(pricing.get("completion", 0)) * 1_000_000
                
                mp = ModelPrice(
                    model_id=model_id,
                    name=model.get("name", model_id),
                    provider="openrouter",
                    prompt_price=prompt_price,
                    completion_price=completion_price,
                    timestamp=datetime.now()
                )
                prices.append(mp)
                
            return prices
        except Exception as e:
            self.log(f"获取 OpenRouter 价格失败: {e}", "ERROR")
            return []
            
    def save_prices(self, prices: List[ModelPrice]):
        """保存价格到数据库"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for p in prices:
            cursor.execute('''
                INSERT INTO price_snapshots 
                (model_id, provider, prompt_price, completion_price, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (p.model_id, p.provider, p.prompt_price, p.completion_price, 
                  p.timestamp.isoformat()))
        
        conn.commit()
        conn.close()
        
    def detect_arbitrage(self, prices: List[ModelPrice]) -> List[Dict]:
        """检测套利机会"""
        opportunities = []
        
        for price in prices:
            model_key = None
            # 模糊匹配模型名
            for key in DIRECT_PRICING:
                if key.lower() in price.model_id.lower():
                    model_key = key
                    break
                    
            if not model_key:
                continue
                
            direct = DIRECT_PRICING[model_key]
            
            # 计算价差百分比
            prompt_diff = (direct["prompt"] - price.prompt_price) / direct["prompt"] if direct["prompt"] > 0 else 0
            completion_diff = (direct["completion"] - price.completion_price) / direct["completion"] if direct["completion"] > 0 else 0
            
            # 记录显著价差 (>15%)
            if abs(prompt_diff) > PRICE_DIFF_THRESHOLD or abs(completion_diff) > PRICE_DIFF_THRESHOLD:
                opp = {
                    "model_id": price.model_id,
                    "or_prompt": price.prompt_price,
                    "or_completion": price.completion_price,
                    "direct_prompt": direct["prompt"],
                    "direct_completion": direct["completion"],
                    "prompt_diff_pct": prompt_diff,
                    "completion_diff_pct": completion_diff,
                    "timestamp": price.timestamp
                }
                opportunities.append(opp)
                
                direction = " cheaper" if prompt_diff > 0 else " more expensive"
                self.log(f"套利信号: {price.model_id} - OpenRouter 比直供{direction} {abs(prompt_diff)*100:.1f}%")
                
        return opportunities
        
    def save_opportunities(self, opportunities: List[Dict]):
        """保存套利机会"""
        if not opportunities:
            return
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for opp in opportunities:
            cursor.execute('''
                INSERT INTO arbitrage_opportunities 
                (model_id, or_prompt_price, or_completion_price, direct_prompt_price,
                 direct_completion_price, prompt_diff_pct, completion_diff_pct, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (opp["model_id"], opp["or_prompt"], opp["or_completion"],
                  opp["direct_prompt"], opp["direct_completion"],
                  opp["prompt_diff_pct"], opp["completion_diff_pct"],
                  opp["timestamp"].isoformat()))
        
        conn.commit()
        conn.close()
        
    def get_hourly_report(self) -> str:
        """生成小时级报告"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        
        # 统计过去1小时数据点
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
        
        conn.close()
        
        report = f"""
📊 曹皇套利监控 - 小时报告
时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}
━━━━━━━━━━━━━━━━━━━━━━━━━━
数据点: {snapshot_count} 条
套利机会: {opp_stats[0]} 次
平均价差: {opp_stats[1]*100:.1f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: 🟢 监控中
        """
        return report.strip()
        
    def run_once(self):
        """执行单次监控"""
        self.log("开始扫描 OpenRouter 价格...")
        
        prices = self.fetch_openrouter_prices()
        if prices:
            self.save_prices(prices)
            self.log(f"已获取 {len(prices)} 个模型价格")
            
            opportunities = self.detect_arbitrage(prices)
            if opportunities:
                self.save_opportunities(opportunities)
                self.log(f"发现 {len(opportunities)} 个套利信号")
            else:
                self.log("当前无明显套利机会")
        else:
            self.log("未能获取价格数据", "WARN")
            
    def run_continuous(self, interval_minutes: int = 5):
        """持续运行"""
        self.log(f"曹皇套利监控系统启动 - 每 {interval_minutes} 分钟扫描一次")
        
        while True:
            try:
                self.run_once()
                self.log(f"下次扫描: {interval_minutes} 分钟后")
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                self.log("监控已手动停止", "INFO")
                break
            except Exception as e:
                self.log(f"运行错误: {e}", "ERROR")
                time.sleep(60)  # 错误后等待1分钟重试

if __name__ == "__main__":
    import sys
    
    monitor = ArbitrageMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        print(monitor.get_hourly_report())
    else:
        monitor.run_once()
