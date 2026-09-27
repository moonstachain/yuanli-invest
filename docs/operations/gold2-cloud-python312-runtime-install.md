# GOLD2：既有优宽宿主的独立 Python 3.12 运行时

2026-09-26 已在既有优宽宿主安装固定 Python 3.12.14，并完成真实子进程纯核心验收。专属目录收紧、短 alias 创建和临时 relay 关闭也已完成。**优宽原生策略仍以 Python 3.9.2 启动，正式执行运行时仍阻塞。**本轮没有启用交易策略、接入新交易所或执行账户／订单操作；生产 `requires-python >=3.12` 与 `main()` 硬门保留。

## 最终实测状态

| 项目 | 实际结果 | 本地仓外回执 |
|---|---|---|
| 固定运行时安装 | 12:55:10 完整包大小／SHA通过；3.12.14 标准库 smoke PASS | [python-r3-install-success.json](../../../outputs/gold2-connectivity-implementation-20260926/python-r3-install-success.json) |
| 新树目录权限 | 13:07:38 仅 r3 `python/` 0777→0700，`HARDENED` | [python312-root-harden-receipt.json](../../../outputs/gold2-connectivity-implementation-20260926/python312-root-harden-receipt.json) |
| 专属短 alias | 13:08:06 `ALIAS_READY`，精确指向固定 r3 dated binary | [python312-alias-ready-receipt.json](../../../outputs/gold2-connectivity-implementation-20260926/python312-alias-ready-receipt.json) |
| 原生解释器选择 | 长／短 `#!`、新建无交易所机器人均仍是 `/usr/bin/python3` 3.9.2 | [长路径](../../../outputs/gold2-connectivity-implementation-20260926/python312-core-long-shebang-blocked.json)、[新机器人](../../../outputs/gold2-connectivity-implementation-20260926/python312-fresh-robot-long-shebang-blocked.json)、[短路径](../../../outputs/gold2-connectivity-implementation-20260926/python312-alias-launch-receipt.json) |
| 子进程纯核心 | 13:13:30 实际 PASS：outer 3.9.2、inner 3.12.14，七项纯核心检查通过；`native_api_connected=false` | [python312-subprocess-core-actual-pass.json](../../../outputs/gold2-connectivity-implementation-20260926/python312-subprocess-core-actual-pass.json) |
| 临时 relay 撤销 | 已重新部署禁用；旧 token 实际请求 HTTP 410 | [python-package-relay-disabled.json](../../../outputs/gold2-connectivity-implementation-20260926/python-package-relay-disabled.json) |

子进程成功的证据范围严格为 `SUBPROCESS_PURE_CORE_ONLY_NOT_NATIVE_API`。实际结果 `SUBPROCESS_PURE_CORE_PASS_NOT_NATIVE_API` 中 `runtime_supplied=false`、账户访问为 false、broker／order 调用均为 0。它证明该主机能执行 3.12 纯核心，不能称为优宽原生 API 接通、正式运行时验收或 SimNow 交易验证。

## 现场事实与可信发行源

2026-09-26 只读探针得到：Linux、x86_64、glibc 2.31，默认 Python 3.9.2；九个固定绝对解释器路径都不存在。当前策略进程 effective UID 为 0，这是平台既有运行方式，因此本方案不是“非 root 安装”。不使用 sudo、不切换用户、不安装系统包、不改系统 Python 或 PATH，所有写入限定为新专属树。

