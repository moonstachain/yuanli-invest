# YIOS-TG1｜Capital Decision Cockpit｜PRD v0.1

Status: PRD_CANDIDATE × PROTOTYPE_IN_PROGRESS
Authority: SHADOW_ONLY
Production: NOT_AUTHORIZED
Live Capital: NOT_AUTHORIZED
Known As Of: 2026-09-22

## 1. Product definition

YIOS-TG1 is the capital-decision product layer of Yuanli Invest OS. It compiles governed Reality / Evidence / PIT / Research State into an explicit, falsifiable and settleable Decision Candidate, then uses Shadow Settlement and Learning Recall to improve future decisions.

North star:
Lifetime Right-Tail Capture under Survival Constraints.

Product promise:
In under three minutes, a principal can understand the current Gold decision state, why it is or is not changing, what would trigger action, what would falsify the thesis, and when the claim will be settled.

## 2. Target user

P0: RAY / Principal as internal alpha.
P1: seed entrepreneur users with meaningful personal/business capital allocation needs.
P2: research / concierge operator for evidence-health and learning review.

## 3. Jobs to be done

1. Do I need to reconsider today?
2. What is the current decision state?
3. Why?
4. What must happen before action?
5. What would prove the thesis wrong?
6. How did the past decision settle?
7. Did the system learn and change a future decision?

## 4. Product principles

- Reality First
- Claim Authority <= Evidence Authority
- UNKNOWN = DENY
- Research != Capital != Execution
- WAIT is a valid product outcome
- Every important claim must be defeatable
- Never rewrite T0

## 5. Phase-1 scope

Genesis case: Gold.

Included:
- Gold Reality State
- Gold Driver State
- Decision Candidate
- Evidence Audit
- Shadow Admission
- Claim
- Settlement
- Learning Candidate
- Pre-Action Recall Preview
- Today Cockpit

Explicit non-goals:
- Broker connection
- Live trading
- Real capital movement
- Automatic position sizing
- Automatic order generation
- Portfolio optimizer
- High-frequency terminal
- Generic market news feed
- Social/community

## 6. Information architecture

Primary navigation:
1. Today
2. Gold
3. Decision
4. Audit
5. Shadow
6. Learning

The six pages are six projections of one governed decision object, not six separate systems.

## 7. Page requirements

### Today
Must answer:
- System health
- Current decision
- What changed (Delta / Delta2)
- Gold snapshot
- Open claims
- What needs attention

### Gold
Must show driver state rather than a scalar score:
- Opportunity Cost / real yield
- USD / monetary credibility
- Structural demand
- Modifiers: stress / crowding / price context
- Dominant driver
- conflicting drivers
- unknowns
- current regime

### Decision
Primary page.
Allowed states:
WAIT / PROBE / HOLD / REDUCE / HEDGE

Each DecisionCandidate must expose:
- Decision State
- Dominant Driver
- Why Now
- Supporting Evidence
- Contradicting Evidence
- Unknowns
- Trigger
- Falsifier
- Survival Boundary
- Expected Horizon
- Settlement Plan
- Authority

### Audit
Must expose:
- source
- value / unit
- observation_at
- released_at
- retrieved_at
- available_at
- vintage
- known_as_of
- provider
- evidence authority
- hard negative
- unknowns
- source conflicts
- data health

### Shadow
DecisionCandidate does not auto-enter Shadow.
Admission = ADMIT / DENY.
Shadow PositionPassport records decision lineage without moving real capital.

### Learning
Settlement states:
OPEN / SUPPORTED / FALSIFIED / UNRESOLVED / RED_ALERT / NOT_SCORABLE.

Flow:
Settlement -> Learning Candidate -> Human Review -> ACCEPT / REJECT / REVISE -> Accepted Learning -> GBrain -> Future Pre-Action Recall.

## 8. Core object model

### DecisionCandidate
decision_id
asset
question
known_as_of
research_state_ref
decision_state
dominant_driver
supporting_evidence
contradicting_evidence
unknowns
trigger
falsifier
survival_boundary
expected_horizon
settlement_rule
authority_state
created_at
version

