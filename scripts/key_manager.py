#!/usr/bin/env python3
"""
曹皇 - API Key 管理器
从 macOS Keychain 安全读取 API Keys

作者: 曹皇 👑
"""

import subprocess
import os
from pathlib import Path

# Keychain 服务名映射
KEY_SERVICES = {
    'openrouter': 'openrouter-api-key',
    'deepseek': 'deepseek-api-key',
    'together': 'together-api-key',
    'github': 'github-token',
}

def get_key(service_name):
    """从 macOS Keychain 获取 API Key"""
    service = KEY_SERVICES.get(service_name, service_name)
    try:
        result = subprocess.run(
            ['security', 'find-generic-password', '-s', service, '-w'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"⚠️ 读取 {service} 失败: {e}")
        return None

def set_key(service_name, api_key):
    """将 API Key 存入 macOS Keychain (主人手动执行)"""
    service = KEY_SERVICES.get(service_name, service_name)
    print(f"请手动执行:\n")
    print(f"security add-generic-password -s '{service}' -a caohuang -w '{api_key}'")

def check_all_keys():
    """检查所有已配置的 API Keys"""
    print("👑 曹皇 API Key 状态检查\n")
    print("-" * 40)
    
    for name, service in KEY_SERVICES.items():
        key = get_key(name)
        status = "✅ 已配置" if key else "❌ 未配置"
        masked = f"{key[:8]}...{key[-4:]}" if key and len(key) > 12 else "N/A"
        print(f"{name:12} {status} {masked if key else ''}")
    
    print("-" * 40)
    
    # 检查环境变量备选
    print("\n环境变量检查:")
    env_vars = ['OPENROUTER_API_KEY', 'DEEPSEEK_API_KEY', 'GITHUB_TOKEN']
    for var in env_vars:
        value = os.getenv(var)
        status = "✅ 已设置" if value else "❌ 未设置"
        print(f"{var:25} {status}")

def load_to_env():
    """将 Keychain 中的 keys 加载到环境变量"""
    keys = {}
    for name in KEY_SERVICES:
        key = get_key(name)
        if key:
            env_name = f"{name.upper()}_API_KEY"
            os.environ[env_name] = key
            keys[name] = True
    return keys

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_all_keys()
    elif len(sys.argv) > 1 and sys.argv[1] == "load":
        keys = load_to_env()
        print(f"已加载 {len(keys)} 个 API Key 到环境变量")
    else:
        check_all_keys()
        print("\n用法:")
        print("  python key_manager.py check  - 检查所有 keys")
        print("  python key_manager.py load   - 加载到环境变量")
