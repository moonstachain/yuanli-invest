# YQS-W1｜Wind Alice Evidence Provider Integration — Design Candidate

> Status: `DESIGN_CANDIDATE / HUMAN_REVIEW_REQUIRED`
>
> Program: `YQS-W1｜Wind Alice Evidence Provider Integration`
>
> Upstream dependency: `YQS0｜Yuanli Quant × Supabase Sovereign Research Kernel Architecture`
>
> Stacked base head: `6364f4ff87215b1fa13382381032864fa244748f`
>
> Provider reference: `Wind-Information-Co-Ltd/wind-skills@858043b90c916b596cd80da01e8dbf381501675d`
>
> Human design gate reserved: `ACCEPT_YQS_W1_WIND_ALICE_EVIDENCE_PROVIDER_DESIGN`

## 0. Decision

YQS-W1 integrates **Wind Alice as a read-only Machine Evidence Analyst / external research-skill provider** for Yuanli Quant Research OS.

It does **not** make Wind Alice:

- Canon Authority;
- Evidence Admission Authority;
- deterministic market-data truth;
- PIT historical truth by default;
- Thesis Authority;
- portfolio / position-sizing authority;
- broker or live-execution authority.

The architectural principle is:

```text
Wind Alice
  -> provider invocation + streamed result
  -> immutable SourceSnapshot + RunReceipt
  -> candidate Claim extraction
  -> Evidence Review / PIT eligibility
  -> ResearchCapability / EngineThesis consumption

Never:
Wind Alice output -> automatic accepted evidence / automatic thesis / automatic trade
```

YQS-W1 is intentionally **evidence-first, read-only, fail-closed**.

---

## 1. Why this provider belongs in YQOS

Wind Alice is useful because it can package Wind financial data and specialist Skills into a callable research agent. Its value to Yuanli is not that it is "another LLM", but that it can become a versioned external research provider with professional financial source access.

The provider should contribute primarily to:

1. source discovery;
2. current-state financial research synthesis;
3. company / industry / macro research artifacts;
4. fact-checking and counter-evidence generation;
5. research-question expansion;
6. candidate claims for later independent review.

It should **not** be the primary deterministic feature engine for YQOS. Numeric PIT observations used for factor research, replay and state computation should later use a separate structured Wind data/MCP provider path rather than infer values from an Alice prose report.

Therefore the program boundary is:

```text
YQS-W1 = Wind Alice A2A Evidence Provider
          -> evidence.* + runtime.run_receipts

Future separate program = Wind structured/MCP data provider
                          -> pit.observations + deterministic quant inputs
```

This separation preserves `deterministic quant, probabilistic reasoning`.

---

## 2. Verified provider facts

The design is grounded in Wind's public AIFin Market and the official `Wind-Information-Co-Ltd/wind-skills` repository pinned above.

### 2.1 Wind AIFin Market

Wind publicly describes AIFin Market as an AI-Agent financial capability marketplace with Wind data, financial skills and MCP-compatible capabilities.

### 2.2 Alice-specific transport

The official `wind-alice` Skill describes the Alice Agent integration as:

- **A2A protocol**;
- **SSE streaming**;
- final user-facing result from `agentResult.value`;
- `WIND_API_KEY` Bearer authentication;
- default Alice endpoint in the official implementation: `https://mcp.wind.com.cn/skills/alice`;
- JSON-RPC request method: `message/stream`;
- request headers include `Accept: application/json, text/event-stream` and `Content-Type: application/json`;
- when authenticated, `Authorization: Bearer <WIND_API_KEY>`;
- Alice Skill routing is encoded by the prompt prefix rather than `selectedSkillIds` / `activatedSkills` in the current official implementation;
- current Skill mode metadata includes `chatMode="12"`, `originalChatMode="4"`, `switchMode="auto"`, `timezone="Asia/Shanghai"`;
- the official Skill explicitly requires passing the user's original question without silently rewriting it;
- report/download files use the same API key for authenticated retrieval.

These are **provider-profile facts, not Yuanli Canon laws**. The protocol is external and may change; therefore it must be version-pinned and isolated behind a provider adapter.

---

## 3. Three implementation approaches considered

### Approach A — Wrap the official Wind `wind-alice` CLI initially

**Mechanism**

