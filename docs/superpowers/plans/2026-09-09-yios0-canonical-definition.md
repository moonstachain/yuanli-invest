# YIOS0｜Canonical Definition v1.0 Implementation Plan

**Date:** 2026-09-09  
**Repository:** `moonstachain/yuanli-invest`  
**Branch:** `yios0-canonical-definition-design`  
**Design authority:** `docs/superpowers/specs/2026-09-09-yios0-canonical-definition-design.md`  
**Execution mode:** TDD + fail-closed + exact-head GitHub Actions + separate Human Gates

## Goal

Implement the accepted YIOS0 Written Spec as the stable GitHub system-definition/discovery layer for Yuanli Investment OS, then—only after the required GitHub Human Acceptance and merge gates—project the merged Canon one-way into Notion and verify parity.

YIOS0 must never create research, capital, broker, paper-order, live-order, or real-capital authority.

## Non-negotiable invariants

- `Reality > Belief`
- `Every Intelligence Claim Must Carry a Pre-Registered Defeat Condition`
- `ResearchPass != CapitalPass`
- `ResearchAuthority != CapitalAuthority != ExecutionAuthority`
- `ClaimAuthority <= EvidenceAuthority`
- `UNKNOWN = DENY`
- `Receipt = Ledger; Status = Projection`
- `Notion = Human Projection; GitHub = Canon/System Definition Authority`
- `ResearchCredential != CapitalCredential != ExecutionCredential != BrokerCredential`
- architecture version and runtime/status projection remain separate

## Task 1｜Freeze implementation baseline and create Draft PR

**Read:** `HANDOFF.md`, Written Spec, protected `main`, PR #72, accepted upstream receipts.  
**Verify:** `main == e2f06e039dccca45d178ab017654005cdb135666` before implementation; record any drift rather than copying design-time assumptions.  
**PR:** Draft PR from `yios0-canonical-definition-design` to `main`.

## Task 2｜TDD RED: add YIOS0 contract tests first

**Create:** `tests/test_yios0_canonical_definition.py`

Tests must cover:
1. current pointer integrity;
2. required machine-contract blocks and exact mother loop;
3. all four mother laws;
4. authority separation and credential separation;
5. three-axis status semantics;
6. `REALITY_PROVEN` evidence/known-as-of requirements;
7. YMQ4-B3 `SCIENTIFIC_NO_GO` + not-merged gap;
8. no silent promotion of YGR0/YRP1/State Compiler/YAU1/YVN1-A1/VeighNa/Broker Paper/Live;
9. Notion one-way projection / no direct Canon mutation;
10. accepted child constitutions remain untouched.

**Run:** `python -m unittest tests.test_yios0_canonical_definition -v` via repository-gates.  
**Expected RED:** tests fail because YIOS0 implementation artifacts do not yet exist.

## Task 3｜Implement machine architecture contract and stable pointer

**Create:**
- `config/yios0/yios0_architecture.v1.json`
- `config/yios0/yios0_current.json`

Contract required blocks:
`identity, versioning, strategic_positioning, mother_loop, mother_laws, authority_topology, knowledge_spine, action_spine, buses, human_layers, machine_services, experience_plane, deployment_domains, status_semantics, projection_contract, bootstrap_contract, non_authorizations`.

Current pointer must remain lifecycle-neutral and become authoritative only from protected-main presence + accepted Human Receipt + post-merge readback.

## Task 4｜Implement human Canon and discovery artifacts

**Create:**
- `docs/architecture/yios0/YIOS0-CANONICAL-ARCHITECTURE-v1.0.md`
- `docs/architecture/yios0/YIOS0-CURRENT.md`
- `docs/architecture/yios0/YIOS0-CHANGELOG.md`

Freeze the accepted 12-layer human architecture, 8 machine services, two spines, three buses, deployment domains, Experience Plane roles, version law, and explicit non-authorizations.

## Task 5｜Materialize dynamic Status Matrix from current evidence

**Create:** `docs/architecture/yios0/YIOS0-STATUS-MATRIX.md`

Every row carries:
`status_known_as_of | authority_state | reality_state | runtime_state | evidence_ref | open_authority_gap`.

Required negative evidence: YMQ4-B3 remains `SCIENTIFIC_NO_GO` and PR #72 open/draft/not merged. No roadmap state may be promoted into current Reality.

## Task 6｜Implement Notion Projection Contract

**Create:** `docs/architecture/yios0/YIOS0-NOTION-PROJECTION-CONTRACT-v1.0.md`

