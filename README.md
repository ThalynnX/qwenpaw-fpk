# QwenPaw FPK for 飞牛 fnOS (RK3566 / ARM)

用 **ThalynnX/qwenpaw** 仓库源码构建的飞牛 fnOS 原生应用安装包，适配 **RK3566 (ARM)** 设备。

## 特性

- 原生 fpk 应用包（非 Docker），安装时自动完成：拉取源码 → 创建 Python venv → 安装依赖 → 生成默认配置
- 元信息全部为用户本人：维护者 / 发布者 / 仓库地址均为 `ThalynnX`
- 支持飞牛应用中心桌面入口（QwenPaw 控制台，端口 8088）
- 安装向导可选 PyPI 镜像源（阿里云 / 清华 / 官方）与日志级别
- GitHub Actions 自动打包，tag 触发自动发布 Release

## 目录结构

```
qwenpaw-fpk/
├── manifest                  # 应用元信息（appname/version/platform/维护者等）
├── config/
│   ├── privilege             # 运行权限（package 用户）
│   └── resource              # 数据共享声明
├── cmd/                      # 飞牛生命周期脚本
│   ├── main                  # start / stop / status
│   ├── install_callback      # 安装：拉源码 + venv + pip install + init
│   └── ...                   # install_init / upgrade_* / uninstall_* / config_*
├── app/
│   ├── fnos-common.sh        # 公共路径解析库
│   └── ui/                   # 桌面入口（config + images）
├── wizard/install            # 安装向导（PyPI 源 + 日志级别）
├── ICON.PNG / ICON_256.PNG   # 应用图标
├── LICENSE                   # Apache-2.0
└── qwenpaw.fpk               # 已打包产物（也可由 Actions 重建）
```

## 本地打包

依赖：`fnpack`（飞牛官方打包工具，见 <https://developer.fnnas.com/docs/cli/fnpack/>）。

```bash
# 下载 fnpack（Linux x86）
curl -sL https://static2.fnnas.com/fnpack/fnpack-1.2.3-linux-amd64 -o /usr/local/bin/fnpack
chmod +x /usr/local/bin/fnpack

# 打包
cd qwenpaw-fpk
fnpack build
# 产物：qwenpaw.fpk
```

## 安装到飞牛

1. 飞牛应用中心 → 手动安装 → 上传 `qwenpaw.fpk`
2. 安装向导选择 pip 源（默认阿里云）与日志级别
3. 等待安装完成（依赖较多，耗时较长属正常）
4. 应用中心打开 QwenPaw → 控制台 `http://localhost:8088/`

**前置要求**：飞牛系统需自带 Python 3.11~3.13 与 git（安装脚本自动检测并提示）。

## 自动打包（GitHub Actions）

- `push` 到 `main` 且改动涉及 manifest/cmd/wizard/config/app/图标 时自动构建
- 打 `v*` 标签（如 `v2.2.3b1`）时自动构建并发布到 Release
- 也可在 Actions 页手动 `Run workflow`

## 说明

- 本应用安装时从 <https://github.com/ThalynnX/qwenpaw> 拉取源码并安装，代码与依赖更新跟随该仓库
- 版权归 QwenPaw 原项目所有（Apache-2.0），本仓库仅做飞牛 fpk 打包工程托管

## License

Apache License 2.0