- install or mount the official Wind Skill externally;
- pin and verify its repository commit;
- invoke its CLI as the provider transport;
- Yuanli normalizes stdout/stderr/result metadata into its own immutable receipt and evidence contracts.

**Advantages**

- lowest protocol-drift risk;
- follows Wind's own Skill-selection and SSE behavior;
- avoids re-implementing undocumented edge cases prematurely;
- fast path to a real authenticated canary.

**Costs / risks**

- Node runtime dependency;
- third-party runtime has filesystem/network behavior;
- must not dynamically pull mutable code in production;
- Wind repository licensing / redistribution boundaries should be respected; Yuanli should not copy Wind source into its own public repo by default.

### Approach B — Native Yuanli A2A client

**Mechanism**

Implement JSON-RPC + SSE directly in Python/TypeScript against the public Alice endpoint.

**Advantages**

- clean typed interface;
- full control over retries, telemetry and structured receipts;
- no subprocess dependency.

**Costs / risks**

- protocol can drift;
- recreates behavior Wind already maintains;
- more likely to diverge from portal/Skill semantics;
- real authenticated tests become mandatory before trusting parity.

### Approach C — Treat Wind MCP as the only integration

This is attractive for deterministic data retrieval, but it does not satisfy the specific YQS-W1 goal of invoking **Alice professional Skills / Agent research output**.

### Decision

**Use Approach A for Genesis / qualification, with a strict Yuanli Provider Adapter boundary.**

A native client remains a later challenger after real canary evidence proves the transport contract stable. Structured Wind MCP ingestion is a separate future provider program.

---

## 4. System boundary

```text
User / Yuanli Research Runtime
             |
             | original prompt + optional Skill
             v
+-------------------------------------------+
| WindAliceProviderAdapter                  |
|                                           |
|  1. validate invocation                   |
|  2. resolve provider profile              |
|  3. preserve prompt bytes                 |
|  4. invoke pinned official transport      |
|  5. consume SSE until terminal result     |
|  6. sanitize secrets                      |
|  7. hash output + artifacts               |
|  8. emit ProviderReceipt                  |
+----------------------+--------------------+
                       |
              +--------+---------+
              |                  |
              v                  v
       Evidence Vault       Supabase Kernel
       raw/restricted       metadata/state
              |                  |
              |          evidence.sources
              |          evidence.source_snapshots
              |          evidence.claims (candidate)
              |          evidence.evidence_links
              |          pit.data_lineage
              |          runtime.run_receipts
              |                  |
              +--------+---------+
                       v
                  Human / Agent
                 Evidence Review
                       |
                       v
                Capability / Thesis
```

### 4.1 Important non-route

By default, YQS-W1 **does not write Alice-generated numeric statements directly into `pit.observations` as historical truth**.

If a downstream workflow wants a numeric Alice claim to become a PIT observation, it must separately establish:

- field identity;
- provider source identity;
- historical publication / availability proof;
- revision semantics;
- `known_as_of` eligibility;
- independent data lineage.

That is a distinct admission step.

---

## 5. Provider profile

The runtime consumes a versioned provider profile, conceptually:

```yaml
provider_id: wind-alice-a2a
provider_class: machine_evidence_analyst
transport: official_cli_wrapper
provider_repo: Wind-Information-Co-Ltd/wind-skills
provider_repo_commit: 858043b90c916b596cd80da01e8dbf381501675d
skill_path: skills/wind-alice
api_endpoint_default: https://mcp.wind.com.cn/skills/alice
auth_scheme: bearer
secret_ref: WIND_ALICE_API_KEY
stream_protocol: sse
rpc_protocol: jsonrpc-2.0
rpc_method: message/stream
result_field: agentResult.value
timezone: Asia/Shanghai
canon_authority: false
evidence_admission_authority: false
thesis_authority: false
live_execution_authority: false
```

The actual key is never part of this profile.

---

## 6. Invocation contract

### 6.1 Input envelope

Each call receives a typed invocation:

```text
invocation_id
provider_id
requested_at
research_target_id? 
capability_id?
replay_case_id?
user_prompt_original
prompt_sha256
skill_requested?
provider_profile_version
knowledge_cutoff?
purpose
caller_role
```

### 6.2 Prompt immutability

The user's research question is preserved verbatim as `user_prompt_original`.

