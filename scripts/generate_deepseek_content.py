#!/usr/bin/env python3
"""
曹皇 - DeepSeek 内容生成器
使用 DeepSeek API 生成 Twitter 内容，成本降低 90%

作者: 曹皇 👑
"""

import requests
import subprocess
import json
from datetime import datetime
from pathlib import Path

CONTENT_PATH = Path.home() / ".openclaw" / "workspace" / "content"

def get_deepseek_key():
    result = subprocess.run(
        ['security', 'find-generic-password', '-s', 'deepseek-api-key', '-w'],
        capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None

def generate_with_deepseek(prompt, max_tokens=500):
    """使用 DeepSeek 生成内容"""
    key = get_deepseek_key()
    if not key:
        return None
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers, json=payload, timeout=30
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return None
    except:
        return None

def generate_twitter_content():
    """生成 Twitter 内容"""
    prompt = """你是一个AI行业分析师，写一条关于GPU显卡降价的Twitter推文。
要求：
- 中文
- 带emoji
- 不超过280字符
- 专业但有吸引力
- 包含 #显卡 #降价 #AI 标签

示例内容：监控发现RTX 4090降价8%，现在是入手好时机。"""
    
    return generate_with_deepseek(prompt, max_tokens=200)

def save_content():
    CONTENT_PATH.mkdir(exist_ok=True)
    
    print("🔄 使用 DeepSeek 生成内容...")
    content = generate_twitter_content()
    
    if content:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        filepath = CONTENT_PATH / f"twitter-daily-{timestamp}.txt"
        with open(filepath, "w") as f:
            f.write(content)
        print(f"✅ 已生成: {filepath}")
        print(f"内容:\n{content}")
        return True
    else:
        print("❌ DeepSeek 生成失败")
        return False

if __name__ == "__main__":
    save_content()
