#!/usr/bin/env python3
"""
曹皇 - 显卡价格监控器 👑
监控 RTX 4090/4080/4070 Ti Super 价格，检测 >=5% 降价
"""

import json
import sqlite3
import re
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

# 数据库路径
DB_PATH = Path.home() / ".openclaw/workspace/data/gpu_prices.db"
DATA_DIR = Path.home() / ".openclaw/workspace/data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 监控的显卡型号
GPU_MODELS = {
    "RTX 4090": {
        "msrp": 1599,
        "keywords": ["RTX 4090", "4090"],
        "targets": [1200, 1300, 1400]  # 关键价格阈值
    },
    "RTX 4080": {
        "msrp": 1199,
        "keywords": ["RTX 4080", "4080"],
        "targets": [850, 950, 1050]
    },
    "RTX 4070 Ti Super": {
        "msrp": 799,
        "keywords": ["RTX 4070 Ti Super", "4070 Ti Super", "4070tis"],
        "targets": [650, 700, 750]
    }
}

# 零售商配置
RETAILERS = {
    "bestbuy": {
        "name": "Best Buy",
        "base_url": "https://www.bestbuy.com",
        "search_urls": {
            "RTX 4090": "/site/searchpage.jsp?st=rtx+4090",
            "RTX 4080": "/site/searchpage.jsp?st=rtx+4080",
            "RTX 4070 Ti Super": "/site/searchpage.jsp?st=rtx+4070+ti+super"
        }
    },
    "newegg": {
        "name": "Newegg",
        "base_url": "https://www.newegg.com",
        "search_urls": {
            "RTX 4090": "/p/pl?d=rtx+4090&N=100006662",
            "RTX 4080": "/p/pl?d=rtx+4080&N=100006662",
            "RTX 4070 Ti Super": "/p/pl?d=rtx+4070+ti+super&N=100006662"
        }
    },
    "amazon": {
        "name": "Amazon",
        "base_url": "https://www.amazon.com",
        "search_urls": {
            "RTX 4090": "/s?k=rtx+4090",
            "RTX 4080": "/s?k=rtx+4080",
            "RTX 4070 Ti Super": "/s?k=rtx+4070+ti+super"
        }
    }
}

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 价格历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gpu_model TEXT NOT NULL,
            retailer TEXT NOT NULL,
            product_name TEXT,
            price REAL,
            currency TEXT DEFAULT 'USD',
            in_stock BOOLEAN,
            url TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 降价警报表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gpu_model TEXT NOT NULL,
            retailer TEXT NOT NULL,
            old_price REAL,
            new_price REAL,
            drop_percent REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_headers():
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

def fetch_url(url):
    """获取URL内容"""
    try:
        req = urllib.request.Request(url, headers=get_headers())
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f"ERROR: {e}"

def extract_prices_from_html(html, retailer):
    """从HTML中提取价格"""
    prices = []
    
    # 通用价格正则模式
    price_patterns = [
        r'\$([\d,]+\.?\d*)',  # $1,299.99
        r'([\d,]+\.?\d*)\s*USD',  # 1299.99 USD
        r'price[\"\']?\s*[:=]\s*[\"\']?\$?([\d,]+\.?\d*)',  # price: 1299.99
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, html)
        for match in matches:
            try:
                price_str = match.replace(',', '')
                price = float(price_str)
                if 100 < price < 5000:  # 合理的显卡价格范围
                    prices.append(price)
            except:
                continue
    
    return prices

def scrape_newegg_prices(gpu_model):
    """抓取Newegg价格"""
    url = RETAILERS["newegg"]["base_url"] + RETAILERS["newegg"]["search_urls"][gpu_model]
    html = fetch_url(url)
    
    if html.startswith("ERROR"):
        return []
    
    prices = []
    
    # Newegg 特定模式
    # 商品块模式
    item_pattern = r'<div class="item-container"[^>]*>(.*?)</div>\s*</div>\s*</div>'
    items = re.findall(item_pattern, html, re.DOTALL)
    
    for item in items[:5]:  # 只取前5个结果
        price_match = re.search(r'<li class="price-current">\s*<strong>(\d+)</strong>\s*<sup>(\d+)</sup>', item)
        title_match = re.search(r'<a[^>]*class="item-title"[^>]*>(.*?)</a>', item, re.DOTALL)
        
        if price_match and title_match:
            try:
                dollars = price_match.group(1)
                cents = price_match.group(2)
                price = float(f"{dollars}.{cents}")
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                
                # 验证是否是目标型号
                keywords = GPU_MODELS[gpu_model]["keywords"]
                if any(kw.lower() in title.lower() for kw in keywords):
                    prices.append({
                        "retailer": "Newegg",
                        "product_name": title[:100],
                        "price": price,
                        "in_stock": "out of stock" not in item.lower() and "sold out" not in item.lower()
                    })
            except:
                continue
    
    return prices

