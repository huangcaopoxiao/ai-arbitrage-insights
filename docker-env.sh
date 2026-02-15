# 曹皇 - Docker 环境配置 👑
# 添加到 ~/.zshrc 或 ~/.bash_profile

# Colima Docker 环境
export DOCKER_HOST="unix:///Users/caohuang/.colima/default/docker.sock"
export DOCKER_CONTEXT="colima"

# 可选：Docker Compose 兼容性
export COMPOSE_DOCKER_CLI_BUILD=1
