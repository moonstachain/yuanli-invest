# YMQ-PROD0-G0｜Founder Team Research Runtime Written Spec

**Status:** DESIGN_ACCEPTED / WRITTEN_SPEC_CANDIDATE  
**Date:** 2026-09-15  
**Product boundary:** Founder Team × Research Runtime × Dual-Key Research Gate × Cockpit-first × Event-native semantics  
**Authority boundary:** Research only. `CAPITAL_NOT_AUTHORIZED / EXECUTION_NOT_AUTHORIZED`.

## 0. Purpose

YMQ-PROD0 turns the already machine-qualified YMQ sovereign intelligence stack into a production research product for a 5–20 person founder research team.

The system is not an AI report generator. It is a sovereign, point-in-time-preserving research runtime that converts important world changes into evidence-qualified research projections, forces those projections to face future reality settlement, and turns error into governed learning.

The single product hypothesis for the first 90 days is:

> Can a founder team use one governed research runtime to move important changes from Signal → Case → Evidence → Compute → Dual-Key Gate → Research Projection → Reality Settlement → Learning, while preserving sovereignty, point-in-time truth, auditability, and founder attention leverage?

## 1. Product Constitution

### 1.1 First principle

`Trust → Close → Transfer → Live → Settle.`

The product first proves trustworthiness, then closes one full research loop, then proves transferability across three different research domains, then becomes a daily team workflow, and only then earns the right to scale.

### 1.2 Authority law

The following separations are non-negotiable:

- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`
- `ResearchPass != CapitalPass`
- `UNKNOWN = DENY`
- `ClaimAuthority <= EvidenceAuthority`
- No product launch, workflow automation, agent output, or founder action may silently escalate research authority into capital or execution authority.
- Founder may change Canon through the governed Canon process, but may not bypass a machine gate for a specific case.

### 1.3 Core product law

YMQ-PROD0 is a sovereign, PIT-preserving, event-semantic research runtime in which humans formulate hypotheses, evidence is independently admitted, machines enforce contracts, compute providers remain non-authoritative, research projections are versioned rather than overwritten, and every qualified belief must eventually face Reality Settlement.

## 2. Product Boundary

### 2.1 In scope

V1 is an internal Founder Team product for 5–20 users.

Primary roles:

- Founder
- Researcher
- Evidence Reviewer
- Runtime Operator

Primary work surface:

- Founder Research Cockpit

Primary operating mode:

- Research Runtime

Primary governance model:

- Dual-Key Research Gate

Initial research universe:

1. AI Infrastructure
2. Gold / Global Money
3. China Policy / New Manufacturing

### 2.2 Explicitly out of scope

YMQ-PROD0 does not include:

- real-money execution
- broker connectivity
- VeighNa live execution
- automated position sizing
- Capital Authority admission
- Execution Authority admission
- external multi-tenant SaaS
- billing
- 100-battle coverage
- universal autonomous research agent
- automatic Canon modification
- Kafka/Pulsar/event-mesh infrastructure

## 3. Sovereign System Architecture

YMQ-PROD0 consists of one Human Principal layer plus six system planes.

### P0｜Human Principal

Founder retains ultimate sovereignty for Canon escalation and any future Capital or Execution authority transition.

### P1｜Experience Plane

**Provider:** Founder Research Cockpit  
**Role:** operational work surface

Primary responsibilities:

- route attention
- present research state
- support research and review actions
- expose system health and escalation

The Cockpit is an Attention Router, not a generic BI dashboard.

### P2｜Law Plane

**Provider:** GitHub  
**Role:** Canon / contracts / schema / gate rules / versioning / CI qualification

GitHub determines what is allowed to happen. Production behavior must be traceable to an approved Git SHA and contract hash.

### P3｜Reality Plane

**Provider:** Supabase / PostgreSQL  
**Role:** canonical Reality Ledger

Supabase records what actually happened and what was known at T0.

It preserves:

- raw evidence lineage
- source snapshots
- PIT observations
- claim receipts
- research case versions
- independent reviews
- compute receipts
- gate runs
- research projections
- settlements
- learning deltas
- append-only events and receipts

### P4｜Runtime Plane

**Provider:** n8n + Yuanli Gateway  
**Role:** deterministic research process runtime

Responsibilities:

- trigger
- route
- wait
- retry
- dispatch
- request human decision
- synchronize
- notify
- reconcile

n8n is not Brain, Truth, or Law. It orchestrates approved capabilities.

### P5｜Compute Plane

**Providers:** Quant/Python Runtime + Hugging Face Blind Runner  
**Role:** heavy computation only

Responsibilities may include:

- quantitative transforms
- PIT replay
- rolling statistics
- transmission models
- corpus analysis
- blind benchmarks
- deterministic remote compute

Compute providers receive no Canon, Capital, or Execution authority.

### P6｜Projection Plane

**Provider:** Notion  
**Role:** Human Knowledge Surface / projection only

Notion receives admitted research projections and human-readable reports. It is not canonical truth and may not grant authority.

### 3.1 Canonical operating sentence

> GitHub 定法，Supabase 存真，Quant/HF 求解，n8n 执行程序，Cockpit 分配注意力，Notion 沉淀人类知识，Human Principal 保留主权。

## 4. Product Work Model

### 4.1 Primary unit of work

`ResearchCase` is the primary unit of work.

A Battle is a research domain. A Thesis is a versioned claim inside a ResearchCase. The product must not create separate software stacks for each Battle.

### 4.2 Research Case lifecycle

A ResearchCase may contain:

- Battle
- T0
- Question
- Thesis
- Hypotheses
- Evidence
- Falsifiers
- Reality State
- Narrative State
- Transmission State
- Price / Payoff State
- Survival State
- Researcher Signature
- Reviewer Signature
- Machine Gate
- Research Projection
- Reality Settlement
- Learning Delta

### 4.3 Case identity vs thesis version

A Case has a stable identity.

A Thesis is immutable once frozen. Any change creates a new `case_version` that supersedes, but never overwrites, the prior version.

## 5. Cockpit Product Architecture

V1 has four first-level workspaces plus one contextual copilot.

### 5.1 TODAY

Purpose: answer `What changed since I last looked?`

The page prioritizes:

- Reality Changes
- Narrative Changes
- Price Changes
- Research Queue
- Gate Alerts
- Settlement Feed

Each attention card exposes:

- what changed
- why it matters
- evidence status
- current belief
- falsifier
- owner
- next required action

Attention is grouped into:

- P0｜NOW
- P1｜TODAY
- P2｜THIS WEEK
- P3｜WATCH

Initial priority semantics:

`Magnitude of Δ × Acceleration Δ² × Capital Relevance × Uncertainty Change × Time Sensitivity`

The product must not pretend this is a precise scientific score in V1; priority buckets are the operational output.

### 5.2 THEMES

Purpose: provide a reusable Battle Room for each research domain.

Every Battle follows the same cognitive order:

1. Reality
2. Change Δ / Δ²
3. Evidence
4. Narrative
5. Transmission
6. Price / Payoff
7. Thesis
8. Falsifier
9. Gate
10. Projection
11. Settlement

The first three Battles are:

- AI Infrastructure
- Gold / Global Money
- China Policy / New Manufacturing

### 5.3 EVIDENCE & GATE

Purpose: create an epistemic control tower.

Evidence Inbox includes:

- New Source
- Updated Source
- Conflicting Source
- PIT Risk
- Revision Risk
- Timestamp Risk
- Archive Failure
- Licensing Issue

Every Evidence Card should expose:

- Source Authority
- Publication Time
- Observation Time
- Ingestion Time
- Archive Provenance
- PIT Status
- Revision Status
- Rights / License
- Hash
- Claims Supported
- Claims NOT Supported (`Does Not Prove`)

Gate status may include:

- Evidence Sufficiency
- PIT Integrity
- Source Independence
- Narrative Evidence
- Transmission Evidence
- Price Evidence
- Falsifier Defined
- Compute Receipt
- Reviewer Signature

There is no `FORCE_PASS` or `IGNORE_WARNING` control.

### 5.4 REVIEW & LEARNING

Purpose: make every qualified belief face Reality.

Settlement views must restore T0 state before comparing with T1 reality.

Required settlement questions:

1. What did we know?
2. What did we believe?
3. What did we expect?
4. What actually happened?
5. What capability should change?

Learning must classify failure modes such as:

- source coverage failure
- transmission model failure
- narrative lag
- price misread
- regime misclassification
- weak falsifier
- PIT leakage
- reviewer bias

Learning may create a Capability Change Proposal, but may not modify Canon automatically.

### 5.5 Founder Copilot

Founder Copilot is contextual, not a generic chatbot.

It carries current:

- battle_id
- case_id
- T0
- Evidence refs
- Gate state
- Canon SHA
- current Projection

Default intents:

- 为什么？ → Evidence
- 然后呢？ → Transmission
- 市场知道了吗？ → Price / consensus
- 什么会证明我们错？ → Falsifier
- 这对资本意味着什么？ → Research Projection only

The Copilot does not own facts. It compiles context, routes capability calls, waits for gates, and explains qualified research state.

## 6. Team Governance and Dual-Key Research Gate

### 6.1 Separation of duties

For the same frozen Case Version:

- Author != Reviewer
- Researcher cannot certify own Evidence
- Reviewer cannot silently rewrite Thesis
- Reviewer decision preserves timestamp and rationale
- Machine Gate is deterministic and fail-closed

For critical cases, Evidence Review should be semi-blind where practical: the reviewer should not need to see the final projected conclusion before evidence qualification.

### 6.2 Gate sequence

`Researcher Thesis Sign → Evidence Reviewer Sign-off → Machine Gate → Research State`

Allowed machine states:

- READY
- READY_WITH_LIMITATIONS
- INDETERMINATE
- BLOCKED
- SCIENTIFIC_NO_GO

`INDETERMINATE` is a valid scientific outcome, not a runtime failure.

### 6.3 Founder role

Founder handles only high-leverage escalation:

- Canon Change
- future Research → Capital Authority
- future Capital → Execution Authority
- strategic unknowns

Founder should not become routine research approver.

## 7. Canonical Data Model

The implementation must extend existing `evidence`, `pit`, and `runtime` lineage rather than create a competing truth schema.

### 7.1 Existing canonical lineage to preserve

Existing objects include:

- `evidence.sources`
- `evidence.source_snapshots`
- `pit.observations`
- `runtime.reality_gate_runs`
- `evidence.claim_receipts`
- `runtime.agent_runs`
- `runtime.research_projections`
- `runtime.learning_deltas`

### 7.2 Additive PROD0 objects

Recommended additive objects:

- `research.battles`
- `research.cases`
- `research.case_versions`
- `research.case_evidence_links`
- `research.review_decisions`
- `runtime.compute_runs`
- `runtime.workflow_runs`
- `runtime.events`
- `runtime.research_gate_runs`
- `runtime.reality_settlements`

Existing tables should be extended only where backward compatibility and authority semantics remain intact.

### 7.3 Immutability rules

- Frozen Case Versions are append-only.
- Prior evidence decisions are not deleted when later invalidated; a new receipt supersedes the old one.
- Research Projections are versioned rather than overwritten.
- Learning only affects future behavior and cannot rewrite T0 history.

## 8. Event-Semantic Ledger

V1 uses Event-Semantic Ledger, not full Event Sourcing.

Architecture:

`Immutable Domain Objects + Append-only Event Ledger + Rebuildable Read Models`

### 8.1 Event envelope

Every material action records at minimum:

- event_id
- event_type
- event_version
- occurred_at
- recorded_at
- workspace_id
- battle_id
- research_case_id
- case_version_id
- correlation_id
- causation_event_id
- run_id
- actor_type
- actor_id
- actor_role
- authority
- canon_sha
- workflow_contract_sha
- evidence_refs
- input_hash
- output_hash
- idempotency_key
- status
- receipt_id
- payload

### 8.2 Event invariants

- `runtime.events` is append-only.
- Business roles may INSERT and SELECT; normal operations may not UPDATE or DELETE canonical event history.
- `idempotency_key` is unique within the relevant capability scope.
- `correlation_id` connects the full research chain.
- `causation_event_id` preserves causal lineage.

## 9. Mutation and Idempotency Law

### 9.1 Canonical mutation path

n8n must not directly act as sovereign writer to canonical tables.

Canonical mutation path:

`n8n → versioned RPC/Edge Function/API → contract validation → authority validation → state-transition validation → idempotency validation → transaction`

### 9.2 Atomic write law

Every canonical business action commits:

`Domain Object + Event + Receipt = One Transaction`

If one component fails, the transaction rolls back.

### 9.3 Idempotency

The same logical request may be retried without creating a second reality.

A stable idempotency key should be derived from inputs such as:

- capability_id
- case_id
- case_version
- logical_operation
- input_hash

A repeated request with the same idempotency key returns the existing canonical result/receipt instead of creating a duplicate fact.

### 9.4 Runtime disposability

n8n execution state is not canonical business state.

If n8n loses transient state, the system must recover from Supabase by finding incomplete canonical processes and resuming the next legal transition.

`Runtime is disposable; Reality is durable.`

## 10. Seven Production Capability Workflows

### W1｜Signal Observer

**Input:** battle_id, as_of, source_cursor, canon_sha  
**Purpose:** source refresh, Δ/Δ² detection, importance screening  
**Output event:** `SIGNAL_OBSERVED`

W1 may propose signals but may not create an authoritative Thesis.

### W2｜Case Genesis

**Input:** signal_refs, question, hypotheses, falsifiers, researcher_signature  
**Purpose:** freeze ResearchCase + CaseVersion  
**Output event:** `CASE_FROZEN`

Once frozen, changes create a new version.

### W3｜Evidence Admission

**Input:** case_version_id, candidate source snapshots, claim map  
**Checks:** provenance, PIT, timestamps, revisions, rights, source independence, authority  
**Output:** Claim Receipts  
**Events:** `EVIDENCE_ADMITTED / EVIDENCE_LIMITED / EVIDENCE_BLOCKED`

Reviewer may qualify Evidence but may not rewrite Thesis.

### W4｜Compute Dispatcher

**Input:** case_version_id, evidence_refs, compute_spec_hash, input_hash  
**Routes:** Quant/Python or HF Blind Runner  
**Output:** provider_run_id, result_hash, runtime metadata, compute receipt  
**Events:** `COMPUTE_DISPATCHED / COMPUTE_SETTLED`

External compute is dispatch-once / poll-many. A timeout must not blindly create duplicate jobs.

### W5｜Dual-Key Research Gate

**Required inputs:** Frozen Case Version, Researcher Signature, Independent Review, Required Evidence, Required Compute Receipts, current Canon SHA  
**Checks:** Evidence Sufficiency, PIT Integrity, Authority Ceiling, Source Independence, Compute Completeness, Falsifier Presence, Contract Integrity  
**Allowed outputs:** READY / READY_WITH_LIMITATIONS / INDETERMINATE / BLOCKED / SCIENTIFIC_NO_GO  
**Event:** `RESEARCH_GATE_SETTLED`

There is no override path.

### W6｜Projection Publisher

Only READY and READY_WITH_LIMITATIONS may enter the normal Research Projection path.

**Input:** research_gate_run_id, case_version_id  
**Output:** versioned Research Projection  
**Event:** `PROJECTION_PUBLISHED`

Supabase is committed before Cockpit/Notion projection. A Notion failure is a projection degradation, not research truth failure.

### W7｜Settlement & Learning

**Triggers:** 30D / 60D / 90D / falsifier / major regime event / authorized manual replay  
**Required T0 restore:** Case Version, Evidence, Projection, Price, Canon SHA  
**T1 comparison:** observed Reality  
**Outcomes:** SUPPORTED / PARTIAL / FALSIFIED / INDETERMINATE  
**Outputs:** RealitySettlement + LearningDelta

Learning is forward-only and cannot rewrite historical evidence or beliefs.

## 11. Runtime Reconciler

The Runtime Reconciler is infrastructure, not an eighth research workflow.

It checks for conditions such as:

- WorkflowRun without Event
- Event without Receipt
- Projection without Gate
- Gate without Review
- Compute without Hash
- expired pending runs
- duplicate idempotency conditions
- n8n/GitHub workflow drift
- Notion projection lag

The reconciler may safely repair transient/runtime projection state or raise an incident. It may never fabricate Evidence, generate a PASS, or escalate authority.

## 12. State Model

Recommended case progression:

`DRAFT → EVIDENCE_PENDING → REVIEW_PENDING → COMPUTE_PENDING → MACHINE_GATE_PENDING → {READY | READY_WITH_LIMITATIONS | INDETERMINATE | BLOCKED | SCIENTIFIC_NO_GO} → PROJECTION_PUBLISHED → SETTLEMENT_DUE → SETTLED → LEARNING_CREATED`

State transitions are enforced by canonical mutation contracts, not by ad hoc n8n memory.

## 13. Read Model vs Write Model

### Canonical write side

Strict, auditable, slower if necessary:

- Evidence
- Case Version
- Review
- Gate
- Projection
- Settlement
- Event
- Receipt

### Cockpit read side

Rebuildable projections may include:

- current_case_state
- today_attention_queue
- battle_summary
- reviewer_queue
- settlement_queue
- founder_escalations

Read models may be views, materialized views, or cached API projections. They may be deleted/rebuilt. Canonical history may not.

## 14. Identity and RBAC

### 14.1 Principal identity

The system uses a stable `principal_id` across planes.

Authorization is based on:

`principal_id + role + scope`

not merely platform email identity.

### 14.2 Human roles

- FOUNDER
- RESEARCHER
- EVIDENCE_REVIEWER
- OPERATOR

### 14.3 Machine identities

At minimum:

- `svc_n8n_runtime`
- `svc_quant_runner`
- `svc_hf_dispatch`
- `svc_projection_sync`
- `svc_reconciler`
- `svc_ci_migration`

Each machine identity follows least privilege by capability.

### 14.4 Core RBAC rules

- Researcher may create/freeze owned research versions within scope.
- Reviewer may admit/reject/downgrade Evidence but not author the same frozen Thesis.
- Machine alone settles deterministic gate state.
- Founder approves Canon escalation, not routine Gate results.
- Operator manages runtime, not research authority.
- No role in PROD0 may grant Capital or Execution authority.

## 15. Environment Isolation

At least three environments are required:

- DEV
- STAGING
- PROD

Rules:

- DEV uses synthetic/fixture data and no production sovereign secrets.
- STAGING uses masked/history/synthetic data suitable for integration and replay.
- PROD holds canonical Reality.
- DEV workflows cannot write production Reality at credential/network/policy level.

## 16. Secret and Credential Architecture

### 16.1 Secret law

No secret literals may appear in GitHub Canon artifacts.

GitHub stores only metadata such as:

- secret name
- provider
- required scope
- rotation policy
- credential identifier

Actual credentials live in authorized secret stores such as GitHub Actions Secrets, n8n Credential Store, platform secret stores, or equivalent governed stores.

### 16.2 Browser boundary

The browser client never holds sovereign credentials such as:

- Supabase service role
- HF write token
- GitHub write credential
- n8n admin credential
- Notion integration secret

### 16.3 Credential lifecycle

Every production credential should track:

- credential_id
- provider
- owner
- purpose
- scope
- environment
- created_at
- last_rotated_at
- next_rotation_due
- status
- last_used_at
- dependent_capabilities

States include:

- ACTIVE
- ROTATION_DUE
- REVOKED
- COMPROMISED

## 17. Production Change and Deployment Governance

Production changes are GitOps-like and must be bound to approved Git SHA / contract hash.

Normal path:

`Change proposal → branch → tests → review → merge → CI qualification → staging → reality test → production promotion`

Direct production UI editing is prohibited except governed Break Glass operations.

### 17.1 Workflow authority tiers

**Tier 1｜Low Authority**

Examples: Notion sync, notification, read-only watch.

**Tier 2｜Research State**

Examples: Case Genesis, Compute Dispatcher, Projection Publisher.

Require PR, tests, staging run, review.

**Tier 3｜Epistemic Authority**

Examples: Evidence Admission, Research Gate, Settlement.

Require contract tests, blind replay, drift check, human approval, exact-SHA deployment, post-deploy readback.

### 17.2 Drift law

Approved n8n workflow definitions are bound to:

- capability_id
- workflow_contract_version
- workflow_contract_sha
- expected_live_hash

High-authority workflow drift fails closed.

### 17.3 Deployment Receipt

Every production deployment records:

- deployment_id
- environment
- git_sha
- capability_id
- workflow_contract_sha
- n8n_definition_hash
- db_migration_sha
- frontend_sha
- gateway_sha
- deployed_by
- approved_by
- deployed_at
- precheck
- postcheck
- rollback_ref

## 18. Observability

YMQ-PROD0 requires four observability layers.

### L1｜Infrastructure

- availability
- latency
- CPU/memory
- DB connections
- API health
- queue depth

### L2｜Workflow

- success rate
- retry rate
- dead-letter rate
- workflow latency
- stuck runs
- duplicate attempts
- projection lag

### L3｜Data Integrity

- PIT integrity
- hash mismatch
- missing Evidence
- source freshness
- duplicate idempotency
- receipt mismatch
- RLS violations

### L4｜Research Integrity

- Evidence rejection rate
- INDETERMINATE rate
- Gate downgrade rate
- reviewer disagreement
- Settlement overdue
- Falsifier hit rate
- Canon drift
- Workflow drift

Infrastructure may be GREEN while Research Integrity is RED. Research Integrity is therefore a first-class operational health dimension.

## 19. SLOs and Zero-Tolerance Integrity Targets

Initial V1 targets:

- Daily refresh complete by 08:45: ≥99%
- P0/P1 workflow successful completion: ≥99.5%
- Qualified Projection → Cockpit visibility: p95 <60 seconds
- Due Settlements closed within 48h: ≥95%

Evidence freshness is source-class specific.

Zero-tolerance targets:

- undetected Canon drift = 0
- silent authority escalation = 0
- canonical mutation without receipt = 0

## 20. Incident Model

### SEV-0｜Sovereignty Incident

Examples:

- unauthorized Capital/Execution action
- Canon bypass
- Reality history mutation
- high-authority credential compromise
- silent authority escalation

Action: immediate freeze of affected capability.

### SEV-1｜Truth Integrity Incident

Examples:

- PIT leakage
- hash mismatch
- false Gate PASS
- Evidence corruption
- duplicate canonical truth

Action: freeze affected authority path, block downstream projection, reconcile Reality.

### SEV-2｜Runtime Incident

Examples:

- n8n outage
- HF unavailable
- Quant job stuck

Truth remains intact; system enters degraded mode.

### SEV-3｜Projection Incident

Examples:

- Notion sync failure
- stale UI card
- notification delay

Research truth remains valid.

### 20.1 Incident response order

`Contain → Preserve Evidence → Freeze Authority → Reconcile Reality → Recover Runtime → Resume → Settle Incident → Learn`

Integrity outranks availability.

## 21. Break Glass and Kill Switch

### 21.1 Break Glass

Emergency action requires:

- incident_id
- Founder + Operator acknowledgement
- time-limited credential
- scoped action
- automatic expiry
- full audit
- mandatory postmortem

Break Glass may restore runtime but may not rewrite research conclusion or bypass epistemic gate law.

### 21.2 Capability Kill Switch

The product supports capability-level and Battle-level freeze instead of only global shutdown.

Examples:

- W3 Evidence OFF
- W5 Gate OFF
- China Battle EVIDENCE_FREEZE

A frozen capability may block new downstream authority while preserving read access and unaffected workflows.

## 22. Disaster Recovery

Recovery priority follows irreversibility.

Critical recoverable estate includes:

- GitHub Canon
- Supabase canonical database
- raw Evidence objects
- workflow definitions
- deployment receipts
- compute receipts
- projection manifests

Notion, Cockpit read models, n8n transient state, and compute outputs may be rebuilt where authoritative receipts and Reality remain intact.

Initial recovery targets:

- GitHub Canon: RPO ≈0 / RTO 1h
- Supabase Canonical Truth: RPO ≤15m / RTO 2h
- Raw Evidence: RPO ≤1h / RTO 4h
- n8n Runtime: rebuildable / RTO 4h
- Cockpit: redeployable / RTO 4h
- Notion Projection: RTO 24h acceptable
- HF/Quant Compute: recomputable / RTO 24h

Recovery order:

`Reality → Runtime → Read Models → Projection`

## 23. Team Operating Rhythm

### Daily

**08:00–09:00 Machine Morning Check**

- refresh sources
- detect Δ/Δ²
- evidence integrity
- price refresh
- narrative refresh
- falsifier checks
- scheduled compute
- Today Queue generation

**09:00 Morning Intelligence**

Founder should consume the key brief in approximately 5–10 minutes; researchers in approximately 15 minutes.

**09:15–12:00 Research Window**

Researchers handle P0/P1 Cases.

**14:00–16:00 Evidence Review Window**

Reviewers independently process evidence.

**17:00 Runtime Settlement**

- collect decisions
- run gates
- publish qualified projections
- schedule settlements
- update Cockpit
- project to Notion
- write receipts

### Weekly

`Weekly Reality Review`

Only discuss:

- major Reality Shift
- major Research Upgrade
- major Falsification
- major Learning Delta
- Canon / strategic escalation

The meeting is not a work-status round-robin.

### Monthly

`Research OS Health Review`

Review research integrity, settlement, adoption, learning conversion, runtime health, and founder leverage.

## 24. Product Metrics

### 24.1 North Star 1｜Reality-Settled Research Rate (RSRR)

`RSRR = qualified decision-relevant cases that complete Reality Settlement + Learning Closure on time / due qualified decision-relevant cases`

Day-90 target: `RSRR >= 85%`.

### 24.2 North Star 2｜Decision-Relevant Case Rate (DRCR)

`DRCR = cases that enter Weekly Reality Review or trigger a real research/founder decision / all formally frozen cases`

V1 establishes the baseline rather than fixing an arbitrary target.

### 24.3 Founder Attention Compression Ratio

Measures how many raw signals and routine judgments the Runtime removes from Founder attention while preserving high-leverage strategic uncertainty.

The target is not Founder involvement → 0; the target is Founder Attention → Highest-Leverage Uncertainty.

### 24.4 Health metrics

Monthly health dimensions include:

- Evidence Rejection Rate
- INDETERMINATE Rate
- Gate Downgrade Rate
- Settlement Completion
- Falsifier Hit Rate
- Research Rewrite Rate
- Reviewer Disagreement
- Founder Escalation Rate
- PIT Integrity
- Learning → Capability Conversion

Research output volume is not a North Star metric.

## 25. Adoption Model

Three adoption states:

- `L0｜Record System` — work happens elsewhere and is entered afterward
- `L1｜Workflow System` — research actually happens through YMQ
- `L2｜Thinking System` — the team prefers not to return to the old workflow

Day-90 target: stable L1 adoption with early signs of L2.

The primary adoption failure mode is Shadow Workflow: core research happens in chat/Excel/Notion/meetings, then is manually reconstructed in YMQ.

## 26. 90-Day Launch Plan

### P0｜Day 0–14｜Trust Foundation

Goal: prove the Runtime deserves trust before real team use.

Required capabilities:

- Identity / RBAC
- Event Ledger
- Canonical Mutation API
- seven Workflow Contracts
- deployment / drift control
- observability / incident recovery
- minimum Cockpit skeleton

Day-14 Gate requires:

- Researcher cannot review own Case
- Canonical mutation always includes Event + Receipt
- duplicate request does not create duplicate reality
- workflow rerun is safe
- GitHub-approved workflow can be compared with live n8n
- browser holds no sovereign secret
- n8n loss can be reconciled from Supabase
- Capital / Execution remain DENY

Failure of a critical trust condition = `P0_NO_GO`.

### P1｜Day 15–30｜AI Infrastructure One-Battle Alpha

Users: 3–5  
Target: 8–12 high-quality real Research Cases.

Pressure-test case mix should include Reality Shift, Transmission, Narrative, Price/Payoff, and Hard Negative cases.

Day-30 `G1｜One-Battle Reality Proof` requires:

- ≥8 complete real Cases
- 100% qualified Cases independently Dual-Key reviewed
- 100% canonical mutation receipts
- sampled Cases reconstruct T0
- at least one legitimate LIMITED / INDETERMINATE / BLOCKED state
- at least one fault-recovery drill
- Founder is not routine approver
- actual research work is performed in Cockpit

### P2｜Day 31–60｜Three-Battle Shadow Operations

Add:

- Gold / Global Money
- China Policy / New Manufacturing

Purpose: test transferability across very different research dynamics.

Pressure tests:

- AI Infrastructure → rapid technical change / transmission / valuation
- Gold → long-cycle regime / macro / cross-asset causality
- China → policy text / revisions / historical PIT / China corpus

Day-60 `G2｜Cross-Battle Operating Proof` initial calibration targets:

- canonical mutation with receipt = 100%
- silent authority escalation = 0
- Gate bypass = 0
- T0 reconstruction success ≥95%
- P0/P1 queue processed on time ≥85%
- due settlement completion ≥80%
- qualified cases Dual-Key reviewed = 100%
- Founder routine approval ratio <20%

These are V1 calibration targets and may be refined from observed baseline without weakening sovereignty/integrity laws.

### P3｜Day 61–90｜Founder Team Production

Users: 5–20.

Enter Feature Freeze except for:

- P0/P1 defect
- security/integrity issue
- severe usability blocker

Primary goal: determine whether the team actually lives in the Runtime and whether early 30D settlements create real learning.

## 27. Stage-Gate Verdicts

Day 90 ends with a Reality Settlement, not a demo.

Allowed verdicts:

### SCALE

Use when sovereignty, integrity, adoption, cross-battle transfer, settlement, and Founder leverage all pass.

Eligible next program:

`YMQ-PROD1｜Research → Shadow Capital`

Possible future chain:

`Research Projection → S/C/R/X Mapping → Position Passport → Survival Gate → Zero-Capital Shadow Portfolio`

Still no real broker execution.

### NARROW

Use when the Runtime works only in selected Battles or evidence environments.

Example: keep AI + Gold production while China enters a separate Evidence Remediation program.

### REFRAME

Use when technical integrity is strong but the work-unit or UX hypothesis is wrong.

Example: if full ResearchCase creation is too heavy for ordinary signals, introduce `Signal → Watch Item → threshold → ResearchCase` rather than forcing every signal into a formal Case.

### KILL

Use when complexity cost exceeds capability gain.

Kill signals include:

- the team still performs core research elsewhere and backfills YMQ after the fact
- most formal Cases have low decision relevance
- Dual-Key becomes governance theater
- T0 cannot be reliably reconstructed
- Settlement remains <50%
- workflow burden grows without improved decision quality/speed
- Founder becomes a bigger approval bottleneck

A SEV-0 event freezes affected sovereignty paths and requires requalification; it does not automatically mean the entire product is killed.

## 28. Production Laws

### Product Laws

- `PL-01｜Cockpit is an Attention Router, not a data dashboard.`
- `PL-02｜Research Case is the primary unit of work.`
- `PL-03｜Evidence review remains independently authoritative from thesis creation.`
- `PL-04｜Founder handles escalation, not routine approval.`
- `PL-05｜Every qualified belief must eventually face Reality Settlement.`

### Data Laws

- `DL-01｜History is append-only.`
- `DL-02｜Every mutation is idempotent.`
- `DL-03｜Domain Object + Event + Receipt commit atomically.`
- `DL-04｜n8n orchestrates; Supabase authorizes state transitions.`
- `DL-05｜Runtime is disposable; Reality is durable.`
- `DL-06｜Every qualified belief is replayable from T0.`

### Production Security Laws

- `PL-SEC-01｜No human or machine receives more authority than the capability requires.`
- `PL-SEC-02｜No production secret exists in Canon artifacts.`
- `PL-SEC-03｜No browser client holds sovereign credentials.`
- `PL-SEC-04｜Production change must be bound to an approved Git SHA / contract hash.`
- `PL-SEC-05｜High-authority workflow drift fails closed.`
- `PL-SEC-06｜Integrity outranks availability.`
- `PL-SEC-07｜Runtime may be rebuilt from Reality; Reality may never be rebuilt from Runtime.`
- `PL-SEC-08｜Every sovereignty or truth-integrity incident ends with Reality Settlement and Learning Delta.`

## 29. Completion Criteria

YMQ-PROD0 may be declared operationally qualified only when all of the following have passed in real team use:

- `SOVEREIGNTY_PASS`
- `REALITY_LEDGER_PASS`
- `DUAL_KEY_PASS`
- `THREE_BATTLE_PASS`
- `TEAM_ADOPTION_PASS`
- `SETTLEMENT_PASS`
- `FOUNDER_LEVERAGE_PASS`

Final allowed product qualification state:

`YMQ_PROD0_OPERATIONALLY_QUALIFIED / CAPITAL_NOT_AUTHORIZED / EXECUTION_NOT_AUTHORIZED`

## 30. Design Review Checklist

This spec intentionally contains no production implementation authorization. It defines the accepted product and architectural design only.

Self-review requirements before implementation planning:

- no `TBD` / `TODO` placeholders
- no competing Law or Reality source
- no implicit Capital or Execution authority
- no dependency on n8n transient state for canonical recovery
- no workflow path capable of overriding gate law
- no Notion-as-database behavior
- no browser sovereign credentials
- no mutable historical ResearchCase version
- no automatic Canon rewrite from Learning
- no Big Bang launch assumption

## 31. Next Step After Human Review

After explicit human approval of this Written Spec, invoke `superpowers:writing-plans` and produce a detailed implementation plan that decomposes PROD0 into independently reviewable, test-first work packages with staging and reality gates.
