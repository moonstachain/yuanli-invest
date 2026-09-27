# GOLD2 私有收讫服务实际部署记录

核对日期：2026-09-26。状态为 `DEPLOYED_SERVICE_DISABLED / ORDER_CLAIM_DISABLED`。这次完成基础设施部署与真实数据库内的回滚验证，没有业务启用、真实信号见证、交易端连接或订单。

## 部署内容

既有 `yuanli-invest-runtime` Supabase 项目承接独立 `gold2_paper` 私有 schema。四张表为 `signal_anchors`、`ledger_heads`、`ledger_events`、`order_claims`；未修改既有研究表。来源为 `supabase/migrations/20260925072235_gold2_paper_private_receipts.sql`，SHA256 `749830f9170b0337168fefa817ec9ad4b2292f98d03d9b2b4a73f743435daf2d`。远端执行版本是 `20260926042141`，名称为 `gold2_paper_private_receipts`；源文件日期与远端执行日期不同，不应因此再次执行同一迁移。

`gold2-paper-control` Edge Function 版本 1 已部署，运行容器状态 `ACTIVE`。应用状态经实际 HTTP 请求读回为 HTTP 503、`{"status":"SERVICE_DISABLED"}`。运行容器存在不等于应用启用。源码使用业务 HMAC 验证而非浏览器 JWT；平台 JWT 检验关闭不表示允许未签名操作。业务开关、业务密钥未配置；订单认领还受源码硬关闭控制。

部署来源文件及哈希：

| 文件 | SHA256 |
| --- | --- |
| `supabase/functions/gold2-paper-control/index.ts` | `d3a2f6938d3019ee452d3532783b57f248298b1fc04709bad4a554478ecdbb57` |
| `supabase/functions/gold2-paper-control/service.mjs` | `f78b89d97156fed1df3a7c97985ca8f956fb462104a78fe049f891aab557f6a0` |
| `supabase/functions/gold2-paper-control/core.mjs` | `03677ce9ec60b4641bf72741f417e04181eeeaf6013e7a1d2a4b546571954d2b` |

## 实际验证

四张表全部启用 RLS；`anon` 与 `authenticated` 均没有 SELECT、INSERT、UPDATE、DELETE 权限。六个对外 RPC 使用 invoker 权限，执行权限只给服务角色。安全检查中的新增 INFO 是私有表没有面向普通用户的 RLS policy，与本服务刻意拒绝浏览器访问的设计一致。

在真实远端数据库的一次显式事务中，以虚构诊断账户和非业务机器人身份验证：首次认领成功，同一命令重复返回 already-claimed，冲突命令拒绝；事件可追加和读回，前缀改写及直接更新被拒绝。事务最终 `ROLLBACK`，诊断账户、认领与事件均未保留；broker 调用为零。该测试证明数据库约束行为，不证明真实 CTP 账户绑定或实际交易幂等。

部署回执保存在工作区外 `outputs/gold2-connectivity-implementation-20260926/`：`supabase-migration-receipt.json`、`supabase-edge-deployment.json`、`supabase-disabled-endpoint-readback.json`、`supabase-table-permissions.json`、`supabase-permissions-and-advisors.json`、`supabase-live-rollback-smoke.json`。其中权限总回执的 SQL 部分只返回了最后一条函数查询；四张表权限以单独的 table-permissions 回执为准。

## 启用前仍需完成

真实账户与机器人身份绑定、非源码秘密注入和最小权限分发、真实信号外部见证、账户级待结订单互斥及终态解除认领协议、七个真实交易端回调、逐笔对账和故障演练仍未完成。数据库的命令级认领不能代替账户级并发控制；不得只配置几个环境变量就开启自动委托。
