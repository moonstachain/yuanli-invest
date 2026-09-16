# YOS-FIN1-G0 Three-Source Reality Proof Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and machine-qualify a provider-neutral three-source finance routing and corroboration proof for Wind, MiaoXiang, and iWenCai.

**Architecture:** Keep canonical semantics provider-independent. Provider adapters emit sanitized receipts; a router selects providers by request class; a comparator distinguishes independent corroboration from semantic/PIT mismatch; all outputs remain research-only.

**Tech Stack:** Python 3.11, pytest/unittest, JSON contracts, existing Yuanli provider-neutral schemas, local CLI/HTTP subprocess adapters.

**Spec:** `docs/superpowers/specs/2026-09-17-yos-fin1-g0-three-source-reality-proof-design.md`

## Global Constraints
- No secrets or raw authenticated bodies in Git.
- No silent fallback to model knowledge.
- No provider may grant capital/sizing/execution/Canon authority.
- iWenCai screening is research-candidate only.
- Cross-provider corroboration requires distinct provider roots.
- Live probes are bounded and read-only.

---

### Task 1: Freeze FIN1 source contract
**Files:** Create `config/yos_fin1/fin1_source_contract.v0.1.json`; create `tests/test_yos_fin1_contract.py`.
**Produces:** `load_contract()` / `validate_contract()` invariants consumed by all later tasks.
- [ ] Write failing tests for provider roles, hard-false action authority, anti-echo roots, and required failure taxonomy.
- [ ] Run `python -m pytest tests/test_yos_fin1_contract.py -q` and observe RED.
- [ ] Add contract + validator.
- [ ] Re-run and observe GREEN.
- [ ] Commit.

### Task 2: Implement normalized provider receipt + comparator
**Files:** Create `scripts/yos_fin1_core.py`; create `tests/test_yos_fin1_core.py`.
**Produces:** `normalize_receipt()`, `compare_provider_receipts()`, `route_request()`.
- [ ] Write tests for distinct evidence roots, same-provider anti-echo, PIT mismatch, semantic mismatch, and router T0/T1/T2-like decisions.
- [ ] Run targeted tests RED.
- [ ] Implement minimal deterministic core.
- [ ] Run targeted tests GREEN.
- [ ] Commit.

### Task 3: Implement Wind adapter
**Files:** Create `scripts/yos_fin1_wind.py`; create `tests/test_yos_fin1_wind.py`.
**Produces:** read-only Wind adapter using existing local Wind MCP CLI; never prints key or raw auth.
- [ ] Write parser/error-classification tests including backend credit/key failure and schema drift.
- [ ] Run RED.
- [ ] Implement adapter using subprocess + JSON normalization.
- [ ] Run GREEN.
- [ ] Run one bounded live read-only probe and save sanitized receipt outside Git/raw body.
- [ ] Commit.

### Task 4: Implement MiaoXiang adapter
**Files:** Create `scripts/yos_fin1_miaoxiang.py`; create `tests/test_yos_fin1_miaoxiang.py`.
**Produces:** credential discovery + endpoint contract abstraction supporting official/observed MiaoXiang data APIs without hardcoding secrets.
- [ ] Write tests for `MX_APIKEY` discovery, auth-missing fail-closed, endpoint version mapping, provenance and PIT requirements.
- [ ] Run RED.
- [ ] Implement adapter with injectable HTTP transport and endpoint map.
- [ ] Run GREEN.
- [ ] If credential exists, run bounded macro/equity probes; otherwise emit Human Gate `MIAOXIANG_CREDENTIAL_REQUIRED`.
- [ ] Commit.

### Task 5: Implement iWenCai adapter
**Files:** Create `scripts/yos_fin1_wencai.py`; create `tests/test_yos_fin1_wencai.py`.
**Produces:** official/open API path when `IWENCAI_API_KEY` exists; optional browser/CLI discovery path explicitly downgraded to `DISCOVERY_ONLY`.
- [ ] Write tests for official vs browser authority, natural-language screen output, credential absence, and no evidence promotion.
- [ ] Run RED.
- [ ] Implement adapter with official API path + optional local CLI discovery detector.
- [ ] Run GREEN.
- [ ] If official credential exists, run bounded query; otherwise optionally run discovery-only CLI if already installed, without installing hidden automation.
- [ ] Commit.

### Task 6: Run three G0 probes and compile qualification receipt
**Files:** Create `scripts/yos_fin1_probe.py`; create `tests/test_yos_fin1_probe.py`; create `docs/architecture/yos_fin1/YOS-FIN1-G0-MACHINE-QUALIFICATION-RECEIPT-v0.1.md`.
**Produces:** Probe A/B/C status with explicit PASS / FAIL_CLOSED / HUMAN_GATE and no fabricated completion.
- [ ] Pre-register probe fixtures and expected authority boundaries.
- [ ] Run unit tests RED then GREEN.
- [ ] Execute bounded real probes using available credentials.
- [ ] Save only sanitized receipts/hashes.
- [ ] Document missing credentials/provider blockers precisely.
- [ ] Commit.

### Task 7: Repository verification and Human Gate
**Files:** Create `docs/architecture/yos_fin1/YOS-FIN1-G0-HUMAN-REVIEW-CARD-v0.1.md`.
- [ ] Run all FIN1 tests.
- [ ] Run full repository tests.
- [ ] Run `git diff --check`.
- [ ] Run changed-file secret scan.
- [ ] Push branch and create Draft PR.
- [ ] Stop before production scheduler, Canon promotion, or any capital/execution authority.
