#!/bin/bash

### QwenPaw 独立管理控制台 CGI（尘墨成风格）
### 功能：查看状态、重置密码、重启服务、查看日志

APP_HOME="/var/apps/com.thalynnx.qwenpaw/target"
APP_VAR="/var/apps/com.thalynnx.qwenpaw/var"
APP_ETC="/var/apps/com.thalynnx.qwenpaw/etc"
PID_FILE="${APP_VAR}/qwenpaw.pid"
LOG_FILE="${APP_VAR}/qwenpaw.log"
SERVICE_PORT="19091"
APP_DIR="com.thalynnx.qwenpaw"
APP_VERSION="2.2.3b1"

find_auth_file() {
    local search_dirs="/var/apps/${APP_DIR}/data /var/data"
    for d in $search_dirs; do
        if [ -d "$d" ]; then
            local found=$(find "$d" -maxdepth 3 -name "auth.json" -path "*.qwenpaw.secret*" 2>/dev/null | head -1)
            if [ -n "$found" ]; then
                echo "$found"
                return 0
            fi
        fi
    done
    find /var /home -maxdepth 4 -name "auth.json" -path "*.qwenpaw.secret*" 2>/dev/null | head -1
}

get_status() {
    if [ -f "$PID_FILE" ]; then
        pid=$(head -n 1 "$PID_FILE" | tr -d '[:space:]')
        if kill -0 "$pid" 2>/dev/null; then
            echo "running"
            return
        fi
    fi
    echo "stopped"
}

get_pid() {
    if [ -f "$PID_FILE" ]; then
        head -n 1 "$PID_FILE" | tr -d '[:space:]'
    fi
}

get_uptime() {
    local pid=$(get_pid)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        local start_time=$(ps -o lstart= -p "$pid" 2>/dev/null)
        if [ -n "$start_time" ]; then
            local start_ts=$(date -d "$start_time" +%s 2>/dev/null)
            local now_ts=$(date +%s)
            local diff=$((now_ts - start_ts))
            local days=$((diff / 86400))
            local hours=$(( (diff % 86400) / 3600 ))
            local mins=$(( (diff % 3600) / 60 ))
            if [ "$days" -gt 0 ]; then
                echo "${days}天 ${hours}:$(printf '%02d' $mins)"
            else
                echo "${hours}:$(printf '%02d' $mins)"
            fi
            return
        fi
    fi
    echo "--:--"
}

do_restart() {
    if [ -f "${APP_HOME}/cmd/main" ]; then
        bash "${APP_HOME}/cmd/main" stop 2>/dev/null
        sleep 2
        bash "${APP_HOME}/cmd/main" start 2>/dev/null
        echo "OK: 服务已重启"
    else
        echo "ERROR: 找不到启动脚本"
        return 1
    fi
}

do_reset_password() {
    local auth_file=$(find_auth_file)
    if [ -z "$auth_file" ]; then
        echo "WARNING: 未找到 auth.json，可能尚未注册"
        return 1
    fi
    rm -f "$auth_file"
    echo "OK: 已删除认证文件"
    do_restart
}

# 处理动作
ACTION="${QUERY_STRING}"
ACTION="${ACTION%%&*}"

echo "Content-Type: text/html; charset=utf-8"
echo ""

# 获取状态
status=$(get_status)
pid=$(get_pid)
uptime=$(get_uptime)
auth_file=$(find_auth_file 2>/dev/null)
if [ -n "$auth_file" ]; then
    auth_status="已启用"
    auth_status_class="ok"
else
    auth_status="未设置"
    auth_status_class="warn"
fi

if [ "$status" = "running" ]; then
    status_text="运行中"
    status_badge="Active"
    status_class="running"
else
    status_text="已停止"
    status_badge="Inactive"
    status_class="stopped"
fi

# 处理动作结果
action_msg=""
if [ "$ACTION" = "reset_password" ]; then
    result=$(do_reset_password 2>&1)
    if echo "$result" | grep -q "^OK:"; then
        action_msg="<div class=\"alert alert-success\">✅ 密码已重置，服务已重启。打开 QwenPaw 后需重新注册。</div>"
    else
        action_msg="<div class=\"alert alert-warning\">⚠️ $result</div>"
    fi
elif [ "$ACTION" = "restart" ]; then
    result=$(do_restart 2>&1)
    if echo "$result" | grep -q "^OK:"; then
        action_msg="<div class=\"alert alert-success\">✅ 服务已重启</div>"
    else
        action_msg="<div class=\"alert alert-error\">❌ $result</div>"
    fi
fi

cat << 'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QwenPaw 控制台</title>
<style>
:root {
  --bg: #f5f7fa;
  --card: #ffffff;
  --border: #e8ecf0;
  --text: #1f2937;
  --text-secondary: #6b7280;
  --primary: #3b82f6;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  min-height: 100vh;
}

