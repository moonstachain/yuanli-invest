# GOLD2-AU SimNow｜授权前部署预检

本预检只准备源码和验证宿主兼容性；不创建机器人、不绑定账户、不启用 `PaperGrant`，也不触发 `GetCommand`、交易端查询、`CommandRobot` 或任何订单 API。源码包不是上线许可或 SimNow 成交证明。

在本仓库根目录运行：

```bash
.venv/bin/python scripts/build_gold_au_simnow_bundle.py
.venv/bin/python scripts/build_gold_au_simnow_bundle.py --execute --output /absolute/private/path/gold2-au-simnow-staged-v3-identity.zip
.venv/bin/python scripts/build_gold_au_simnow_bundle.py --verify /absolute/private/path/gold2-au-simnow-staged-v3-identity.zip
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p 'test_gold_au_deploy_preflight.py' -q
```

2026-09-25 本地 v3 产物已放在仓库外的私人输出目录，文件名为 `gold2-au-simnow-staged-v3-identity.zip`。重验结果为 `SOURCE_BUNDLE_VERIFIED_NOT_DEPLOYED`，源集合 SHA-256 为 `1ae72d9173c673c9b48fb4f0a5777a33b4b50584e446885a32d0c92fd981f1b3`，完整 ZIP SHA-256 为 `de5830cbd71cbf3525fdde933f09bf3f04df14d9a82808da62743d5b7986b904`；身份校验入口源文件 SHA-256 为 `e0ebacd2dc8def03fb7752ade29cc0c69d07c782d9de665ab9bb827aadfa0572`。宿主兼容、账户连接与纸面授权仍全部为 `false`。本轮相关 32 项、当前 442 项、历史 88 项测试通过。

默认 dry-run 不写文件。`--execute` 只新建权限 `0600` 的 ZIP，拒绝覆盖；包内仅有优宽策略入口、只读预检入口、`yuanli_invest` 包初始化文件、纸面执行核心和逐文件 SHA-256 清单。当前校验器还把**整个 ZIP 字节流**与当前白名单源码重建的规范字节逐一比对，因此 ZIP comment、前缀、尾部和非规范元数据也会被拒绝；单看文件列表和 manifest 不足以证明包内没有隐藏字节。ZIP 内容与哈希不含时间戳；相同源码产生相同字节。这个 ZIP 是本地审计源包，**不是**优宽可直接上传的策略格式；[官方导入说明](https://www.youquant.com/user-guide/%E5%AE%8C%E6%95%B4%E7%AD%96%E7%95%A5%E7%9A%84%E5%AF%BC%E5%85%A5%E4%B8%8E%E5%AF%BC%E5%87%BA)将 Python 源码下载和平台导出 XML 的完整策略导入区分开。不得把原始数据、账户回执、密钥、`PaperGrant` 或本地 outbox 追加到包中。

优宽界面当前是单一代码编辑器，暂未见多文件上传。因此可以把**独立单文件** `scripts/youquant_gold_simnow_preflight.py` 的源码放入一个专门的预检草稿并保存；这个文件不依赖本仓库其他模块，使用较旧 Python 3 也能解析的保守语法，再在报告中判定项目要求的 3.12。文件加载自身不会调用 `main()`；需要宿主调用 `main()`，才能看到一次只读报告。它只观察 Python 版本、模块路径规格及 `exchange`、`GetCommand`、`_G`、`Sleep`、`Log` 名称是否存在，不调用这些宿主对象。`module_spec_located` 仅表示路径规格被定位；预检用 `PathFinder` 分段查找，不执行父包初始化，仍不能宣称模块可导入、能上传或能运行。`broker_api_calls=0` 只记录本预检脚本自身没有调用交易 API，不是全宿主审计。`HOST_PREFLIGHT_BLOCKED` 连同缺失字段说明多文件执行核心尚无可用路径；即便 `HOST_SYMBOLS_PRESENT_UNVERIFIED`，也只表示最浅层兼容性：账户身份、SimNow 第一套正常环境、机器人、CTP 合约元数据、交易时间、费用、保证金、外部时间锚、跨主机原子认领、四方对账和自定义模块上传机制仍**未验证**。优宽宿主能否导入此多文件包，需要在只读部署实验中实测；失败时不得用删掉保护检查的方式让策略“启动”。

真正的策略 `main()` 依赖外部注入 `GOLD2_SIMNOW_RUNTIME`，未注入时固定报 `RUNTIME_NOT_CONFIGURED`。后续工作必须先实现真实宿主 bootstrap 和独立来源的只读回调，再取得准确账户/机器人读回与外部账本服务；任何 `PaperGrant` 保持 `enabled=false`，直到项目纸面授权、首次蒙熊事前审核及一手工程测试所需门槛分别通过。授权前可以保存草稿和完成只读兼容性检查，不能把源码已上传或 `CommandRobot` API ACK 写成“自动模拟盘已运行”。

### 已准备的单编辑器源码

`scripts/build_gold_au_simnow_single_file.py` 把经过 SHA-256 固定的 `gold_paper.py` 与优宽适配器合成一份 Python 源码，移除仅用于本仓包结构的导入，保留其余源码原文。它只解决优宽单代码编辑器**源码装载形态**；生成物没有凭据、授权、账户连接或 `GOLD2_SIMNOW_RUNTIME`。若原文件改变，构建器拒绝生成，需先审查变更并显式更新固定哈希。可在仓库根目录离线执行：

```bash
.venv/bin/python scripts/build_gold_au_simnow_single_file.py
.venv/bin/python scripts/build_gold_au_simnow_single_file.py --execute --output /absolute/private/path/gold2-au-simnow-editor-staged-v1.py
.venv/bin/python scripts/build_gold_au_simnow_single_file.py --verify /absolute/private/path/gold2-au-simnow-editor-staged-v1.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p 'test_gold_au_single_file.py' -q
```

2026-09-25 的本地私有产物为 `outputs/gold-au-simnow-preflight-20260925/gold2-au-simnow-editor-staged-v1.py`，84,620 字节，SHA-256 `2d0185cfbd592d85425d6220f087301d9258fa4faddba17bcf367bb6d9ab5830`；模式 `0600`。该文件可以逐字节比对后用于**草稿装载实验**，但直接运行 `main()` 仍会在任何交易端调用前以 `RUNTIME_NOT_CONFIGURED` 拒绝。后续 bootstrap 和外部回调未完成前，不得将它激活为交易机器人。

账户绑定回调的候选合同已补上账号范围验证：`GetPlatformList` 原响应须含当前账号**已添加**的 CTP 对象及可解析的 Broker ID／交易前置／行情前置，`GetRobotDetail.strategy_exchange_pairs` 须把运行时机器人 ID 精确绑定到该对象 ID。`GetExchangeList` 只是全站支持的配置模板，不接受为账号连接证明；只出现 Broker ID `9999` 或一个 `first_normal_environment_verified` 布尔值也不足以证明第一套环境。优宽预置与 2026-09-25 SimNow 官网第一套第一组页面一致，V1 候选 allowlist 锁为 `182.254.243.31:30001` 与 `182.254.243.31:30011`；这仍不能证明**本账户**已连接该环境。正式 `PaperGrant` 前须复核当时官方页面和真实连接读回；本地合成响应与自报 API 方法名不能替代真实同账号读回。官网对 `GetPlatformList.profiles` 只展示占位符，当前代码仅接受可解析为直层 `BrokerId`、`TDFront`、`MDFront` 的对象或 JSON 对象字符串；其他实际形状一律 `DENY`，不得猜测字段。配置变更必须另开版本并重新打包。