def scrape_bestbuy_prices(gpu_model):
    """抓取Best Buy价格"""
    url = RETAILERS["bestbuy"]["base_url"] + RETAILERS["bestbuy"]["search_urls"][gpu_model]
    html = fetch_url(url)
    
    if html.startswith("ERROR"):
        return []
    
    prices = []
    
    # Best Buy 特定模式
    # 价格模式: $1,299.99
    price_pattern = r'class="sr-price"[^>]*>.*?\$([\d,]+\.\d{2})'
    title_pattern = r'class="sku-title"[^>]*>.*?<a[^>]*>(.*?)</a>'
    
    price_matches = re.findall(price_pattern, html, re.DOTALL)
    title_matches = re.findall(title_pattern, html, re.DOTALL)
    
    for i, (price_str, title_html) in enumerate(zip(price_matches[:5], title_matches[:5])):
        try:
            price = float(price_str.replace(',', ''))
            title = re.sub(r'<[^>]+>', '', title_html).strip()
            
            keywords = GPU_MODELS[gpu_model]["keywords"]
            if any(kw.lower() in title.lower() for kw in keywords):
                prices.append({
                    "retailer": "Best Buy",
                    "product_name": title[:100],
                    "price": price,
                    "in_stock": True  # Best Buy通常只显示有货商品
                })
        except:
            continue
    
    return prices

def get_baseline_price(gpu_model, retailer):
    """获取基准价格（上次记录的价格）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT price FROM price_history 
        WHERE gpu_model = ? AND retailer = ? 
        ORDER BY timestamp DESC LIMIT 1
    ''', (gpu_model, retailer))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def save_price(gpu_model, retailer, product_name, price, in_stock):
    """保存价格记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO price_history (gpu_model, retailer, product_name, price, in_stock)
        VALUES (?, ?, ?, ?, ?)
    ''', (gpu_model, retailer, product_name, price, in_stock))
    
    conn.commit()
    conn.close()

def save_alert(gpu_model, retailer, old_price, new_price, drop_percent):
    """保存降价警报"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO price_alerts (gpu_model, retailer, old_price, new_price, drop_percent)
        VALUES (?, ?, ?, ?, ?)
    ''', (gpu_model, retailer, old_price, new_price, drop_percent))
    
    conn.commit()
    conn.close()

def check_price_drops(gpu_model, retailer, new_price):
    """检查是否降价 >= 5%"""
    baseline = get_baseline_price(gpu_model, retailer)
    
    if baseline is None:
        return None  # 首次运行，无基准价格
    
    if new_price < baseline:
        drop_percent = ((baseline - new_price) / baseline) * 100
        if drop_percent >= 5:
            return {
                "old_price": baseline,
                "new_price": new_price,
                "drop_percent": round(drop_percent, 2)
            }
    
    return None

