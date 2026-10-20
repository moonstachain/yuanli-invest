# XC0-A Political-Economy Constraint × Cross-Asset Transmission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the machine-auditable staging architecture for XC0-A profiles while preserving Yuanli Research OS authority boundaries and QXM1/QXM2 isolation.

**Architecture:** XC0-A is implemented as a profile layer attached to existing ResearchCapability identities. It does not create a new ontology, registry authority, trading authority, or replacement Financial Mechanics framework. Runtime objects such as ShockPacket and TransmissionEdge remain staging research objects.

**Tech Stack:** Existing yuanli-invest repository conventions, JSON schemas, Python validators/tests, GitHub CI repository-gates workflow.

**Spec:** `docs/superpowers/specs/2026-08-21-xc0-a-political-economy-cross-asset-transmission-design.md`

## Global Constraints

- Preserve `one_core_three_worlds_three_gates_one_loop`.
- Preserve `P = P.capital + P.asset`; XC0 must not create a fourth human world.
- Preserve `X := (Xs, Xa, Xp)` semantics.
- Preserve `Claim Authority <= Evidence Authority`.
- No Registry admission, benchmark authority, production runtime, portfolio output, or trading authority.
- No mutation of QXM1/QXM2 artifacts.

---

### Task 1: Create XC0-A architecture artifact structure

**Files:**
- Create: `docs/architecture/xc0_a/XC0-A-ARCHITECTURE-PROFILE-FREEZE-v0.1.md`
- Create: `docs/architecture/xc0_a/XC0-A-ISOLATION-MATRIX-v0.1.json`

- [ ] Write failing validation expectations for required XC0 artifact presence.
- [ ] Run validator test and confirm missing-artifact failure.
- [ ] Create architecture documents derived only from accepted XC0-A design.
- [ ] Run artifact validation and confirm pass.

### Task 2: Define XC0 staging object schemas

**Files:**
- Create: `docs/architecture/xc0_a/XC0-A-SHOCK-PACKET-SCHEMA-v0.1.json`
- Create: `docs/architecture/xc0_a/XC0-A-TRANSMISSION-EDGE-SCHEMA-v0.1.json`

- [ ] Add schema tests covering required fields, PIT cutoff, evidence references and falsifier fields.
- [ ] Confirm invalid objects fail validation.
- [ ] Confirm valid objects pass validation.

### Task 3: Compile six XC profile contracts

**Files:**
- Create: `docs/architecture/xc0_a/XC0-A-PROFILE-CONTRACTS-v0.1.json`

- [ ] Define six profile identities only.
- [ ] Bind each profile to its parent capability.
- [ ] Add explicit authority ceiling inheritance.
- [ ] Validate that no profile creates independent Canon authority.

### Task 4: Add XC0-A validator gates

**Files:**
- Create or modify: existing repository validator location following current conventions.
- Test: repository-gates tests.

- [ ] Add tests preventing QXM1/QXM2 mutation references.
- [ ] Add tests preventing registry/canon writes from XC0-A scope.
- [ ] Add tests preventing trading-output semantics.
- [ ] Run repository-gates locally.

### Task 5: Human review package and CI closure

**Files:**
- Create: `docs/architecture/xc0_a/XC0-A-HUMAN-REVIEW-CARD-v0.1.md`
- Create: `docs/architecture/xc0_a/XC0-A-STATE.json`

- [ ] Record design acceptance receipt.
- [ ] Record validation head SHA.
- [ ] Run exact-head CI.
- [ ] Prepare review package without merge authorization.
