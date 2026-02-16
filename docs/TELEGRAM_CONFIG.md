# Telegram 配置与故障排除指南 👑

## 核心配置

### 1. 正确配置位置
- **配置文件**: `~/.openclaw/openclaw.json`
- **Telegram部分**: `channels.telegram`
- **关键字段**:
  ```json
  "telegram": {
    "enabled": true,
    "dmPolicy": "pairing",
    "botToken": "YOUR_BOT_TOKEN",
    "groupPolicy": "allowlist",
    "streamMode": "partial"
  }
  ```

### 2. 正确 Chat ID 格式
- **个人聊天**: 使用数字ID (如: `8062358314`)
- **群组聊天**: 使用带`-100`前缀的数字ID (如: `-1001234567890`)
- **错误示例**: `"曹皇主人"` (文本ID无效)

### 3. Cron任务配置
```json
"delivery": {
  "mode": "announce",
  "to": "8062358314"  // 正确的数字ID
}
```

## 故障排除

### 问题1: "chat not found"
**症状**: `Telegram send failed: chat not found (chat_id=曹皇主人)`

**原因**: 使用了文本ID而非数字ID

**解决方案**:
1. 获取正确数字ID:
   - 与Bot开始私聊
   - 访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - 查找 `chat.id` 字段

2. 更新所有cron任务:
   ```bash
   # 查看所有任务
   openclaw cron list
   
   # 更新任务配置
   openclaw cron update <jobId> --patch '{"delivery":{"to":"8062358314"}}'
   ```

### 问题2: Bot未启动
**症状**: 消息无法发送，Bot无响应

**解决方案**:
1. 检查Bot状态:
   ```bash
   openclaw status
   ```

2. 重启Bot:
   ```bash
   openclaw gateway restart
   ```

3. 验证Token:
   - 访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe`
   - 应返回Bot信息

### 问题3: 权限问题
**症状**: Bot无法发送消息到群组

**解决方案**:
1. 确保Bot已添加到群组
2. 检查群组权限
3. 使用 `groupPolicy: "allowlist"` 配置

## 预防措施

### 1. 配置验证脚本
创建 `scripts/verify_telegram.sh`:
```bash
#!/bin/bash
echo "验证Telegram配置..."
openclaw status | grep -A2 Telegram
echo "测试消息发送..."
openclaw message --channel telegram --to 8062358314 --message "✅ Telegram配置测试"
```

### 2. 定期健康检查
添加到 `HEARTBEAT.md`:
```markdown
## Telegram健康检查
- [ ] 验证Bot在线状态
- [ ] 测试消息发送
- [ ] 检查cron任务错误计数
```

### 3. 错误监控
监控以下日志:
- `~/.openclaw/logs/telegram.log`
- Cron任务错误计数 (`consecutiveErrors` > 3 时告警)

## 最佳实践

### 1. ID管理
- 将正确Chat ID存储在 `TOOLS.md`:
  ```markdown
  ### Telegram IDs
  - 主人个人ID: 8062358314
  - 项目群组ID: -100xxxxxxxxxx
  ```

### 2. 配置备份
- 定期备份 `openclaw.json`
- 使用版本控制跟踪配置变更

### 3. 自动化测试
每月运行一次完整测试:
```bash
# 测试所有通信通道
./scripts/test_communications.sh
```

## 紧急恢复

### 1. 快速修复步骤
1. 停止所有cron任务
2. 验证Telegram配置
3. 测试消息发送
4. 逐步恢复cron任务

### 2. 回滚方案
如果新配置导致问题:
```bash
# 恢复上次备份
cp ~/.openclaw/openclaw.json.backup ~/.openclaw/openclaw.json
openclaw gateway restart
```

---

**曹皇通讯保障**: Telegram是核心汇报通道，必须100%可靠。任何配置变更需双重验证。👑