Other governed objects:
Evidence
PITObservation
ResearchState
Claim
ShadowPositionPassport
Settlement
LearningDelta

## 9. Main user flow

Today
-> Gold
-> Decision
-> Audit
-> WAIT exit OR Shadow Admission
-> Frozen Claim
-> Settlement
-> Learning
-> Future Pre-Action Recall

## 10. Runtime operating model

Daily:
Provider Read -> Normalize PIT -> Data Health -> Research State -> Product Snapshot -> Decision Re-evaluation -> Today Projection.

Weekly:
Six-question review:
1. What materially changed?
2. Did dominant driver change?
3. Did Decision State change?
4. Which Unknowns resolved?
5. Which claims approach settlement?
6. Any Learning Candidate?

Monthly:
Review WAIT ratio, decision changes, evidence freshness, unknown aging, falsifier discipline, settlement coverage and learning reuse.

## 11. Exception states

Must be designed:
HEALTHY
STALE
DEGRADED
MISSING
SOURCE_CONFLICT
UNKNOWN
WAIT
PROBE
OPEN CLAIM
SETTLEMENT

Provider failure must not silently carry forward stale facts as new facts.

## 12. API boundary

Frontend must not access database directly.

Read APIs:
GET /api/invest/gold/state
GET /api/invest/gold/evidence
GET /api/invest/gold/data-health
GET /api/invest/gold/decision
GET /api/invest/gold/audit
GET /api/invest/gold/shadow
GET /api/invest/gold/settlements

Controlled writes:
POST /shadow/admission
POST /learning/review

## 13. Authority

GitHub: Canon / Contract / Schema / Gate / Version.
Supabase: Runtime Reality / PIT / State / Settlement.
GBrain: Learning retrieval / pre-action recall.
Notion: Human Projection only.
Yuanli OS: Identity / Personal Node / Authorization / Product Gateway / Web/PWA/MCP.

Roles:
VIEWER
PRINCIPAL
RESEARCH_OPERATOR
SYSTEM

Hard boundary:
Research Authority != Capital Authority != Execution Authority.

## 14. Prototype acceptance

Prototype must prove:
- 30-second comprehension
- Decision visibility
- Trigger visibility
- Falsifier visibility
- Unknown visibility
- Authority clarity
- Shadow clarity
- Settlement clarity
- Learning clarity
- Navigation simplicity

Required clickable scenarios:
A. Normal WAIT
B. PROBE candidate
C. DEGRADED provider
D. Settlement
E. Learning Recall

## 15. Gold frozen claim

Claim:
claim-20261016-gold-v01

Settlement date:
2026-10-16

Prototype renders but must not modify frozen criteria:
- Gold >= 4470 -> FALSIFICATION CONDITION
- Gold < 4130 -> SUPPORT CONDITION
- 4130-4470 -> UNRESOLVED
- Real Yield > 2.75% AND Gold >= 4470 -> RED_ALERT

## 16. Product gates

P0 PRD Review
P1 Low-Fi Prototype
P2 Clickable Prototype
P3 Blind UX Test
P4 High-Fi UI
P5 Interactive UI Test
P6 Engineering Contract Freeze
P7 Backend Integration
P8 Internal Alpha
P9 Learning Proof
P10 Seed Alpha

Engineering cannot begin until:
PRD_ACCEPTED
× PROTOTYPE_ACCEPTED
× UX_FLOW_ACCEPTED
× UI_CORE_ACCEPTED
× API_CONTRACT_READY
× AUTHORITY_BOUNDARY_ACCEPTED

## 17. Current reality alignment

G1 Core Reality Sink: PASS
G1R Machine Gateway: ACTIVATED
G2A0: ENGINEERING READY
Runtime Authority: SHADOW_ONLY
Production: NOT AUTHORIZED
Live Capital: NOT AUTHORIZED

## 18. Prototype handoff

Figma low-fi:
https://www.figma.com/design/YkP5ooZxDpEP4n3w7uTVSA

Prototype package:
itp-2f5b9fdae138

Next legal product action:
YIOS-TG1-PROT0｜Capital Decision Cockpit × Low-Fi Review × Clickable Flow
