#!/bin/bash

### QwenPaw 信息页静态文件服务（CGI）
### 支持 /console.cgi 管理控制台路由

BASE_PATH="/var/apps/com.thalynnx.qwenpaw/target/www"

URI_NO_QUERY="${REQUEST_URI%%\?*}"

# 如果请求 console.cgi，转发到管理控制台 CGI
if echo "$URI_NO_QUERY" | grep -q "console.cgi"; then
    exec /var/apps/com.thalynnx.qwenpaw/target/ui/console.cgi
fi

REL_PATH="/"
case "$URI_NO_QUERY" in
    *index.cgi*)
        REL_PATH="${URI_NO_QUERY#*index.cgi}"
        ;;
esac

if [ -z "$REL_PATH" ] || [ "$REL_PATH" = "/" ]; then
    REL_PATH="/index.html"
fi

TARGET_FILE="${BASE_PATH}${REL_PATH}"

if echo "$TARGET_FILE" | grep -q '\.\.'; then
    echo "Status: 400 Bad Request"
    echo "Content-Type: text/plain; charset=utf-8"
    echo ""
    echo "Bad Request"
    exit 0
fi

if [ ! -f "$TARGET_FILE" ]; then
    echo "Status: 404 Not Found"
    echo "Content-Type: text/plain; charset=utf-8"
    echo ""
    echo "404 Not Found: ${REL_PATH}"
    exit 0
fi

ext="${TARGET_FILE##*.}"
case "$ext" in
    html|htm) mime="text/html; charset=utf-8" ;;
    css)     mime="text/css; charset=utf-8" ;;
    js)      mime="application/javascript; charset=utf-8" ;;
    jpg|jpeg) mime="image/jpeg" ;;
    png)     mime="image/png" ;;
    gif)     mime="image/gif" ;;
    svg)     mime="image/svg+xml" ;;
    txt|log) mime="text/plain; charset=utf-8" ;;
    *)       mime="application/octet-stream" ;;
esac

echo "Content-Type: $mime"
echo ""
cat "$TARGET_FILE"
