#!/bin/bash
# 部署支付页面到GitHub Pages

set -e

echo "🚀 开始部署曹皇盈利系统支付页面到GitHub Pages"

# 检查GitHub CLI是否安装
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI未安装，请先安装: brew install gh"
    exit 1
fi

# 检查是否已登录GitHub
if ! gh auth status &> /dev/null; then
    echo "❌ 未登录GitHub，请先登录: gh auth login"
    exit 1
fi

# 创建支付页面目录
echo "📁 创建支付页面目录..."
mkdir -p payment_page
cp payment_page.html payment_page/index.html

# 创建配置文件
cat > payment_page/config.json << EOF
{
    "payment_system": "曹皇盈利系统",
    "version": "2.0.0",
    "deploy_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "api_endpoint": "https://api.caohuang.ai",
    "stripe_publishable_key": "pk_live_6Jl8aCtCq5NveJmoN4liQMnh00TlXhlHWs",
    "products": [
        {
            "key": "gpu_monitor",
            "name": "显卡监控SaaS订阅",
            "price": 500,
            "currency": "cad",
            "interval": "month"
        },
        {
            "key": "ai_arbitrage_report",
            "name": "AI套利深度报告",
            "price": 1000,
            "currency": "cad",
            "interval": "one_time"
        },
        {
            "key": "code_bounty_service",
            "name": "代码赏金服务",
            "price": 1000,
            "currency": "cad",
            "interval": "month"
        }
    ]
}
EOF

# 创建README
cat > payment_page/README.md << 'EOF'
# 曹皇盈利系统支付页面

## 概述
这是曹皇盈利系统的支付页面，支持Stripe Checkout支付。

## 功能
- 产品展示和选择
- Stripe安全支付集成
- 响应式设计
- 支付成功处理

## 部署状态
- **部署时间**: $(date)
- **API端点**: https://api.caohuang.ai
- **GitHub Pages**: https://huangcaopoxiao.github.io/ai-arbitrage-insights/payment/

## 产品列表
1. **显卡监控SaaS订阅** - $5 CAD/月
2. **AI套利深度报告** - $10 CAD
3. **代码赏金服务** - $10 CAD/月

## 技术栈
- HTML5/CSS3/JavaScript
- Bootstrap 5
- Stripe Checkout
- GitHub Pages

## 安全说明
- 使用Stripe Restricted Key，无法提现退款
- 单笔交易限额$10，每日限额$100
- 仅支持加拿大和美国客户
EOF

# 检查Git仓库状态
echo "📊 检查Git仓库状态..."
cd /Users/caohuang/.openclaw/workspace

if [ ! -d ".git" ]; then
    echo "❌ 当前目录不是Git仓库"
    exit 1
fi

# 添加支付页面到Git
echo "📝 添加支付页面到Git..."
git add payment_page/
git add payment_page.html
git add deploy_payment_page.sh

# 提交更改
echo "💾 提交更改..."
git commit -m "🚀 部署曹皇盈利系统支付页面 v2.0.0

- 添加支付页面HTML文件
- 集成Stripe Checkout支付
- 支持3个盈利产品
- 响应式设计适配移动端
- 添加部署脚本和文档

部署时间: $(date)
API端点: https://api.caohuang.ai
安全限制: 单笔$10，每日$100，无法提现" || {
    echo "⚠️ 提交失败，可能没有更改"
}

# 推送到GitHub
echo "📤 推送到GitHub..."
git push origin main

# 检查GitHub Pages状态
echo "🌐 检查GitHub Pages状态..."
gh repo view --web

echo ""
echo "✅ 部署完成！"
echo ""
echo "📋 部署摘要:"
echo "   - 支付页面: payment_page/index.html"
echo "   - 配置文件: payment_page/config.json"
echo "   - 访问地址: https://huangcaopoxiao.github.io/ai-arbitrage-insights/payment/"
echo "   - API端点: https://api.caohuang.ai"
echo "   - 安全限制: 单笔$10，每日$100，无法提现"
echo ""
echo "🎯 下一步:"
echo "   1. 访问支付页面测试支付流程"
echo "   2. 向现有用户推广订阅服务"
echo "   3. 监控支付状态和用户增长"
echo ""
echo "👑 曹皇盈利系统支付页面已部署完成！"