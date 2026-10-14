#!/usr/bin/env bash
# ============================================================
# trigger-sync.sh — 通过 GitHub API 触发 blog 同步 workflow
#
# 用途：NAS 上的 cron 定时调用，是 GitHub Actions cron 的保底渠道。
#
# 配置：
#   1. 存放 PAT（权限必须 600）：
#      mkdir -p ~/.config
#      echo "github_pat_xxx" > ~/.config/blog-sync-token
#      chmod 600 ~/.config/blog-sync-token
#
#   2. 加到 crontab（NAS 用户名替换）：
#      3,33 8-19 * * * /home/<用户名>/blog/scripts/trigger-sync.sh >> /tmp/blog-sync.log 2>&1
# ============================================================

set -euo pipefail

TOKEN_FILE="${HOME}/.config/blog-sync-token"
REPO="darcyjoven/blog"
WORKFLOW="sync.yml"
API="https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}/dispatches"

# --- 前置检查 ---
if [[ ! -f "$TOKEN_FILE" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 错误：找不到 $TOKEN_FILE"
    exit 1
fi

# 权限过宽则提醒（不影响运行）
PERM=$(stat -c '%a' "$TOKEN_FILE" 2>/dev/null || echo "未知")
if [[ "$PERM" != "600" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 警告：$TOKEN_FILE 权限是 $PERM，建议改成 600"
fi

TOKEN=$(tr -d '\n\r ' < "$TOKEN_FILE")
if [[ -z "$TOKEN" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 错误：$TOKEN_FILE 是空的"
    exit 1
fi

# --- 触发 workflow ---
# 用 env -u 清掉代理：NAS 上如果设了全局代理，
# 请求会走代理导致超时或失败。
HTTP_CODE=$(env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
    curl -sS -o /tmp/blog-sync-resp.txt -w '%{http_code}' \
    --max-time 30 \
    -X POST "$API" \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -H "Content-Type: application/json" \
    -d '{"ref":"main"}' 2>&1) || HTTP_CODE="000"

TS=$(date '+%Y-%m-%d %H:%M:%S')

case "$HTTP_CODE" in
    204)
        echo "[$TS] ✓ 已触发 sync workflow"
        ;;
    401|403)
        echo "[$TS] ✗ 认证失败（$HTTP_CODE）：PAT 无效、过期或权限不足"
        cat /tmp/blog-sync-resp.txt 2>/dev/null | head -3
        exit 1
        ;;
    404)
        echo "[$TS] ✗ 找不到 workflow（$HTTP_CODE）：检查 $REPO 和 $WORKFLOW"
        exit 1
        ;;
    422)
        echo "[$TS] ✗ 参数错误（$HTTP_CODE）：body 必须是 {\"ref\":\"main\"}"
        cat /tmp/blog-sync-resp.txt 2>/dev/null | head -3
        exit 1
        ;;
    000)
        echo "[$TS] ✗ 网络错误：无法连接 GitHub（检查 NAS 外网连通性）"
        exit 1
        ;;
    *)
        echo "[$TS] ? 意外响应（$HTTP_CODE）"
        cat /tmp/blog-sync-resp.txt 2>/dev/null | head -3
        ;;
esac

# 注：即使每次都触发，sync.yml 里没有变更时会跳过提交，
# 所以频繁调用无害。只有 Notion 内容变了才会 commit + 部署。