A provider-specific Skill prefix may be added by the transport layer because that is part of the current Wind routing protocol, but Yuanli records both:

```text
user_prompt_original
provider_wire_prompt_hash
```

The adapter must never silently summarize, translate or "improve" the user's original question before provider invocation.

### 6.3 Skill resolution

The adapter accepts:

- no Skill -> Alice auto route;
- Chinese Skill name;
- English Skill name;
- explicitly governed aliases supported by the provider profile.

The normalized provider-resolved Skill name is recorded in the receipt.

Yuanli does **not** treat a Skill name as a Capability identity. Wind Skill taxonomy and Yuanli ResearchCapability taxonomy remain separate namespaces.

---

## 7. Secret and credential law

### 7.1 Secret identity

Use a secret reference such as:

```text
WIND_ALICE_API_KEY
```

### 7.2 Forbidden storage

The real key must never be written to:

- GitHub repository content;
- Git history;
- Supabase ordinary tables;
- Evidence body;
- RunReceipt payload;
- application logs;
- exception strings;
- screenshots committed to repo;
- prompts sent to another model.

### 7.3 Runtime secret placement

Genesis qualification should inject the key through the execution environment / secret manager of the provider worker. Supabase stores, at most, a **secret reference / provider credential identity**, never the key body.

Cloud secret installation is **not authorized by this design acceptance**.

### 7.4 Logging law

All request/response logging is secret-scrubbed before persistence. `Authorization` headers are prohibited from serialized telemetry.

---

## 8. Evidence mapping into YQS0

YQS-W1 reuses YQS0 objects; it does not create a parallel evidence ontology.

### `evidence.sources`

One provider source identity for Alice, including:

- provider = Wind;
- source class = `machine_evidence_analyst`;
- access classification = restricted/licensed external;
- authority tier = non-canon candidate evidence source;
- provider profile/version reference.

### `evidence.source_snapshots`

Each completed Alice invocation creates an immutable snapshot metadata record containing at least:

```text
source_snapshot_id
source_id
invocation_id
captured_at
available_at
known_as_of
content_sha256
content_locator
provider_profile_version
provider_repo_commit
skill_resolved
prompt_sha256
request_wire_hash
response_terminal_state
access_classification
```

Large/raw content lives in a restricted evidence object store / vault; GitHub contains only contracts, hashes and non-sensitive fixtures.

### `evidence.claims`

Claims extracted from `agentResult.value` are **candidate claims** only.

Each claim must retain:

- source snapshot ref;
- exact locator within the provider output when possible;
- claim type;
- extraction method/version;
- current `known_as_of`;
- review state;
- support/counterevidence links.

### `evidence.evidence_links`

Alice can support or challenge a claim, but the link does not itself promote the claim to accepted evidence.

### `pit.data_lineage`

Records the transformation chain:

```text
Wind Alice invocation
-> source snapshot
-> claim extraction
-> research state/capability consumption
```

### `runtime.run_receipts`

Every call produces an immutable Provider/Research Receipt.

---

## 9. PIT law for an AI-generated external source

This is the most important YQS-W1 rule.

### 9.1 Alice response time is not historical data time

An Alice report generated at `2026-08-26T...` cannot be backdated to 2024 merely because the report discusses a 2024 financial statement.

For the Alice-generated artifact itself:

```text
captured_at = when Yuanli captured the provider output
available_at = no earlier than successful provider delivery
known_as_of = conservative time at which the complete output became knowable to Yuanli
```

### 9.2 No synthetic historical authority

For historical Replay, an Alice output is ineligible if it was generated after the replay knowledge cutoff, unless the workflow separately reconstructs and proves the underlying historical information set under YQS0 PIT-05/PIT-06.

Therefore:

```text
Alice generated today
  != evidence known historically
```

### 9.3 Underlying source citations

If Alice returns source references, those references may become candidates for independent capture. They do not inherit historical eligibility simply because Alice cites them.

The downstream capture must prove publication/availability timing separately.

### 9.4 Fail closed

If the historical knowability of an underlying source cannot be established, the replay status is `unknown/ineligible`, never inferred from current availability.

---

## 10. SSE / completion semantics

The adapter treats the provider call as a streamed task.

It records:

