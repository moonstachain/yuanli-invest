# GOLD2 AU 云端纯计算诊断

`scripts/build_gold_au_simnow_core_dryrun.py` 将已固定哈希的 GOLD2 纸面执行核心和优宽适配器合成一份单文件，再用独立 `main()` 覆盖原本未配置的交易入口。诊断只执行时区、ActionContract 哈希和事件链的纯计算；它没有账户凭据、`PaperGrant`、`GOLD2_SIMNOW_RUNTIME` 或订单权限，也不调用 `exchange`、`GetCommand`、`_G`、`Buy`、`Sell`、`CancelOrder`。若有人向该策略注入运行时对象，它返回 `UNEXPECTED_RUNTIME_PRESENT`，仍不调用对象。

在仓库根目录运行 `python3 scripts/build_gold_au_simnow_core_dryrun.py` 只返回哈希和字节数；加 `--output <已有目录中的绝对新 .py 路径>` 才写入权限为 `0600` 的文件，拒绝覆盖。将该文件作为**另一个独立的优宽诊断策略**保存，核对导出源码哈希，然后在已购托管者上只运行一次，读取 `GOLD2_SIMNOW_CORE_DRYRUN` 日志。预期 `status=CORE_PURE_FUNCTIONS_OBSERVED`、`order_api_calls=0`、`paper_authority_enabled=false`。这只证明已加载的单文件及纯计算在宿主解释器上工作，不证明 CTP 连通、SimNow 身份、账户资金、委托结果或生产交易运行时可用。

2026-09-25 云端浅层预检报告 Python 3.9.2 和 `zoneinfo` 可定位；本地 Python 3.9.6 编译并运行相同固定源通过。当日已在优宽保存策略 `415105`，从网站导出后与私有 v2 诊断文件逐字节核对，SHA-256 `d3cf6b0998d8c29d55cfbe048ae015e33c847a16d763a235cf78b820b3f57d7b`。机器人 `479510` **未绑定交易所**，在云端 Python 3.9.2 返回 `CORE_PURE_FUNCTIONS_OBSERVED`、`stage=complete`、`broker_api_calls=0`、`order_api_calls=0`、`paper_authority_enabled=false`，并自行停止。该结果仅覆盖加载及这三项纯计算，不等于完整策略可在 3.9 上交易。正式纸面交易的 Python 3.12 门槛与账户、外部收据、原子认领、对账门槛保持 `DENY`；该诊断不能降低它们。
