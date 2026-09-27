# GOLD2 当前研究预检与自然晨间验收

当前公有研究观察、08:30 冻结研究决定、交易执行准入是三个独立结果。当前观察不会生成有效订单合同、信号注册授权或历史事前成绩。正式晨间研究可以显式使用 `execution_mode: RESEARCH_ONLY`；真实账户费用、保证金及后续账户/委托核对仍是执行的必需输入，09:15 得到的成本不得回填 08:30。

## 当前时点真实预检

```sh
GOLD2_RESEARCH_RUNTIME="$HOME/.yuanli/runtime/gold_au_decision"
.venv/bin/python scripts/gold_au_research_diagnostic.py \
  --runtime-dir "$GOLD2_RESEARCH_RUNTIME" --capture-public
```

该独立命令在真实当前时点抓取两个 FRED CSV 和一个上期所最近已完成官方交易日日线，用已有明确指定的 273 日官方种子逐份校验原始哈希。新抓的最近日线必须与种子相同，否则阻止研究观察。每次写入新的私有 `research_diagnostics/<真实UTC时间>/`，不会写正式 `macro_captures/`、`shfe_archives/`、`requests/` 或决定 SQLite；失败也留下独立证据，不覆盖。此命令没有可伪造 08:30 的时间参数。

观察中所有价格回看输入必须严格满足**真实观测时点**的可用性。历史中间价格点仅用于当前趋势/ATR的描述，不代表历史各日的事前判断。原始取得时点、发布时间上界和哈希保持原值；宏观使用真实观测时点的严格 PIT 查询，不按观测日期提前使用。账户成本不读取、不编造，只报告不含成本的 2×ATR 一手价格风险。WGC 未提供时明确未知，预算减半；不产生可执行入场。

2026-09-26 北京时间 12:13:38—12:13:41 的实跑已成功：最新完成交易日 09-24，重新取得的官方原文哈希与种子一致，273 日回看合约参考为 au2612，ATR20=17.672 元/克，价格未超过此前 20 个交易日最高收盘；已发布宏观观测窗口实际利率变化 +51bp、广义美元 +1.2286%，均为逆风。正常波动、WGC未知时纸面政策预算 12,500 元；一手纯 2×ATR 价格风险 35,344 元，费用及实际保证金未知。它是当时研究观察，不是周一预测、08:30 决策或 SimNow 成交。

私有完整证据位于 私有运行目录下的 `research_diagnostics/20260926T041338782001Z/report.json`，同目录保存请求、FRED 原文和 manifest、重新取得的上期所原文及核验回执。

## 研究装配模式

`daily_request_sources.json` 只有显式 `execution_mode: RESEARCH_ONLY` 才省略成本输入。装配请求不会携带成本路径，来源 pin 集只包含实际读取的日历、H.10映射、当日FRED、明确指定的上期所档案及可选WGC。未知模式拒绝；未提供模式时旧的账户成本必需行为保持不变。研究模式最终 `actionable_entry=false`、`action_block=AWAITING_EXECUTION_COST_VERIFICATION`，没有订单授权。宏观缺失、来源哈希变化、日历不符及未来可用性仍然阻止研究决定。

本地目录已显式改为研究模式；修改前原始内容与前后哈希回执保存于 `source_catalog_changes/20260926T042015106910Z/`，原目录 SHA256 `20dba514747e36f9809670f19a14ec16afe98f07753e48f917c1dbe732037314`，修改后 SHA256 `52c848e38ff6d6b9b4b7c2351bee42358e63826c3daedd39d081894db67fa353`。未修改调度或交易运行时。

## 周一自然验收

保持已安装的 08:05 上期所滚动档案、08:10 宏观取得、08:25 研究装配、08:30 冻结决定顺序。宿主 Mac 必须在对应时段可运行；睡眠或离线的延迟启动不会补造及时冻结。官方日历、来源可用性和原时间窗口继续校验。

2026-09-28 的自然 08:30 运行后，执行：

```sh
GOLD2_RESEARCH_RUNTIME="$HOME/.yuanli/runtime/gold_au_decision"
.venv/bin/python scripts/gold_au_research_diagnostic.py \
  --runtime-dir "$GOLD2_RESEARCH_RUNTIME" --accept-day 2026-09-28
```

验收只读取四项文件清单与 SQLite 的只读连接，验证整个决定哈希链、追加保护及自然记录时点，不创建日志、不重放决定、不替换请求。尚未到08:31记 PENDING；之后无自然记录记 MISSING_NATURAL_DECISION；完整有效研究记录记 ACCEPTED_RESEARCH_FREEZE；明确跳过记 RECORDED_EXPLICIT_SKIP，并保留原因。输入文件存在仅标为存在，不能当账户成本真实核验；本地链仍无独立外部时间见证，不授予执行权限。缺少交易成本不妨碍显式研究模式，但仍列在执行依赖中。

剩余依赖：周一公有取得和宿主及时运行的自然证据；SimNow连接后实际账户成本/保证金的真实取得；账户、持仓、委托和结算的完整只读核对；独立信号见证与原网关准入；工程测试及随后正式模拟盘运行。这份预检不代替这些验收。
