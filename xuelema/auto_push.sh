#!/bin/bash
#
# 学了吗APP - 自动检查推送脚本
# 
# 使用方法：
#   chmod +x auto_push.sh
#   ./auto_push.sh
#
# 或添加到cron定时任务：
#   */5 * * * * cd /path/to/xuelema && ./auto_push.sh
#

# 配置
REPO_DIR="/d/xueliao/xuelema"
LOG_FILE="/tmp/auto_push.log"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================"
log "🚀 学了吗APP 自动检查推送"
log "========================================"

# 切换到仓库目录
cd "$REPO_DIR" || {
    log "${RED}❌ 无法切换到仓库目录: $REPO_DIR"
    exit 1
}

log "📁 当前目录: $(pwd)"

# 检查是否有未提交的修改
if git diff --quiet && git diff --cached --quiet; then
    log "✅ 代码是最新的，无需推送"
    exit 0
fi

log "📝 发现未提交的修改"

# 显示修改的文件
log "修改的文件:"
git status --short

# 自动添加所有修改
log "📦 添加修改..."
git add -A

# 检查是否有实际修改
if git diff --cached --name-only | grep -q .; then
    # 生成提交信息
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
    COMMIT_MSG="auto: update at ${TIMESTAMP}"
    
    # 提交
    log "📝 提交: $COMMIT_MSG"
    git commit -m "$COMMIT_MSG"
    
    # 推送
    log "📤 推送到GitHub..."
    if git push origin master 2>&1 | tee -a "$LOG_FILE"; then
        log "${GREEN}✅ 推送成功！"
        
        # 触发GitHub Actions
        if [ -n "$GITHUB_TOKEN" ]; then
            log "🔄 触发GitHub Actions..."
            curl -X POST \
                -H "Authorization: token $GITHUB_TOKEN" \
                -H "Accept: application/vnd.github.v3+json" \
                "https://api.github.com/repos/hjyhjony-glitch/xuelema/actions/workflows/windows.yml/dispatches" \
                -d '{"ref":"master"}' 2>/dev/null
            
            log "✅ GitHub Actions已触发"
        fi
        
        exit 0
    else
        log "${RED}❌ 推送失败"
        exit 1
    fi
else
    log "⚠️ 没有实际修改"
    exit 0
fi
