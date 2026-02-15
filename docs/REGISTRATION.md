# 曹皇 - 平台账户注册指南 👑

## 邮箱信息 (主人已提供)
- **邮箱:** huangcao.poxiao@gmail.com
- **密码:** [主人持有，曹皇不存储]

---

## 待注册平台清单

### 1. OpenRouter (最高优先级)
- **用途:** API 套利核心通道
- **免费额度:** 有限免费请求
- **注册地址:** https://openrouter.ai/
- **步骤:**
  1. 点击 "Sign Up"
  2. 使用邮箱: caohuang.poxiao@gmail.com
  3. 验证邮箱
  4. 进入 Dashboard 创建 API Key
  5. 将 Key 保存在 macOS Keychain
- **Cost:** $0

### 2. DeepSeek Platform (高优先级)
- **用途:** DeepSeek 模型直供，OpenRouter 溢价114%
- **免费额度:** 10元 RMB 免费额度
- **注册地址:** https://platform.deepseek.com/
- **步骤:**
  1. 邮箱注册
  2. 手机验证 (需主人协助)
  3. 创建 API Key
- **Cost:** $0

### 3. Together AI (中优先级)
- **用途:** Llama 模型备用通道
- **免费额度:** $5
- **注册地址:** https://www.together.ai/
- **Cost:** $0

### 4. GitHub (Phase 1 必需)
- **用途:** 代码托管 + GitHub Pages 站点
- **注册地址:** https://github.com/signup
- **步骤:**
  1. 用户名建议: caohuang-ai 或 caohuang-arbitrage
  2. 使用邮箱注册
  3. 验证邮箱
  4. 创建 repo: ai-arbitrage-insights
  5. 启用 GitHub Pages (Settings > Pages)
- **Cost:** $0

### 5. Twitter/X (Phase 1 必需)
- **用途:** 内容发布，吸引订阅
- **注册地址:** https://twitter.com/i/flow/signup
- **用户名建议:** CaoHuangAI 或 AIArbitrageIntel
- **Cost:** $0

---

## 注册后配置清单

完成注册后，主人需执行：

```bash
# 1. 将 API Keys 存入 macOS Keychain
security add-generic-password -s "openrouter-api-key" -a caohuang -w "YOUR_KEY_HERE"
security add-generic-password -s "deepseek-api-key" -a caohuang -w "YOUR_KEY_HERE"

# 2. 配置 GitHub Pages
# 在 GitHub repo 设置中启用 Pages，指向 main branch / docs folder

# 3. 曹皇读取 Keychain
cd ~/.openclaw/workspace && source venv/bin/activate
python3 << 'EOF'
import subprocess
def get_key(service):
    result = subprocess.run(
        ['security', 'find-generic-password', '-s', service, '-w'],
        capture_output=True, text=True
    )
    return result.stdout.strip()

openrouter_key = get_key('openrouter-api-key')
deepseek_key = get_key('deepseek-api-key')
print(f"OpenRouter Key loaded: {'Yes' if openrouter_key else 'No'}")
print(f"DeepSeek Key loaded: {'Yes' if deepseek_key else 'No'}")
EOF
```

---

## 曹皇建议注册顺序

1. **GitHub** → 部署 Pages 站点 (立即有展示窗口)
2. **Twitter/X** → 开始发布内容 (吸引流量)
3. **OpenRouter** → 获取免费 API Key (验证套利)
4. **DeepSeek** → 获取直供通道 (高溢价模型)
5. **Together AI** → 备用选项

---

*所有账户密码建议统一使用主人提供的密码格式，便于记忆。*

👑