def monitor_gpu_prices():
    """主监控函数"""
    init_db()
    
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "alerts": [],
        "new_baselines": [],
        "all_prices": []
    }
    
    print(f"👑 曹皇显卡监控启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    for gpu_model in GPU_MODELS.keys():
        print(f"\n🔍 监控 {gpu_model}...")
        
        # 抓取各零售商价格
        all_retailer_prices = []
        
        # Newegg
        try:
            newegg_prices = scrape_newegg_prices(gpu_model)
            all_retailer_prices.extend(newegg_prices)
            print(f"  Newegg: 找到 {len(newegg_prices)} 个商品")
        except Exception as e:
            print(f"  Newegg: 抓取失败 - {e}")
        
        # Best Buy
        try:
            bestbuy_prices = scrape_bestbuy_prices(gpu_model)
            all_retailer_prices.extend(bestbuy_prices)
            print(f"  Best Buy: 找到 {len(bestbuy_prices)} 个商品")
        except Exception as e:
            print(f"  Best Buy: 抓取失败 - {e}")
        
        # 处理价格数据
        for item in all_retailer_prices:
            retailer = item["retailer"]
            price = item["price"]
            product_name = item["product_name"]
            in_stock = item["in_stock"]
            
            # 保存价格记录
            save_price(gpu_model, retailer, product_name, price, in_stock)
            
            results["all_prices"].append({
                "gpu_model": gpu_model,
                "retailer": retailer,
                "product_name": product_name,
                "price": price,
                "in_stock": in_stock
            })
            
            # 检查降价
            price_drop = check_price_drops(gpu_model, retailer, price)
            
            if price_drop:
                alert = {
                    "gpu_model": gpu_model,
                    "retailer": retailer,
                    "product_name": product_name,
                    "old_price": price_drop["old_price"],
                    "new_price": price_drop["new_price"],
                    "drop_percent": price_drop["drop_percent"],
                    "in_stock": in_stock
                }
                results["alerts"].append(alert)
                save_alert(gpu_model, retailer, price_drop["old_price"], price_drop["new_price"], price_drop["drop_percent"])
                print(f"  🚨 降价警报: {retailer} ${price_drop['old_price']:.2f} → ${price_drop['new_price']:.2f} (-{price_drop['drop_percent']}%)")
            else:
                baseline = get_baseline_price(gpu_model, retailer)
                if baseline is None:
                    results["new_baselines"].append({
                        "gpu_model": gpu_model,
                        "retailer": retailer,
                        "price": price
                    })
                    print(f"  📊 建立基准: {retailer} ${price:.2f}")
                else:
                    change = ((price - baseline) / baseline) * 100
                    change_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                    print(f"  {change_emoji} {retailer}: ${price:.2f} (基准: ${baseline:.2f}, {'+' if change > 0 else ''}{change:.1f}%)")
    
    print("\n" + "-" * 60)
    print(f"✅ 监控完成 - 发现 {len(results['alerts'])} 个降价警报")
    
    return results

def format_alert_message(results):
    """格式化警报消息"""
    if not results["alerts"]:
        # 无降价警报时，返回当前价格摘要
        msg = "👑 **曹皇显卡价格监控报告**\n\n"
        msg += f"⏰ 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} EST\n"
        msg += "📊 状态: 暂无 >=5% 降价\n\n"
        
        # 按型号分组显示当前最低价
        current_prices = {}
        for item in results["all_prices"]:
            gpu = item["gpu_model"]
            if gpu not in current_prices or item["price"] < current_prices[gpu]["price"]:
                current_prices[gpu] = item
        
        msg += "**当前最低价:**\n"
        for gpu, item in current_prices.items():
            msrp = GPU_MODELS[gpu]["msrp"]
            vs_msrp = ((msrp - item["price"]) / msrp) * 100
            stock_emoji = "🟢" if item["in_stock"] else "🔴"
            msg += f"• {gpu}: ${item['price']:.0f} @ {item['retailer']} ({'低于' if vs_msrp > 0 else '高于'}MSRP {abs(vs_msrp):.0f}%) {stock_emoji}\n"
        
        return msg
    
    # 有降价警报
    msg = "🚨 **曹皇显卡降价警报** 🚨\n\n"
    msg += f"⏰ 发现时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} EST\n\n"
    
    for alert in results["alerts"]:
        stock_status = "🟢 有货" if alert["in_stock"] else "🔴 缺货"
        msg += f"**{alert['gpu_model']}** @ {alert['retailer']}\n"
        msg += f"💰 ${alert['old_price']:.2f} → **${alert['new_price']:.2f}**\n"
        msg += f"📉 降幅: **-{alert['drop_percent']}%**\n"
        msg += f"🏷️ {alert['product_name'][:50]}...\n"
        msg += f"📦 {stock_status}\n\n"
    
    msg += "⚡ 建议: 降价超过5%，值得关注!"
    return msg

if __name__ == "__main__":
    results = monitor_gpu_prices()
    
    # 输出JSON结果
    print("\n" + "=" * 60)
    print("JSON_OUTPUT:")
    print(json.dumps(results, indent=2, default=str))
    
    # 输出格式化消息
    print("\n" + "=" * 60)
    print("TELEGRAM_MESSAGE:")
    print(format_alert_message(results))
