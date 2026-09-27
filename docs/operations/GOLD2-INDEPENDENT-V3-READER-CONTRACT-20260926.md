# GOLD2 独立 V3 reader：实现与现实验收边界

日期：2026-09-26。适用范围：SimNow 第一套正常交易环境。本文记录代码交付，**不证明 reader 已部署、实际权限已隔离、真实四方生产者已接通或模拟交易已验收**。

## 交付

`gold_au_independent_reader.py` 提供独立 reader 的组装入口和 `NATIVE_ORDER`／`PAIRED_TERMINAL` 发布器；`gold_au_reader_journal.py` 保留发布原 ID、事实哈希、原观察时间和未决状态。入口只加载既有 `broker_reader` 私有配置，不创建密钥、机器人、订阅或交易授权。原 OMS、云端候选和七个已冻结模块保持不变。

真实部署所需的输入仍需外部提供：原生只读 adapter；独立签署的部署隔离证明；订单与原生订单的准确绑定；母子 claim 的不可变绑定；四方来源及固定验证公钥；首启一次性控制面授权。缺项直接拒绝。测试提供这些契约的离线样本，不代表外部服务已存在。

## 来源与隔离

部署证明 source 为 `independent_gold2_reader_deployment_binding_v3`，需独立验签、有效期和不超过 15 秒的观察时间。证明绑定账户、机器人、实际 reader PID、reader 源码哈希、实际 reader 角色密钥 fingerprint，以及不同的 runtime PID／源码／密钥。还要求 reader 无订单提交能力、runtime 无 reader 私钥访问能力、reader 无 runtime 事件账写权限。

**不同 PID、文件名、配置声明或哈希不能证明 OS 权限隔离。** 外部控制面必须检查实际服务用户、ACL／密钥保管、网络授权和进程权限，再签署证明；代码无法自行证明这些事实。现有优宽云端是否支持独立只读进程与最小权限仍需实际核验。本轮没有配置此控制面、真实 verifier、角色密钥或部署服务。

原生订单证据来自已实现的 `BrokerFactsReader.native_order_evidence_v3`。它需要独立认证的 command→claim→平台订单→CTP 原生订单精确映射，读取实际订单、成交、持仓、现金及挂单。缺映射时拒绝，不按时间邻近、价格相近、同合约或仅一个订单猜测绑定。

## 成对四方账

成对终态先核验独立签署的母子关系 `independent_gold2_parent_child_claim_binding_v3`：母 OPEN、子 CLOSE、相同账户／具体合约、明确两笔 command／claim／order。随后重新读取两笔真实原生订单，要求各已成交一手、真实当前仓位为零、无挂单、两订单不同、账户和持仓原文哈希一致，再读一次整账户事实。

这一步产生唯一 frozen cut。broker、execution、ledger、expected 四方都必须就同一个 cut 返回独立签名回执，绑定两笔原生事实哈希、两订单、零仓和一手开平；现金、可用和冻结保证金以整数分对照原生账户，每项容许误差不超过一分。回执观察时间必须晚于 cut 请求，完整采集不超过 15 秒。代码不生成或复制四方证明。

四方固定 producer ID 和**实际验签公钥 fingerprint**必须各不相同，不能只用四个不同 callback／自报 ID。每个 verifier 需以自身固定公钥验证并返回可信结果：

```json
{
  "source": "independent_signature_verification_result_v3",
  "status": "SIGNATURE_VERIFIED_WITH_PINNED_KEY",
  "verified_signer_id": "<部署绑定的 producer ID>",
  "verified_signer_key_fingerprint": "sha256:<实际使用的固定公钥哈希>",
  "verified_receipt_sha256": "sha256:<此次被验证的回执哈希>"
}
```

返回字段必须来自可信 verifier 的固定信任配置，不能从输入回执复制；布尔 `true` 不够。reader 不持有四方生产者私钥。四种真实会计／执行／账本／预期来源和公钥登记尚未部署，当前无法产出真实成对终态。

## 发布与重启恢复

