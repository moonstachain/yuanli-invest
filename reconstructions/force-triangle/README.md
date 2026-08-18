# Force Triangle Reconstruction Packets

本目录保存历史 point-in-time 重建的**候选工件**，不是 Canon Outcome，也不是 admitted Evidence。

A5 使用两层文件：

1. `a5-evidence-freeze-v0.1.json`：冻结来源集合、T0 资格与排除状态；
2. 三个 case packet：在 Outcome 锁定状态下记录 P/N/X 暂定判断。

这些文件故意不伪装成正式 `ParadigmSnapshot` / `StageSnapshot` / `ConvexityProfile` / `ForceTriangleSnapshot`。原因是独立 Evidence Reviewer 尚未具名，历史网页/PDF 还没有通过真实 Evidence Vault 的稳定快照、SHA-256 与 locator 审核。

A6 完成真实 Evidence Vault Freeze 与 Human Adjudication 后，才能把被接受的重建编译为 `canon/` 下的新版本对象；不得覆盖 A4 pre-registration 或 A5 reconstruction 历史。