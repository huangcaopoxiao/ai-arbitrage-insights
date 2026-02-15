#!/usr/bin/env python3
"""
曹皇 - Twitter/X 自动发布系统 v2.1 👑
使用 Twitter API v1.1 + OAuth 1.0a (完整凭证)

⚠️ 重要警告:
- Twitter 对自动化有严格限制
- 每日推文上限: 50 条 (基础版)
- 重复内容会被标记为垃圾信息
- 建议开启限速模式

作者: 曹皇
"""

import requests
import json
import base64
import hmac
import hashlib
import time
import random
import string
import urllib.parse
from datetime import datetime
from pathlib import Path
import subprocess

# Keychain 服务名
CONSUMER_KEY_SERVICE = 'twitter-consumer-key'
CONSUMER_SECRET_SERVICE = 'twitter-consumer-secret'
ACCESS_TOKEN_SERVICE = 'twitter-access-token'
ACCESS_SECRET_SERVICE = 'twitter-access-secret'

def get_keychain_password(service):
    """从 macOS Keychain 获取密码"""
    try:
        result = subprocess.run(
            ['security', 'find-generic-password', '-s', service, '-w'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except:
        return None

class TwitterBot:
    def __init__(self):
        self.consumer_key = get_keychain_password(CONSUMER_KEY_SERVICE)
        self.consumer_secret = get_keychain_password(CONSUMER_SECRET_SERVICE)
        self.access_token = get_keychain_password(ACCESS_TOKEN_SERVICE)
        self.access_secret = get_keychain_password(ACCESS_SECRET_SERVICE)
        
    def check_credentials(self):
        """检查凭证状态"""
        return {
            'consumer_key': '✅ 已配置' if self.consumer_key else '❌ 未配置',
            'consumer_secret': '✅ 已配置' if self.consumer_secret else '❌ 未配置',
            'access_token': '✅ 已配置' if self.access_token else '❌ 未配置',
            'access_secret': '✅ 已配置' if self.access_secret else '❌ 未配置',
            'ready_to_post': '✅ 可以发帖' if all([self.consumer_key, self.consumer_secret, self.access_token, self.access_secret]) else '❌ 不能发帖'
        }
    
    def generate_oauth_params(self):
        """生成 OAuth 1.0a 参数"""
        return {
            'oauth_consumer_key': self.consumer_key,
            'oauth_nonce': ''.join(random.choices(string.ascii_letters + string.digits, k=42)),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_token': self.access_token,
            'oauth_version': '1.0'
        }
    
    def oauth1_signature(self, method, url, params, consumer_secret, token_secret):
        """生成 OAuth 1.0a 签名"""
        # 按字母顺序排序参数
        sorted_params = sorted(params.items())
        param_string = '&'.join([f"{urllib.parse.quote(str(k), safe='')}={urllib.parse.quote(str(v), safe='')}" for k, v in sorted_params])
        
        # 构建签名基字符串
        base_string = f"{method.upper()}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
        
        # 签名密钥
        signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret or '', safe='')}"
        
        # HMAC-SHA1 签名
        signature = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        return base64.b64encode(signature).decode()
    
    def make_oauth_header(self, method, url, extra_params=None):
        """生成 OAuth 请求头"""
        params = self.generate_oauth_params()
        if extra_params:
            params.update(extra_params)
        
        # 生成签名
        params['oauth_signature'] = self.oauth1_signature(
            method, url, params, self.consumer_secret, self.access_secret
        )
        
        # 构建 Authorization header
        auth_parts = []
        for key in sorted(params.keys()):
            if key.startswith('oauth_'):
                auth_parts.append(f'{urllib.parse.quote(key)}="{urllib.parse.quote(params[key])}"')
        
        return 'OAuth ' + ', '.join(auth_parts)
    
    def verify_credentials(self):
        """验证凭证是否有效"""
        if not all([self.consumer_key, self.consumer_secret, self.access_token, self.access_secret]):
            return {'valid': False, 'error': '凭证不完整'}
        
        url = "https://api.twitter.com/1.1/account/verify_credentials.json"
        headers = {
            'Authorization': self.make_oauth_header('GET', url)
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'valid': True,
                    'username': data.get('screen_name'),
                    'name': data.get('name'),
                    'followers': data.get('followers_count')
                }
            else:
                return {
                    'valid': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def post_tweet(self, text):
        """
        发布推文 (Twitter API v1.1)
        
        Args:
            text: 推文内容 (最多 280 字符)
        
        Returns:
            dict: 发布结果
        """
        if not all([self.consumer_key, self.consumer_secret, self.access_token, self.access_secret]):
            return {
                'success': False,
                'error': 'OAuth 凭证不完整'
            }
        
        # 检查长度
        if len(text) > 280:
            return {
                'success': False,
                'error': f'推文太长 ({len(text)} 字符)，Twitter 限制 280 字符'
            }
        
        url = "https://api.twitter.com/1.1/statuses/update.json"
        
        # 请求参数
        params = {'status': text}
        
        # 生成 OAuth header
        headers = {
            'Authorization': self.make_oauth_header('POST', url, params)
        }
        
        try:
            response = requests.post(url, data=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'tweet_id': data.get('id_str'),
                    'text': data.get('text'),
                    'url': f"https://twitter.com/i/web/status/{data.get('id_str')}",
                    'created_at': data.get('created_at')
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_from_file(self, filepath):
        """从文件读取并发布推文"""
        try:
            with open(filepath, 'r') as f:
                content = f.read().strip()
            
            # 提取第一个适合长度的段落
            lines = content.split('\n')
            tweet_text = []
            current_length = 0
            
            for line in lines:
                if current_length + len(line) + 1 <= 280:
                    tweet_text.append(line)
                    current_length += len(line) + 1
                else:
                    break
            
            final_text = '\n'.join(tweet_text)
            return self.post_tweet(final_text)
        except Exception as e:
            return {'success': False, 'error': str(e)}

def main():
    """主函数 - 测试和验证"""
    bot = TwitterBot()
    
    print("👑 曹皇 Twitter 发布系统 v2.1 (OAuth 1.0a)")
    print("=" * 40)
    
    # 检查凭证
    creds = bot.check_credentials()
    print("\n📋 凭证状态:")
    for key, status in creds.items():
        print(f"  {key}: {status}")
    
    if not all([bot.consumer_key, bot.consumer_secret, bot.access_token, bot.access_secret]):
        print("\n❌ OAuth 凭证不完整")
        return
    
    # 验证凭证
    print("\n🔐 验证凭证...")
    validation = bot.verify_credentials()
    
    if validation.get('valid'):
        print(f"✅ 凭证有效!")
        print(f"   用户名: @{validation.get('username')}")
        print(f"   昵称: {validation.get('name')}")
        print(f"   粉丝: {validation.get('followers')}")
    else:
        print(f"❌ 凭证验证失败: {validation.get('error')}")
        return
    
    print("\n✅ Twitter 自动发布系统就绪!")
    print("\n使用方式:")
    print("  python scripts/twitter_bot.py post    # 发布最新推文")
    print("  python scripts/twitter_bot.py test    # 发布测试推文")

def post_latest():
    """发布最新的推文文件"""
    bot = TwitterBot()
    
    # 查找最新的推文文件
    content_dir = Path.home() / ".openclaw" / "workspace" / "content"
    daily_files = sorted(content_dir.glob("twitter-daily-*.txt"), reverse=True)
    
    if not daily_files:
        print("❌ 没有找到推文文件")
        return
    
    latest = daily_files[0]
    print(f"📝 读取文件: {latest.name}")
    
    with open(latest) as f:
        content = f.read()
    
    print(f"内容:\n{'='*40}")
    print(content)
    print('='*40)
    
    result = bot.post_from_file(latest)
    
    if result.get('success'):
        print(f"\n✅ 发布成功!")
        print(f"   推文链接: {result.get('url')}")
        print(f"   推文ID: {result.get('tweet_id')}")
    else:
        print(f"\n❌ 发布失败: {result.get('error')}")

def post_test():
    """发布测试推文"""
    bot = TwitterBot()
    
    test_text = f"📊 曹皇监控系统测试推文 {datetime.now().strftime('%m/%d %H:%M')}\n\nAI API 套利情报实时更新 👑 #AI #API #省钱"
    
    print(f"📝 发布测试推文:\n{'='*40}")
    print(test_text)
    print('='*40)
    
    result = bot.post_tweet(test_text)
    
    if result.get('success'):
        print(f"\n✅ 发布成功!")
        print(f"   推文链接: {result.get('url')}")
    else:
        print(f"\n❌ 发布失败: {result.get('error')}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "post":
        post_latest()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        post_test()
    else:
        main()
