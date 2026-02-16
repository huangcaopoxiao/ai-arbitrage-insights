#!/bin/bash
# 曹皇显卡监控修复版 - macOS兼容 👑

cd ~/.openclaw/workspace

# 设置Python脚本超时（使用Python内置机制）
python3 -c "
import subprocess
import signal
import sys

def run_with_timeout(cmd, timeout_sec):
    '''运行命令并设置超时'''
    try:
        # 启动进程
        proc = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待超时
        try:
            stdout, stderr = proc.communicate(timeout=timeout_sec)
            return proc.returncode, stdout, stderr
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            return -1, '', f'命令超时 ({timeout_sec}秒)'
            
    except Exception as e:
        return -1, '', str(e)

# 运行显卡监控脚本
print('🚀 开始执行显卡价格监控...')
returncode, stdout, stderr = run_with_timeout('python3 scripts/gpu_price_monitor.py', 30)

if returncode == 0:
    print('✅ 监控执行成功')
    # 提取JSON输出和消息
    if 'JSON_OUTPUT:' in stdout:
        parts = stdout.split('JSON_OUTPUT:')
        json_part = parts[1].split('TELEGRAM_MESSAGE:')[0].strip()
        message_part = stdout.split('TELEGRAM_MESSAGE:')[1].strip()
        
        print('📊 JSON数据:')
        print(json_part[:500] + '...' if len(json_part) > 500 else json_part)
        
        print('\n📱 Telegram消息:')
        print(message_part)
    else:
        print('⚠️ 输出格式异常')
        print(stdout)
else:
    print('❌ 监控执行失败')
    print('错误信息:', stderr)
    print('输出:', stdout)
" 2>&1