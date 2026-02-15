#!/bin/bash
# 曹皇 - GitHub 自动推送脚本 👑
# 每小时自动推送最新报告到 GitHub Pages

cd "$(dirname "$0")/.."

# 加载 GitHub Token 到 URL
GITHUB_TOKEN=$(security find-generic-password -s github-token -w 2>/dev/null)
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GitHub Token 未配置"
    exit 1
fi

# 确保 remote 配置正确
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/huangcaopoxiao/ai-arbitrage-insights.git"

# 检查是否有变更
if [ -z "$(git status --porcelain)" ]; then
    echo "📭 无新内容需要推送"
    exit 0
fi

# 提交并推送
git add -A
git commit -m "曹皇自动更新: $(date '+%Y-%m-%d %H:%M') | 新报告生成"
git push origin main

echo "✅ 已推送至 GitHub Pages: https://huangcaopoxiao.github.io/ai-arbitrage-insights/"
