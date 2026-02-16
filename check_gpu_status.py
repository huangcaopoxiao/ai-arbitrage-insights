#!/usr/bin/env python3
import sqlite3
import sys

def check_gpu_status():
    try:
        conn = sqlite3.connect('gpu_prices.db')
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        print('📊 数据库表:', tables)
        
        # 检查gpu_prices表
        cursor.execute('SELECT COUNT(*) FROM gpu_prices')
        total_count = cursor.fetchone()[0]
        print(f'📈 总记录数: {total_count}')
        
        # 获取最新价格
        cursor.execute('SELECT model, price, source, timestamp FROM gpu_prices ORDER BY timestamp DESC LIMIT 10')
        latest = cursor.fetchall()
        print('🆕 最新10条记录:')
        for row in latest:
            print(f'  {row[0]} | ${row[1]:.2f} | {row[2]} | {row[3]}')
        
        # 按型号统计
        cursor.execute('SELECT model, COUNT(*) as count, MIN(price) as min_price, MAX(price) as max_price, AVG(price) as avg_price FROM gpu_prices GROUP BY model ORDER BY count DESC')
        models = cursor.fetchall()
        print('📋 按型号统计:')
        for row in models:
            print(f'  {row[0]}: {row[1]}条记录, 价格范围 ${row[2]:.2f}-${row[3]:.2f}, 平均 ${row[4]:.2f}')
        
        # 检查警报状态
        cursor.execute('SELECT model, price, source, timestamp FROM gpu_prices WHERE price < 1700 AND model LIKE "%4090%" ORDER BY price ASC LIMIT 5')
        alerts = cursor.fetchall()
        print('🚨 潜在低价警报 (RTX 4090 < $1700):')
        if alerts:
            for row in alerts:
                print(f'  ⚠️ {row[0]} | ${row[1]:.2f} | {row[2]} | {row[3]}')
        else:
            print('  ✅ 暂无低价警报')
        
        conn.close()
        return True
        
    except Exception as e:
        print(f'❌ 数据库检查失败: {e}')
        return False

if __name__ == '__main__':
    check_gpu_status()