/* 布局 */
.layout {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  gap: 20px;
}

/* 左侧导航 */
.sidebar {
  width: 200px;
  flex-shrink: 0;
  background: var(--card);
  border-radius: 12px;
  padding: 16px 0;
  border: 1px solid var(--border);
  height: fit-content;
  position: sticky;
  top: 20px;
}
.sidebar-title {
  padding: 8px 20px 16px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  font-size: 14px;
  color: var(--text);
  text-decoration: none;
  transition: all 0.15s;
  cursor: pointer;
}
.nav-item:hover { background: #f3f4f6; }
.nav-item.active {
  background: #eff6ff;
  color: var(--primary);
  font-weight: 500;
}
.nav-icon {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

/* 主内容 */
.main {
  flex: 1;
  min-width: 0;
}

.page-header {
  margin-bottom: 20px;
}
.page-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}
.page-desc {
  color: var(--text-secondary);
  font-size: 14px;
}

/* 卡片 */
.card {
  background: var(--card);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 20px;
  margin-bottom: 16px;
}

/* 状态卡片 */
.status-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border: 1px solid #bbf7d0;
}
.status-card.stopped {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-color: #fecaca;
}
.status-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.status-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #dcfce7;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.status-card.stopped .status-icon {
  background: #fecaca;
}
.status-info h2 {
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}
.status-badge {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 999px;
  background: #dcfce7;
  color: #166534;
}
.status-card.stopped .status-badge {
  background: #fecaca;
  color: #991b1b;
}
.status-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