```text
request_started_at
first_event_at?
terminal_event_at?
response_completed_at
provider_task_id?
provider_context_id?
event_count
event_digest
terminal_state
agent_result_sha256
```

Only the provider's terminal result is eligible to become the canonical **provider output snapshot** for that invocation.

Intermediate SSE reasoning/status events may be retained as restricted diagnostic telemetry but do not automatically become evidence claims.

---

## 11. Retry and cost discipline

Wind professional Skills may take minutes and consume account points. Duplicate invocations are not harmless.

Therefore YQS-W1 uses conservative retry semantics:

1. before any response/SSE event is observed, a clear transport failure may permit **at most one** automatic transport retry;
2. after the first provider event has been received, the adapter does not automatically issue a duplicate research task;
3. application-level failures, quota exhaustion, authorization errors and terminal provider errors require a new governed attempt / explicit requeue;
4. all attempts share an `invocation_intent_id` but have distinct `attempt_id` values;
5. the runtime records estimated/returned cost or point metadata if the provider exposes it, but never fabricates cost when unavailable.

---

## 12. Attachment handling

Alice Skills can return downloadable files.

Yuanli attachment rules:

1. download only provider-returned URLs whose host/path passes an explicit Wind allowlist;
2. authenticate with the same runtime secret only in-memory;
3. never log the Bearer token;
4. stream bytes directly to restricted evidence storage;
5. calculate SHA-256 while writing;
6. record MIME/type, size, original provider URL hash and local/object-store locator;
7. do not commit provider report bodies or licensed binary artifacts to public GitHub;
8. attachment download failure does not rewrite the completed provider result; it creates a separate retrieval status/error record.

The allowlist is configurable/versioned because provider download domains may evolve.

No arbitrary URL emitted by an LLM may be downloaded merely because it appears in text.

---

## 13. Authority boundary

### Alice may

- retrieve/analyze under its own provider capabilities;
- produce research artifacts;
- propose claims;
- provide candidate counterevidence;
- generate provider-side Skill output;
- return source/file locators.

### Alice may not

- mark a Yuanli claim `accepted`;
- promote a ResearchCapability;
- create Canon deltas;
- mutate EngineThesis authority;
- authorize PositionPassport/BookState;
- write portfolio weights;
- create buy/sell/hold instructions as Yuanli authority;
- invoke a broker;
- change GitHub Canon.

### Yuanli invariant

```text
Claim Authority <= Evidence Authority
Provider Analysis != Primary Evidence
Research PASS != Capital PASS
```

---

## 14. Supply-chain boundary

The Wind Skill repository is third-party provider code.

Genesis path:

- pin exact provider repository commit;
- verify expected commit before execution;
- do not use a mutable `latest` provider runtime in qualification evidence;
- do not dynamically execute newly downloaded provider scripts inside a privileged worker;
- run the provider transport with the minimum filesystem/network permissions it requires;
- do not copy or republish Wind source code into Yuanli public Canon unless licensing explicitly permits it.

The provider commit is part of every qualification receipt.

When Wind updates the official Skill, Yuanli performs a provider-profile qualification before changing the pinned version.

---

## 15. Genesis canary

No real Alice call is performed until a credential is installed outside chat and a separate runtime authorization is given.

The first live canary should be intentionally low-cost and non-trading.

Recommended canary class:

```text
Skill: Fact Check / 事实核验
Purpose: verify one simple public financial identity or statement
Output requirement: concise conclusion + source trace
```

The canary validates only:

1. authentication;
2. Skill routing;
3. SSE completion;
4. result extraction;
5. secret redaction;
6. immutable snapshot hash;
7. attachment handling if present;
8. Supabase/evidence mapping once YQS0/YQS1 substrate exists.

It does **not** validate investment alpha or research quality.

---

## 16. Qualification tests

Before any provider result is used by YQOS research, YQS-W1 implementation must pass:

### Contract tests

- original prompt remains unchanged;
- provider Skill prefix is isolated from original prompt;
- profile version and provider commit are recorded;
- missing key fails closed;
- key never appears in stdout/stderr/receipt fixtures;
- non-Wind attachment hosts are rejected;
- response hashes are deterministic for identical fixture bytes.

### SSE fixture tests

- normal completion;
- partial stream / disconnect;
- malformed event;
- provider terminal error;
- quota exhaustion;
- duplicate terminal event;
- no `agentResult.value`;
- attachment success/failure.