证据 ID 固定为 `EV3-` 加 `{kind, observed_at, facts_sha256}` 的 SHA256。发送前持久记录原 ID、类型、事实哈希和原观察时间，再唯一一次调用 `ingest_native_evidence_v3`，最后以同一 ID 调 `read_native_evidence_v3` 验证真实包含。重复 ID 只读，读回还重算 ID，不能把老证据的观察时间刷新成现在。

发布日志是绝对规范路径，目录须属当前用户且 0700，普通单链接文件和锁文件须 0600。每次打开重验目录，使用 dirfd 和 `O_NOFOLLOW`，整个发布／恢复流水线使用非阻塞进程锁。首次创建日志／锁和每次追加均 fsync 文件及目录；字节上限、完整末行、canonical JSON、重复字段、链哈希、准确字段、时间顺序和 Prepared→ACK／UNKNOWN→Readback 状态均检查。两个恢复 worker 不能重复追加确认事件。

失去写入 ACK，或重启时只发现 Prepared 而没有已持久 ACK，永久停止新发布；只能核对原 ID。即使原 ID 已实际包含，仍保留停止状态，不自动解除 ReceiptClient 冻结、不重发、不用 TTL 释放。明确 ACK 但尚未读回时，阻止新 ID，直至同一 ID 包含得到核对。服务仍不可用时保留未决，不能声称继续止损。

日志默认 **resume**，缺文件直接拒绝。首次初始化必须显式请求，并获得 `independent_reader_journal_bootstrap_admission_v3` 控制面回执：绑定 fresh nonce、账户／机器人／源码／实际 PID／日志路径哈希，状态 `FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED`。真实控制面必须原子地确认该 publisher scope 无已有历史／未决写，且只允许一次首启；不能因本地缺账而自动签发空账授权。此真实控制面服务尚未实现或部署。删掉 UNKNOWN 日志会拒绝恢复，不会静默建空账。

控制面的一次性判定必须以稳定的账户／机器人／reader 部署身份追踪历史，跨 PID、nonce、路径、密钥或源码升级仍检查旧未决；请求内的 PID／nonce 是此次绑定材料，不能用作允许再次首启的唯一键。没有该真实控制面事实时，初始化保持拒绝。

本地链是恢复提示和损坏检测，**不是外部锚定的不可篡改交易账**。独立账户真值和不可变证据仍由远端回执／原生事实承担。日志满、损坏、权限改变、锁冲突都拒绝新发布；没有自动清空或自动轮转。

## 接入限制与下一步验收

1. 当前入口只支持 V3 `NATIVE_ORDER` 和 `PAIRED_TERMINAL`。不接受 V2 PRE_CLAIM／TERMINAL，因此不能未经单独组装／验收就替换完整 coordinator evidence callback。
2. 实际 reader 角色、独立进程权限、固定验签公钥、订单准确映射、母子关系生产者和四方事实来源均须部署并验收；仅配置函数名不算接通。
3. 原生查询仍为同步调用。15 秒门会拒绝迟到结果；部署还需外部进程 watchdog 和交易窗口性能证据，才能声称及时保护。测试没有证明云端持续止损能力。
4. 先完成无订单的真实行情／账户／持仓／订单读回与独立证据包含，再进行已授权范围内工程开平、成对对账和结算。生产硬门保持；本轮没有新授予下单能力。
5. UNKNOWN 的人工裁定／重新准入流程仍需独立控制面验收，不能通过换日志、换证据 ID、换进程或清掉冻结继续提交。

离线测试：自测 30 项与两个独立逆向审查套件 9／11 项合计 50 项通过。覆盖同一实际签名 key 伪装四方、布尔 verifier、错误关系／金额／仓位、缺来源、ACK 丢失、跨重启冻结、删账拒绝、首启 nonce 回放、时间刷新、日志损坏／重复字段／非法状态、权限变化、多硬链接、符号链接和并发恢复。它们证明实现对这些攻击情景的拒绝，不证明实际环境已经验收。