/* 按钮 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: opacity 0.15s;
}
.btn:hover { opacity: 0.9; }
.btn-primary { background: var(--primary); color: white; }
.btn-success { background: var(--success); color: white; }
.btn-warning { background: var(--warning); color: white; }
.btn-secondary { background: #f3f4f6; color: var(--text); }

/* 三信息卡片 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.info-item {
  background: var(--card);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 16px 20px;
}
.info-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.info-value {
  font-size: 18px;
  font-weight: 600;
  font-family: "SF Mono", Consolas, monospace;
}

/* 两栏布局 */
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* 操作列表 */
.action-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.action-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: 8px;
  background: #f9fafb;
  border: 1px solid var(--border);
}
.action-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.action-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.action-icon.open { background: #dbeafe; }
.action-icon.restart { background: #fef3c7; }
.action-icon.log { background: #f3f4f6; }
.action-icon.reset { background: #fef3c7; }
.action-title {
  font-size: 14px;
  font-weight: 500;
}
.action-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 服务信息列表 */
.service-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  background: #f9fafb;
  border: 1px solid var(--border);
}
.info-row-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #e0e7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}
.info-row-content {
  flex: 1;
}
.info-row-label {
  font-size: 12px;
  color: var(--text-secondary);
}
.info-row-value {
  font-size: 14px;
  font-weight: 500;
}

/* 提示框 */
.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}
.alert-success { background: #dcfce7; color: #166534; }
.alert-warning { background: #fef3c7; color: #92400e; }
.alert-error { background: #fecaca; color: #991b1b; }

/* 日志区域 */
.log-content {
  background: #1f2937;
  color: #d1d5db;
  padding: 16px;
  border-radius: 8px;
  font-family: "SF Mono", Consolas, monospace;
  font-size: 12px;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 响应式 */
@media (max-width: 768px) {
  .layout { flex-direction: column; }
  .sidebar { width: 100%; position: static; }
  .info-grid { grid-template-columns: 1fr; }
  .two-col { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<div class="layout">

  <!-- 左侧导航 -->
  <div class="sidebar">
    <div class="sidebar-title">QwenPaw 控制台</div>
    <a href="?tab=console" class="nav-item active">
      <span class="nav-icon">🏠</span>
      <span>控制台</span>
    </a>
    <a href="?tab=logs" class="nav-item">
      <span class="nav-icon">📋</span>
      <span>运行日志</span>
    </a>
  </div>

  <!-- 主内容 -->
  <div class="main">
HTMLEOF

# 处理标签页
TAB="${QUERY_STRING}"
TAB="${TAB%%&*}"
TAB="${TAB#tab=}"
if [ -z "$TAB" ]; then
    TAB="console"
fi

if [ "$TAB" = "logs" ]; then
    # 日志页面
    echo '
    <div class="page-header">
      <div class="page-title">运行日志</div>
      <div class="page-desc">查看 QwenPaw 服务的实时运行日志</div>
    </div>
    <div class="card">
      <a href="?" class="btn btn-secondary" style="margin-bottom:16px;">← 返回控制台</a>
      <div class="log-content">'
    if [ -f "$LOG_FILE" ]; then
        tail -50 "$LOG_FILE" 2>/dev/null | sed 's/</\&lt;/g'
    else
        echo "暂无日志文件"
    fi
    echo '
      </div>
    </div>'
else
    # 控制台首页
    echo "
    <div class=\"page-header\">
      <div class=\"page-title\">QwenPaw 控制台</div>
      <div class=\"page-desc\">管理 QwenPaw 服务的运行状态与版本升级</div>
    </div>
    "

    # 动作提示
    if [ -n "$action_msg" ]; then
        echo "$action_msg"
    fi

    # 状态卡片
    echo "
    <div class=\"card status-card ${status_class}\">
      <div class=\"status-left\">
        <div class=\"status-icon\">📈</div>
        <div class=\"status-info\">
          <h2>${status_text} <span class=\"status-badge\">${status_badge}</span></h2>
          <div class=\"status-desc\">QwenPaw 服务${status_text}</div>
        </div>
      </div>
      <a href=\"?restart\" class=\"btn btn-primary\" onclick=\"return confirm('确定要重启服务吗？')\">
        🔄 重启服务
      </a>
    </div>
    "

    # 三信息卡片
    echo "
    <div class=\"info-grid\">
      <div class=\"info-item\">
        <div class=\"info-label\">进程 ID (PID)</div>
        <div class=\"info-value\">${pid:---}</div>
      </div>
      <div class=\"info-item\">
        <div class=\"info-label\">已运行</div>
        <div class=\"info-value\">${uptime}</div>
      </div>
      <div class=\"info-item\">
        <div class=\"info-label\">当前版本</div>
        <div class=\"info-value\">${APP_VERSION}</div>
      </div>
    </div>
    "

    # 两栏布局 - 用双引号让变量展开
    echo "
    <div class=\"two-col\">
      <!-- 常用操作 -->
      <div class=\"card\">
        <h3 style=\"margin-bottom:16px; font-size:16px;\">⚡ 常用操作</h3>
        <div class=\"action-list\">
          <div class=\"action-item\">
            <div class=\"action-left\">
              <div class=\"action-icon open\">🌐</div>
              <div>
                <div class=\"action-title\">打开 QwenPaw</div>
                <div class=\"action-desc\">访问 QwenPaw Web 界面</div>
              </div>
            </div>
            <a href=\"http://NAS:19091\" target=\"_blank\" class=\"btn btn-primary\">打开</a>
          </div>
          <div class=\"action-item\">
            <div class=\"action-left\">
              <div class=\"action-icon restart\">🔄</div>
              <div>
                <div class=\"action-title\">重启服务</div>
                <div class=\"action-desc\">重启 QwenPaw 服务</div>
              </div>
            </div>
            <a href=\"?restart\" class=\"btn btn-warning\" onclick=\"return confirm('确定要重启服务吗？')\">重启</a>
          </div>
          <div class=\"action-item\">
            <div class=\"action-left\">
              <div class=\"action-icon log\">📋</div>
              <div>
                <div class=\"action-title\">查看日志</div>
                <div class=\"action-desc\">查看服务运行日志</div>
              </div>
            </div>
            <a href=\"?tab=logs\" class=\"btn btn-secondary\">查看</a>
          </div>
          <div class=\"action-item\">
            <div class=\"action-left\">
              <div class=\"action-icon reset\">🔑</div>
              <div>
                <div class=\"action-title\">重置密码</div>
                <div class=\"action-desc\">重新设置账号密码</div>
              </div>
            </div>
            <a href=\"?reset_password\" class=\"btn btn-warning\" onclick=\"return confirm('确定要重置密码吗？这会删除当前认证数据，服务将重启。打开 QwenPaw 后需重新注册。')\">重置</a>
          </div>
        </div>
      </div>

      <!-- 服务信息 -->
      <div class=\"card\">
        <h3 style=\"margin-bottom:16px; font-size:16px;\">📊 服务信息</h3>
        <div class=\"service-info\">
          <div class=\"info-row\">
            <div class=\"info-row-icon\">🔌</div>
            <div class=\"info-row-content\">
              <div class=\"info-row-label\">服务端口</div>
              <div class=\"info-row-value\">19091</div>
            </div>
          </div>
          <div class=\"info-row\">
            <div class=\"info-row-icon\">📁</div>
            <div class=\"info-row-content\">
              <div class=\"info-row-label\">工作目录</div>
              <div class=\"info-row-value\">应用文件/${APP_DIR}</div>
            </div>
          </div>
          <div class=\"info-row\">
            <div class=\"info-row-icon\">🔐</div>
            <div class=\"info-row-content\">
              <div class=\"info-row-label\">认证状态</div>
              <div class=\"info-row-value\">${auth_status} 安全</div>
            </div>
          </div>
          <div class=\"info-row\">
            <div class=\"info-row-icon\">📦</div>
            <div class=\"info-row-content\">
              <div class=\"info-row-label\">当前版本</div>
              <div class=\"info-row-value\">${APP_VERSION}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    "
fi

echo '
  </div>
</div>
</body>
</html>
'
