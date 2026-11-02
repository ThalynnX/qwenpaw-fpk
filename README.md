# QwenPaw fpk 自动打包工程（com.thalynnx.qwenpaw）

将 [ThalynnX/qwenpaw](https://github.com/ThalynnX/qwenpaw) 源码自动编译为飞牛 fnOS 原生应用安装包 `com.thalynnx.qwenpaw.fpk`，并上传到 GitHub Release 下载页。

## 成品特征（对齐商店成品版）

- **打包完整源码**：安装时无需联网拉源码，从本地 `app.tgz` 内的 `qwenpaw/code` 源码建虚拟环境并安装依赖。
- **依赖飞牛应用商店运行时**：`install_dep_apps = nodejs_v24:python312`，安装时自动安装 Node.js v24 与 Python 3.12。
- **4 步安装向导**：欢迎说明 → 安装注意事项 → PyPI 源选择 → 日志级别。
- **双桌面入口**：Web 控制台（http://NAS:19091）+ 应用信息页（CGI）。
- **生命周期完整**：启动/停止/状态、安装、配置、升级、卸载回调齐全。

## 目录结构

```
├── manifest                 # 应用元信息（version/checksum 由 CI 自动更新）
├── cmd/                     # 生命周期脚本（main / install / config / upgrade / uninstall）
├── config/                  # privilege + resource
├── wizard/                  # install / config / uninstall / upgrade 向导
├── app/
│   ├── config/              # 打包进 app.tgz 的应用配置
│   ├── qwenpaw/code/        # 【CI 生成】QwenPaw 源码（克隆自 ThalynnX/qwenpaw）
│   ├── ui/                  # 桌面 UI 入口（config / index.cgi / images）
│   └── www/                 # 应用信息页
├── ICON.PNG / ICON_256.PNG
└── LICENSE                  # Apache-2.0
```

## 自动编译

GitHub Actions 工作流 `.github/workflows/build-fpk.yml` 在以下时机触发：

1. **每日 03:00 UTC**（北京时间 11:00）定时拉取 ThalynnX/qwenpaw 最新源码自动编译；
2. **手动触发**（Actions → Build QwenPaw FPK → Run workflow）；
3. **推送本仓库 main 分支**（manifest / cmd / wizard / config / app 等变更）。

每次构建流程：

1. 克隆 `ThalynnX/qwenpaw` 最新源码 → `app/qwenpaw/code`；
2. 读取源码 `__version__` 更新 manifest 的 `version`；
3. 打包 `app.tgz`（源码 + ui + www）；
4. 用 fnpack 生成 `com.thalynnx.qwenpaw.fpk`；
5. 上传构建产物到 GitHub Actions artifact，并创建/更新 `v<版本>` Release 供下载。

## 本地构建

```bash
git clone --depth 1 https://github.com/ThalynnX/qwenpaw.git app/qwenpaw/code
rm -rf app/qwenpaw/code/.git
tar -czf app.tgz -C app .
curl -sL https://static2.fnnas.com/fnpack/fnpack-1.2.3-linux-amd64 -o fnpack && chmod +x fnpack
./fnpack build
# 输出：com.thalynnx.qwenpaw.fpk
```

## 版本

- 应用标识：`com.thalynnx.qwenpaw`（独立应用，不影响社区包）
- 版本号：随 ThalynnX/qwenpaw 源码 `__version__` 自动更新
- 发布者：ThalynnX
