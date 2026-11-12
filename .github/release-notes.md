由 ThalynnX 自动编译发布，覆盖飞牛 fnOS、Docker、通用 Linux、Debian 四类平台。

## 产物说明

| 文件 | 用途 |
| --- | --- |
| `com.thalynnx.qwenpaw-<日期>-x86_64.fpk` | 飞牛 fnOS（x86_64）原生应用 |
| `com.thalynnx.qwenpaw-<日期>-arm64.fpk` | 飞牛 fnOS（ARM64：RK3566、N1 等） |
| `ghcr.io/thalynnx/qwenpaw:<版本>` | Docker 多架构镜像（amd64 / arm64），群晖、威联通、N1 通用 |
| `qwenpaw-<版本>-linux-amd64.tar.gz` / `-arm64.tar.gz` | 通用 Linux：解压后 `sudo bash install.sh` |
| `qwenpaw_<版本>_amd64.deb` / `_arm64.deb` | Debian / Ubuntu / Armbian：`sudo apt install ./*.deb` |

## 安装速查

- 飞牛：应用中心 → 手动安装 → 选对应架构 fpk
- Docker：`docker run -d -p 19091:19091 -v /vol1/qwenpaw:/data ghcr.io/thalynnx/qwenpaw:latest`
- Debian：`sudo apt install ./qwenpaw_<版本>_<架构>.deb`
- 通用：`tar -xzf qwenpaw-<版本>-linux-<架构>.tar.gz && cd qwenpaw-* && sudo bash install.sh`

## 说明

- 数据目录：飞牛在 `@appshare/com.thalynnx.qwenpaw`，其它平台 `/var/lib/qwenpaw/.qwenpaw`，卸载均保留。
- 保留上游 Apache-2.0 许可与版权声明，未做删改。
