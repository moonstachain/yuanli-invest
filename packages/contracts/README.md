# Research contracts

所有 Schema 使用 JSON Schema Draft 2020-12，并以 `urn:yuanli-invest:schema:*` 作为稳定 `$id`。部署域名或目录结构不得进入 Schema 身份。

研究对象必须包含共同的审计字段，状态变化通过新版本或 `ResearchEvent` 表达。`latest` 只能由构建器生成，不能被当作历史真值。
