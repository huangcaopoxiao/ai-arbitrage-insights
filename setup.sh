#!/bin/bash
# 曹皇 - 一键设置脚本 (主人执行) 👑

echo "👑 曹皇 Mac Mini 设置向导"
echo "=========================="
echo ""

# 检查环境
echo "📋 环境检查..."
python3 --version && echo "✅ Python OK"
node --version && echo "✅ Node OK"
git --version && echo "✅ Git OK"
echo ""

# 提示注册
echo "📧 平台注册 (使用邮箱: huangcao.poxiao@gmail.com)"
echo "------------------------------------------------"
echo "请依次访问以下链接完成注册:"
echo ""
echo "1. GitHub   → https://github.com/signup"
echo "   建议用户名: caohuang-ai"
echo "   完成后创建 repo: ai-arbitrage-insights"
echo ""
echo "2. Twitter  → https://twitter.com/i/flow/signup"  
echo "   建议用户名: CaoHuangAI"
echo ""
echo "3. OpenRouter → https://openrouter.ai/"
echo "   注册后创建 API Key"
echo ""
echo "4. DeepSeek → https://platform.deepseek.com/"
echo "   注册后创建 API Key (10元免费额度)"
echo ""

# API Key 存储提示
echo "🔐 API Key 存储"
echo "---------------"
echo "获取 API Key 后，请执行以下命令存入 Keychain:"
echo ""
echo "# OpenRouter"
echo "security add-generic-password -s 'openrouter-api-key' -a caohuang -w 'YOUR_KEY'"
echo ""
echo "# DeepSeek"
echo "security add-generic-password -s 'deepseek-api-key' -a caohuang -w 'YOUR_KEY'"
echo ""
echo "# GitHub Token (Settings > Developer settings > Personal access tokens)"
echo "security add-generic-password -s 'github-token' -a caohuang -w 'YOUR_TOKEN'"
echo ""

# 配置 Git
echo "⚙️ Git 配置"
echo "-----------"
echo "注册 GitHub 后，配置 Git:"
echo ""
echo 'git config --global user.name "Cao Huang"'
echo 'git config --global user.email "huangcao.poxiao@gmail.com"'
echo ""

# GitHub Pages 提示
echo "🌐 GitHub Pages 部署"
echo "-------------------"
echo "1. 在 GitHub 创建 repo: ai-arbitrage-insights"
echo "2. 上传 ~/.openclaw/workspace/docs/index.html"
echo "3. Settings > Pages > Source: Deploy from branch"
echo "4. Branch: main / Folder: /docs"
echo "5. 访问 https://caohuang-ai.github.io/ai-arbitrage-insights"
echo ""

echo "✅ 完成以上步骤后，曹皇将接管后续自动化运营"
echo ""

read -p "按回车键退出..."