优宽官方支持策略第一行指定已安装解释器的绝对路径；其文档没有保证当前租用宿主预装 Python 3.12。[优宽 Python 指南](https://www.youquant.com/user-guide/%E7%BC%96%E7%A8%8B%E8%AF%AD%E8%A8%80/python)

采用 Astral 自有 `python-build-standalone` 的固定发行版本，不把它称为 Python.org 发布的官方 Linux 二进制。Astral 官方说明 uv 使用这一发行源；该源码发行的运行文档要求普通 GNU Linux 目标 glibc ≥2.17，当前宿主 2.31 符合最低条件。最终兼容性仍由解释器实际启动、标准库检查与优宽回调读回确认。[Astral 的发行源说明](https://docs.astral.sh/uv/concepts/python-versions/#cpython-distributions)、[固定发行提交的运行文档](https://github.com/astral-sh/python-build-standalone/blob/6a729962cddc76630b59b1b895501b1539412524/docs/running.md)

| 项目 | 固定值 |
|---|---|
| Python / release tag | 3.12.14 / 20260924 |
| 平台 | baseline x86_64-unknown-linux-gnu |
| 包 | cpython-3.12.14+20260924-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz |
| 大小 | 34,270,188 字节 |
| SHA256 | 269b2c99e4db15b242bf01832f4fea1e8f1a664f273cff519393f296e9820b41 |
| GitHub asset / release ID | 586643551 / 395990880 |
| 专属根目录 | /opt/yuanli-gold2-runtime |
| 首轮候选解释器 | /opt/yuanli-gold2-runtime/cpython-3.12.14-20260924-x86_64/python/bin/python3.12 |

固定发行的 GitHub API `immutable=true`，提供了与上述下载大小、SHA256 一致的 asset digest。[固定发行](https://github.com/astral-sh/python-build-standalone/releases/tag/20260924)、[该版本 API 元数据](https://api.github.com/repos/astral-sh/python-build-standalone/releases/tags/20260924)

## 历史首轮方案与执行顺序

1. `scripts/youquant_python_host_readonly.py`：只读探针，不列目录、不读环境变量、不写文件。固定九条系统解释器路径使用隔离子进程，单次最多 3 秒。
2. `scripts/youquant_python_runtime_install.py`：整文件部署至不绑定交易所的专用工具策略，保持 `INSTALL_MODE = "DRY_RUN"`；先读回固定机器、UID、glibc、`/opt` 父目录可写性及新目标不存在。默认不下载、不写文件。
3. 在经过审核的部署副本中，只把唯一模式常量改为 `INSTALL_MODE = "EXECUTE"`。源码中的专属目录、机器、UID、固定包与哈希均保留。只允许一个执行实例；目标已存在即拒绝，不覆盖旧树。
4. 执行成功回执必须显示 `INSTALLED_NOT_PRODUCTION_ENABLED`、SHA／大小吻合、标准库 `PASS`、版本 `[3,12,14]`；回执同时保存在新树 `install-receipt.json`。
5. 原计划另用无交易所工具策略，以 `#!` 绝对路径验证原生启动。本机实际未采纳该选择，长路径／短 alias／新机器人都仍用 3.9.2，已如最终状态表保存失败结果。安装器 smoke 和子进程纯核心 PASS 不能替代优宽原生回调或交易端连接审核。
6. 正式策略启用须独立经过现有准入、连接／账户／委托读取等门槛。解释器安装本身不授予任何委托权限。

优先使用已通过 metadata dry-run 的 `/opt` 专属目录。备选固定 `/tmp/yuanli-gold2-runtime-uid-0` 只可在新的审核副本中选择；此位置可能随宿主重启或清理消失，不适合静默替换持久运行路径。平台每次创建的 `/tmp/fmz-py-*` 临时工作目录不可作安装根。

## 边界与验证

下载只接受 HTTPS 及固定 GitHub／发行 CDN 域名，不读取代理环境；每次读取有 15 秒超时，总下载期限 120 秒。严格验证固定包的精确大小与 SHA256 后才解压，不从 `latest` 选择版本，不执行下载脚本，不调用 shell。

解压用手工受限写入：最多 30,000 个成员、512 MiB 总普通文件、128 MiB 单文件；只允许 `python/` 子树，拒绝绝对路径、穿越、硬链接、特殊文件、重复路径、链接祖先、链接目标穿越、缺失目标与循环。合法 terminfo 内部相对别名被保留；普通文件写入先于链接创建。所有目标文件独占创建，权限不继承 owner/setuid。失败目录保留，停止启用，不自动删目录或重试。

原安装器 26 项离线测试在 Python 3.12.14 与 bootstrap Python 3.9.6 上均通过。实际固定包已在本地校验大小／SHA，并通过加强成员校验：4,534 个成员、1,049 个内部链接、98,394,214 字节普通文件；dated 解释器是普通可执行文件。本地 Mac 大小写不敏感卷的完整展开因 terminfo 大小写同名碰撞停止，未运行 Linux 二进制；本地验证本身不能证明 Linux 启动；后来 r3 真实云安装和子进程验收回执已补足解释器／纯核心证据，原生启动仍失败。

测试命令：

```sh
.venv/bin/python -m unittest tests.test_youquant_python_runtime_tools -q
/usr/bin/python3 -m unittest tests.test_youquant_python_runtime_tools -q
```

本轮没有改正式策略、数据 worker、账户、系统解释器，也没有创建新付费主机。

## 2026-09-26 有界网络恢复记录与 r3 实际安装

首轮安装的云端回执为 `DOWNLOAD_DEADLINE_EXCEEDED`，原目标只保留 2,490,368 字节普通 partial 文件、无 receipt、无展开目录。该文件权限 0666 是旧下载在 `open("xb")` 后尚未到达完成时 `chmod(0600)` 的结果；父目录仍是 UID 0／0700。恢复方案只接受这个经过现场审查的精确大小、权限、owner、nlink=1 组合，不能把任意可写文件纳入允许集。

r2 使用同一个官方公开包的八条 HTTPS Range 连接。实际回执 `PARALLEL_INCOMPLETE_PARTS_RETAINED`，manifest 没有完整分片，只有一条连接收到 196,608 字节；旧目标和新失败树均保留。只读 manifest 工具仅打开固定新树内一个 ≤16 KiB 文件，并输出白名单错误类别、序号和字节数；Python 3.9 的标准 `socket.timeout` 类名 `timeout` 单独列入允许集，不将任意异常文本或 URL 外传。

r3 安装工具 `scripts/youquant_python_runtime_recover_relay.py` 使用用户现有项目的一个临时 HTTPS 端点转送同一公开包，包内容的信任仍由原固定 SHA 决定。端点固定为 `https://tbmoimbdhsrltvospwpu.supabase.co/functions/v1/gold2-runtime-package-20260926`，禁止任何重定向；不读取 Supabase 数据、账户或环境变量。仓库源码的 `RELAY_TOKEN` 为空，默认仍为 `DRY_RUN`。短命 header 值只注入权限 0600 的私有执行副本，不进仓库、日志、plan 或 receipt。

r3 独立新目标为 `/opt/yuanli-gold2-runtime/cpython-3.12.14-20260924-x86_64-recovery-20260926-r3`。仅复制原已审查 partial 为新私有种子，不复用 r2 未完成分片。八段不交叠的 Range 须逐段满足 206、精确 Content-Range、总长与分段长度；网络 IO 超时 30 秒，总下载界限 600 秒。若端点声明 `X-Gold2-Package-Sha256`，必须与原固定哈希一致。顺序合并后仍须完整大小和 SHA256 全部通过，才复用原严格解包和隔离 smoke。

安装与恢复有 58 项离线测试，加上 alias 6 项、未来显式父目录解包 2 项，共 66 项相关测试在 Python 3.12.14 与 3.9.6 都通过。真实 r3 安装、子进程纯核心和 relay 关闭由最终状态表的现场回执确认；源码和离线 PASS 不替代这些证据。工具策略已由不含 token 的诊断源替换，纯核心验收不访问 exchange、GetCommand、`_G`，不提供 `GOLD2_SIMNOW_RUNTIME`，也不授予交易准入。

r3 的真实安装回执于北京时间 2026-09-26 12:55:10 确认固定包完整 SHA／大小通过，隔离解释器启动和标准库 smoke 均为 Python 3.12.14；临时 relay 随后停用，旧 token 请求得到 410。该回执证明解释器已安装，不代表优宽已用它启动策略。既有与新建的无交易所诊断机器人均实际以 `/usr/bin/python3` 3.9.2 启动，正式核心保持 `PYTHON_VERSION_UNSUPPORTED` 阻断，不能写成优宽原生核心通过。

专属树只读 metadata 另确认 r3 的 `python/` 中间目录模式为 0777，BASE／r3ROOT 为 0700、`python/bin` 为 0700，dated binary 模式 0700，独立二进制 SHA `edffa803e5c4d73a1357f7f2c6c9fd38e9693712b2c06793e6a5e5cc1090d03a` 正确。历史安装器的 `Path.mkdir(parents=True, mode=0700)` 只约束最末目录；新增单步收紧工具仅对这个已验证新树的精确 `python/` 目录由 0777 收紧为 0700，不降低 alias 校验门槛。短 alias `/opt/yuanli-gold2-runtime/python312` 已创建并核验，精确指向固定 dated binary；实际最小 `#!` 探针仍以 3.9.2 启动。未来的新解包 helper 显式逐级创建和检查 0700，原安装器历史源码保持不变；未来安装器须显式选用新 helper。

2026-09-26 13:07:38 已将确切 r3 `python/` 目录收紧至 0700，13:08:06 专属短 alias 核验并创建成功；13:08:43 使用短 `#!` 的最小策略仍实际以 `/usr/bin/python3` 3.9.2 启动。因此长路径、短路径和 fresh 无交易所机器人都未解决原生解释器选择，不能归因于单一缓存或路径长度，也不能据此放宽版本门槛、修改默认系统 Python。

最后部署并实际执行了一个私有、无 secret 的子进程纯核心诊断：外层保持平台实际 3.9；只对固定已安装 binary 和嵌入 core 验证 SHA，启动隔离 `env={}`、`-I -B` 的 3.12 子进程，保留 30 秒运行期限和有限 stdout/stderr。它没有 exchange、GetCommand、`_G` 或正式 runtime，不运行订单；结果必须明确标注 `SUBPROCESS_PURE_CORE_ONLY_NOT_NATIVE_API`。13:13:30 的真实子进程验收已通过七项检查：最低版本和精确路径、时区、规范哈希与自引用、事件链与篡改拒绝、AU 元数据与平仓方向、bridge 纯助手与坏哈希拒绝、构造 bridge 而不调用回调。私有 launcher 和云导出全文 SHA 均为 `29ccd0241664dc0820aeaed0f789457c0b90e36bdd9e9b1cbeaf2003db509ea6`，内嵌无 secret core SHA 为 `7b6b01d70959b716999f0c00fb6a914c4cf01df7053bbd3434abec4e6a002438`。这只证明 3.12 的纯核心能够在该主机运行，不能写成优宽原生 API／正式执行运行时已接通。原生启动问题仍需平台支持或另行批准、验证的独立 bridge 方案；本轮不再扩展运行方案。
