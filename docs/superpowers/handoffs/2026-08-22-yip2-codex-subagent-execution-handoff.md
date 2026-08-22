# YIP2｜Codex Subagent-Driven Execution Handoff

Status: **READY_FOR_CODEX_SUBAGENT_DRIVEN_EXECUTION**

Repository: `moonstachain/yuanli-invest`

Execution branch: `yip2-portal-2-design-spec`

Accepted design spec:

`docs/superpowers/specs/2026-08-22-yip2-yuanli-investment-portal-2-design.md`

Accepted implementation plan:

`docs/superpowers/plans/2026-08-22-yip2-yuanli-investment-portal-2-implementation.md`

Design acceptance:

`ACCEPT_YIP2_PORTAL_2_0_EXPERIENCE_ARCHITECTURE_DESIGN`

Written spec acceptance:

`ACCEPT_YIP2_PORTAL_2_0_WRITTEN_DESIGN_SPEC`

Execution mode chosen by human:

`A｜SUBAGENT_DRIVEN_YIP2`

---

## 1｜Execution Mandate

Execute the accepted YIP2 implementation plan using **superpowers:subagent-driven-development**.

Required shape:

`14 Tasks → fresh implementer per judgment-bearing task → task review → fix loop as needed → final whole-branch review`

Batch only truly small same-shape mechanical edits where the SDD skill explicitly permits batching.

Do not silently collapse tasks that require distinct judgment or independent verification.

---

## 2｜Binding Authority Order

When anything conflicts, resolve in this order:

1. Accepted Design Spec
2. Accepted Implementation Plan
3. Existing Yuanli Portal Governance
4. Existing Notion live schema / resource reality
5. Implementation convenience

The spec is binding authority. The plan is its implementation argument.

---

## 3｜Global Non-Negotiables

- One Belief: **先问你准备赚什么钱，再问你准备买什么资产。**
- Primary audience: 聪明但混合 Thesis 的企业家投资者.
- Secondary audience: 财富治理型高净值企业家.
- Core identity shift: `Asset Picker → Thesis Architect → Reality Learner`.
- Human Grammar: `势 · 信 · 极｜真 · 价 · 生`.
- `Human Grammar ≠ Machine Ontology`.
- Return engines: `ENG-C / ENG-R / ENG-X`.
- `Asset ≠ Engine`.
- `Cash ≠ Engine`.
- C/R/X are an open-world Genesis Engine Set; do not claim completeness.
- Object grammar: `ResearchTarget → EngineThesis → PositionPassport → BookState@PIT`.
- `Target ≠ Thesis ≠ Position ≠ Book`.
- `Research pass ≠ Capital pass`.
- `No Silent Thesis Migration`.
- Final return: `Survive → Capture → Compound`.
- Notion remains Human Projection only.
- GitHub accepted Canon remains upstream authority.
- Do not create Canon, ontology, schema, portfolio sizing, trading, live execution, or public-publish authority.
- Reuse existing Projection Lifecycle; do not invent a YIP2-specific state machine.
- ME2–ME5 are not authorized.
- Existing Notion `原力投研` identity and URL must be preserved.
- No Case Lab item may be treated as a current recommendation or live signal.
- Every case requires PIT/as-of context and a Falsifier.
- Build completion does not authorize publishing.

---

## 4｜Required SDD Setup

Before Task 1:

1. Read `superpowers:subagent-driven-development`.
2. Read `superpowers:using-git-worktrees` and create/verify an isolated worktree for this plan.
3. Run the SDD workspace setup for the implementation plan.
4. Create the plan-specific ledger at the path required by the SDD skill.
5. Read the full accepted spec and implementation plan.
6. Perform the required pre-flight cross-task/interface scan and write the table to the ledger.
7. Record rulings for any conflicts before dispatching Task 1.

Never implement directly on `main`.

---

## 5｜Execution Loop

For each task:

1. Record BASE commit.
2. Generate the task brief from the accepted implementation plan.
3. Dispatch a fresh implementer subagent with the brief as the requirements source.
4. Implement, verify, self-review, and commit.
5. Generate a task review package.
6. Dispatch a task reviewer for both spec compliance and quality.
7. If findings exist, run the SDD fix loop and scoped re-review.
8. Record the final ruling / completion in the ledger.
9. Continue automatically to the next task.

Do not pause for routine human confirmation between tasks.

---

## 6｜Named Stop Conditions

Stop only when required by SDD or by this project’s governance. In particular, stop before:

- destructive/irreversible Notion operations;
- public publishing;
- merging/pushing to a shared protected branch when a human authorization is required;
- changing GitHub Canon or accepted semantics;
- authorizing or implementing ME2–ME5;
- turning research output into portfolio/trading authority;
- any action that would delete existing child pages or databases unless explicitly human-approved;
- a plan failure so severe that every path forward is guesswork.

For ordinary ambiguity, make a ruling, record it in the ledger, and continue.

---

## 7｜Notion-Specific Execution Rules

- Fetch and inspect live Notion schema before writing database properties.
- Preserve the existing `原力投研` page identity/URL.
- Prefer targeted edits where safe; do not replace content in a way that accidentally deletes child pages/databases.
- Reuse existing Portal governance:
  - `Portal Authority Constitution v1.0`
  - `Projection Lifecycle v1.0`
  - `Naming Standard v1.0`
  - `Change Log`
- Keep Portal state PRIVATE / NOT PUBLISHED unless separately authorized.
- Provenance fields must be populated only using the live schema and valid existing options.
- Do not invent a new enum or schema unless separately designed and approved.

---

## 8｜Human Review / Reality Boundaries

The implementation plan may build the Portal and prepare the Human Review surface, but must not claim Reality acceptance without real-user evidence.

Required design-level review target:

`YIP2 Human Review = 10/10 PASS`

Opening Day / Live Trial remains a separate Reality Gate.

Do not treat user praise as behavioral evidence.

Do not treat build completion as publish authorization.

---

## 9｜Final Review

After all 14 tasks are complete:

1. Dispatch a broad final reviewer on the most capable available model.
2. Check the whole implementation against the accepted spec, not merely task-local success.
3. Run one final fix dispatch + scoped re-review if needed.
4. Adjudicate any residual findings explicitly in the ledger.
5. Verify final state with fresh evidence.
6. Use `superpowers:finishing-a-development-branch`.

The final execution report must include:

- task-by-task completion status;
- exact Notion resources created/modified;
- exact provenance/state changes;
- review findings and their disposition;
- outstanding Human/Reality gates;
- confirmation that no Canon, ME2–ME5, trading, or public-publish authority was created.

---

## 10｜Codex Start Prompt

Use the following as the controller instruction after opening the repository in Codex:

> Execute YIP2 in `moonstachain/yuanli-invest` using Subagent-Driven Development. Work from branch `yip2-portal-2-design-spec`. Read `docs/superpowers/handoffs/2026-08-22-yip2-codex-subagent-execution-handoff.md` first, then the accepted design spec and implementation plan it references. Use `superpowers:subagent-driven-development` exactly: isolated worktree, plan ledger, pre-flight scan, fresh implementer per judgment-bearing task, task reviewer, fix loop, final whole-branch review. Execute all 14 tasks continuously. Do not publish, merge to protected main, mutate Canon, authorize ME2–ME5, create trading/portfolio authority, or perform destructive Notion operations without the required human gate. Stop only at a named stop condition or after all tasks and final review are complete.