### PIT tests

- current Alice output cannot be used before its `known_as_of`;
- current Alice output cannot enter an older Replay by backdating its subject period;
- cited historical source requires independent historical eligibility.

### Authority tests

- provider cannot set evidence admission state to accepted;
- provider cannot create Canon/Registry promotion;
- provider cannot authorize capital or live execution.

### Live canary

A real authenticated canary must be separately approved and its exact provider commit/profile recorded.

---

## 17. Failure semantics

Normalized provider outcomes:

```text
success
transport_error
unauthorized
quota_exceeded
provider_error
stream_incomplete
result_missing
attachment_partial
cancelled
unknown
```

A failed provider call never creates a false-success evidence snapshot.

A failed call **does** create an immutable runtime receipt describing the failure, with secrets removed.

---

## 18. Observability

Minimum operational metrics:

```text
wind_alice_invocations_total
wind_alice_success_rate
wind_alice_latency_seconds
wind_alice_stream_incomplete_total
wind_alice_quota_exceeded_total
wind_alice_unauthorized_total
wind_alice_attachment_failures_total
wind_alice_claims_extracted_total
wind_alice_claims_admitted_total
wind_alice_claim_admission_rate
wind_alice_replay_ineligible_total
```

The final two categories are deliberately separate: retrieval volume must never be confused with accepted evidence quality.

---

## 19. Data retention / licensing posture

Wind output is treated as restricted/licensed external evidence unless the provider terms explicitly permit broader redistribution.

Default posture:

- no raw Wind/Alice report bodies in public GitHub;
- no public redistribution of downloadable provider files;
- keep source body/artifacts in restricted evidence storage;
- GitHub may retain contracts, hashes, provider profile metadata and synthetic fixtures;
- Supabase stores operational metadata and typed candidate claims subject to access controls;
- deletion/retention policy must respect provider terms and organizational policy.

---

## 20. Dependency and sequencing

YQS-W1 is stacked on YQS0 because it depends on the YQS0 Evidence/PIT/Runtime authority boundary.

Legal sequence:

```text
YQS0 architecture accepted + merged
        |
        v
YQS1 local Supabase kernel substrate
        |
        +-------------------------+
        |                         |
        v                         v
YQS-W1 provider adapter      future Wind MCP data provider
        |
        v
no-secret synthetic qualification
        |
        v
credential installation authorization
        |
        v
one live canary
        |
        v
Human Review
        |
        v
read-only shadow use
```

YQS-W1 design acceptance alone does **not** authorize YQS0/YQS1, credential installation, cloud infrastructure or provider calls.

---

## 21. Non-goals

YQS-W1 does not:

- create a Supabase production project;
- install a paid plan;
- collect a real API key in ChatGPT;
- ingest private account credentials;
- scrape the logged-in Alice web UI;
- replace deterministic Wind market/fundamental ingestion;
- create a factor pipeline;
- create an Alpha Engine;
- authorize Evidence Admission;
- authorize ME2–ME5 / QXM3;
- authorize portfolio allocation;
- authorize brokerage/live execution.

---

## 22. Acceptance criteria for this design

Human review should answer PASS only if all are true:

1. Alice is classified as Machine Evidence Analyst, not Canon Authority.
2. Alice A2A and future Wind structured/MCP data paths are not conflated.
3. provider protocol is isolated behind a versioned adapter.
4. official provider repository commit is pinned for qualification.
5. API key never enters GitHub/Supabase ordinary data/logs/prompts.
6. original user prompt is preserved.
7. current Alice synthesis cannot be backdated into historical Replay.
8. provider output maps to YQS0 evidence/runtime objects without inventing a parallel ontology.
9. claims remain candidates until separate admission/review.
10. attachments are restricted, hashed and host-allowlisted.
11. duplicate/costly automatic retry is constrained.
12. no capital/trading/live-execution authority is created.
13. real authenticated canary requires a later explicit authorization.
14. YQS-W1 cannot merge ahead of its YQS0/YQS1 dependencies.

If accepted, the exact design token is:

`ACCEPT_YQS_W1_WIND_ALICE_EVIDENCE_PROVIDER_DESIGN`

Acceptance means **design only**. It does not imply implementation, secret installation, live invocation or merge.