Freeze:
`GitHub Canon → Projection Contract → Notion Human Projection`.

Target child page under existing `原力投研` registry row: `原力投研 OS｜最新版定义`.

No Domain Registry schema changes. Reverse edits may only become review requests/issues/battles/PR candidates.

## Task 7｜Implement fail-closed validator

**Create:** `scripts/validate_yios0_canonical_definition.py`

Validator must enforce all 18 fail-closed conditions in the Written Spec using repository-local facts only; CI performs no GitHub/Notion network reads.

## Task 8｜Wire validator into protected repository-gates

**Update:** `.github/workflows/ci.yml`

Add `python scripts/validate_yios0_canonical_definition.py` to `contracts` before repository-wide unittest discovery.

Do not change the required `contracts` / `governance` job identities.

## Task 9｜Reach GREEN and exact-head machine qualification

**Run through PR Actions:**
- YIOS0 validator PASS
- `contracts` PASS
- `governance` PASS
- full unittest discovery PASS

Record exact head SHA and workflow run ID/number. Re-read PR #72 and protected main at qualification time.

## Task 10｜Create machine qualification receipt and Human Review Card

**Create:**
- `docs/architecture/yios0/YIOS0-MACHINE-QUALIFICATION-RECEIPT-v1.0.md`
- `docs/architecture/yios0/YIOS0-HUMAN-REVIEW-CARD-v1.0.md`

Receipt binds candidate SHA, exact-head CI, validator, contracts/governance, scope audit and live readback time. Human Review Card explicitly preserves all non-authorizations.

Run exact-head CI again after receipt/card commit if repository manifest/gates require it.

## Task 11｜G2: GitHub Canon Human Acceptance

**Required independent Human token:** `ACCEPT_YIOS0_CANONICAL_DEFINITION`

Only after it is received, create:
`docs/architecture/yios0/YIOS0-HUMAN-ACCEPTANCE-RECEIPT-v1.0.json`

Receipt binds the reviewed machine-qualified head/run and records `AUTHORIZE_YIOS0_MERGE` as the separate next token. Acceptance does not authorize merge.

## Task 12｜Post-acceptance exact-head CI

Run repository-gates on the Human Acceptance Receipt head. Require `contracts=success`, `governance=success`, validator PASS and full unit tests PASS.

## Task 13｜G3: protected-main merge

**Required independent Human token:** `AUTHORIZE_YIOS0_MERGE`

Only then mark PR ready if needed and merge through protected-main rules with expected head SHA. No bypass of required checks.

## Task 14｜Post-merge GitHub Reality readback

Read protected `main` after merge and prove:
- merged YIOS0 files exist on `main`;
- `YIOS0-CURRENT` and machine pointer resolve v1.0 consistently;
- accepted Human Receipt is present;
- main SHA is the merged revision;
- YVN1-A1/VeighNa/Broker Paper/Live remain unauthorized.

This readback, not a self-declared pointer field, establishes current Canon reality.

## Task 15｜Build Notion Human Projection from merged Canon only

Read the existing Notion `原力投研` registry row and current schema. Create child page:
`原力投研 OS｜最新版定义`.

Progressive-disclosure content:
1. human definition;
2. current version card;
3. objective;
4. four mother laws;
5. mother loop;
6. two spines;
7. three buses;
8. 12 layers;
9. 8 services;
10. current Reality Status;
11. deep links;
12. return path.

Update existing Registry fields only:
- Canon URI → stable GitHub `YIOS0-CURRENT.md` URL
- Canon Revision → `YIOS0 v1.0 @ <merged-sha>`
- Source Authority → `MULTI_CANON`
- Projection State → `human_review`
- Last Reviewed → actual date

## Task 16｜Cross-system parity readback

Read back GitHub protected main and Notion. Compare:
`Canon System ID, Architecture Version, Canon URI, Canon Commit SHA, Status Known As Of, Last Synced At, Projection State, Projection Verification State`.

Any mismatch leaves projection `human_review/stale`, never silently current.

## Task 17｜G4: Notion Projection Human Acceptance

**Required independent Human token:** `ACCEPT_YIOS0_NOTION_PROJECTION`

Only after token and parity PASS may projection move to `published` / finite verification (default expiry 90 days).

## Task 18｜Final closure receipt in PR discussion / readback

Final statement must distinguish:
- Architecture authority
- Reality status
- Runtime/deployment status
- GitHub merge state
- Notion projection state
- all downstream non-authorizations

No completion claim without fresh verification evidence.
