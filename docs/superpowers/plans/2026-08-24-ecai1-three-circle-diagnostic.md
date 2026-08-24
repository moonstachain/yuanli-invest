# ECAI1 Three-Circle Diagnostic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the accepted ECAI1 v0.1 diagnostic as a deterministic, fail-closed contract system that converts the 36-question entrepreneur diagnostic into versioned three-circle profiles, conflict flags, Force Investment Domain classifications, C/R/X fit, and an 8-section Capital Constitution report without producing security recommendations or capital-allocation authority.

**Architecture:** Keep the human front-end simple (`信念 × 精专 × 凸性 = 原力投资域`) while implementing machine-readable contracts under a dedicated `ecai1` schema namespace. Questionnaire data, scoring/interpretation rules, fictional Gold fixtures, hard-negative fixtures, and human projections live under `docs/architecture/ecai1` and `docs/human-projection`; deterministic interpretation and fail-closed validation live in `scripts/`. Existing ME0/ME1 ontology is read-only and referenced by stable engine IDs only.

**Tech Stack:** Python 3.12 standard library, `jsonschema==4.25.1`, JSON Schema draft 2020-12, `unittest`, Markdown/JSON fixtures, GitHub Actions existing `repository-gates` workflow.

**Spec:** `docs/superpowers/specs/2026-08-24-ecai1-three-circle-diagnostic-design.md`

## Global Constraints

- Human grammar remains exactly `信念 × 精专 × 凸性 = 原力投资域`.
- `Capital Context` is a constraint layer and must never become a fourth circle.
- Questionnaire remains exactly 36 scored/diagnostic questions: 6 Capital Context + 8 Conviction + 8 Specialization + 8 Asymmetry + 6 Scenario Consistency.
- No exact net-worth field is required in v0.1; capital questions use intervals or categorical context.
- No global pseudo-scientific personality or investment-ability score may be emitted.
- Allowed profile labels are `strong`, `mature`, `developing`, `weak`, `conflicted`, `unknown`.
- Allowed Force Investment Domain actions are `OWN`, `DELEGATE`, `EXPLORE`, `AVOID`, `WATCH`; these are research/governance classifications, never capital authorization.
- Allowed engine-fit outputs are `primary_fit`, `secondary_fit`, `learning_only`, `delegate_preferred`, `not_fit_currently`, `unknown`.
- Engine identities consumed from ME0 are only `ENG-C`, `ENG-R`, `ENG-X`; ECAI1 must not mutate ME0/ME1 schemas or accepted artifacts.
- Human-facing `Asymmetry` is opportunity-asymmetry recognition/preference and must not be equated with `ENG-X｜Convexity`.
- `PersonalConviction != MarketBelief != EvidenceAuthority`.
- `Profile != Prescription`; fit never grants buy/sell/size/manager-approval authority.
- `No Source → No Personalized Claim`: every personalized report claim must cite one or more question IDs or explicit domain-evidence IDs.
- Scenario consistency and contradiction flags override polished self-description when the two conflict.
- Force Investment Domain generation may only use user-supplied domain evidence; if domain evidence is absent, output `unknown` rather than inventing expertise.
- Profile history is PIT/versioned: new review creates a new profile version and never rewrites prior states.
- Recommendation leakage is fail-closed: generated Gold reports must reject security-specific buy/sell/weight/target-price/return-guarantee language.
- Implementation scope excludes live portfolio sizing, security recommendations, trade execution, manager approval/fund-selection authority, ME0/ME1 ontology mutation, and automatic capital movement.

---

## File Structure

Create or modify the following focused files:

```text
packages/contracts/schemas/ecai1/
  questionnaire-response.schema.json      # raw questionnaire + optional domain evidence
  entrepreneur-capital-profile.schema.json # interpreted PIT profile
  capital-constitution-report.schema.json  # structured 8-section report + provenance

docs/architecture/ecai1/
  ECAI1-GOLD-DIAGNOSTIC-v0.1.json          # canonical 36-question bank
  ECAI1-PROFILE-RULES-v0.1.json            # deterministic thresholds, scenario semantics, conflicts
  ECAI1-ENGINE-FIT-RULES-v0.1.json         # ENG-C/R/X fit rules
  ECAI1-STATE.json                         # candidate lifecycle + authority boundary
  ECAI1-HUMAN-REVIEW-CARD-v0.1.md          # post-implementation Human Gate
  fixtures/
    gold-chen-response.json                # fictional response + domain evidence
    gold-chen-profile.json                 # expected interpreted profile
    gold-chen-report.json                  # expected structured report
    hard-negatives.json                    # anti-pattern fixture pack

docs/human-projection/
  ECAI1-ENTREPRENEUR-THREE-CIRCLE-DIAGNOSTIC-v0.1.md
  ECAI1-GOLD-SAMPLE-REPORT-v0.1.md
scripts/
  ecai1_diagnostic.py                      # deterministic interpreter library
  validate_ecai1_three_circle_diagnostic.py # fail-closed repository/fixture validator

tests/
  test_ecai1_three_circle_diagnostic.py
.github/workflows/ci.yml                   # add ECAI1 validator command
```

No production API endpoint or user database is added in v0.1.

---

### Task 1: Freeze the Machine Contracts and Canonical 36-Question Bank

**Files:**
- Create: `packages/contracts/schemas/ecai1/questionnaire-response.schema.json`
- Create: `packages/contracts/schemas/ecai1/entrepreneur-capital-profile.schema.json`
- Create: `packages/contracts/schemas/ecai1/capital-constitution-report.schema.json`
- Create: `docs/architecture/ecai1/ECAI1-GOLD-DIAGNOSTIC-v0.1.json`
- Create: `tests/test_ecai1_three_circle_diagnostic.py`

**Interfaces:**
- Consumes: accepted Written Spec section 3–8 question IDs and section semantics.
- Produces: schema IDs `urn:yuanli-invest:schema:ecai1-questionnaire-response:1.0.0`, `urn:yuanli-invest:schema:ecai1-entrepreneur-capital-profile:1.0.0`, `urn:yuanli-invest:schema:ecai1-capital-constitution-report:1.0.0`; canonical question bank with exactly 36 unique question IDs.

- [ ] **Step 1: Write failing contract tests for section counts, IDs, and schema authority**

Add tests with these assertions:

```python
class ECAI1QuestionBankTests(unittest.TestCase):
    def test_question_bank_has_exact_genesis_counts(self):
        bank = load_json(QUESTION_BANK)
        counts = Counter(q["section"] for q in bank["questions"])
        self.assertEqual(len(bank["questions"]), 36)
        self.assertEqual(counts, {
            "capital_context": 6,
            "conviction": 8,
            "specialization": 8,
            "asymmetry": 8,
            "scenario": 6,
        })

    def test_question_ids_are_unique_and_complete(self):
        bank = load_json(QUESTION_BANK)
        ids = [q["question_id"] for q in bank["questions"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {
            *(f"CC-{i:02d}" for i in range(1, 7)),
            *(f"CV-{i:02d}" for i in range(1, 9)),
            *(f"SP-{i:02d}" for i in range(1, 9)),
            *(f"AS-{i:02d}" for i in range(1, 9)),
            *(f"SC-{i:02d}" for i in range(1, 7)),
        })

    def test_capital_context_does_not_require_exact_net_worth(self):
        text = QUESTION_BANK.read_text(encoding="utf-8")
        self.assertNotIn('"exact_net_worth"', text)
        self.assertNotIn('"net_worth_amount"', text)

    def test_profile_schema_has_zero_capital_authority(self):
        schema = load_json(PROFILE_SCHEMA)
        authority = schema["properties"]["authority"]["properties"]
        self.assertEqual(authority["portfolio_weight_authority"]["const"], False)
        self.assertEqual(authority["trade_execution_authority"]["const"], False)
        self.assertEqual(authority["manager_approval_authority"]["const"], False)
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```bash
python -m unittest tests.test_ecai1_three_circle_diagnostic -v
```

Expected: FAIL because ECAI1 schemas and question bank do not exist.

- [ ] **Step 3: Create the three JSON Schemas**

Use JSON Schema draft 2020-12 and `additionalProperties: false` at every stable object boundary. `questionnaire-response.schema.json` must require:

```json
{
  "response_id": "ECAI1-RSP-...",
  "schema_version": "1.0.0",
  "recorded_at": "date-time",
  "known_as_of": "date",
  "answers": {"CC-01": "A", "CV-01": 4},
  "domain_evidence": {
    "personal_priors": [],
    "specialization_domains": [],
    "watch_domains": []
  }
}
```

`domain_evidence` is optional, but Force Investment Domain output must become `unknown` when evidence is absent.

`entrepreneur-capital-profile.schema.json` must include:

```text
profile_id
schema_version
recorded_at
known_as_of
source_response_id
capital_context
conviction_profile
specialization_profile
asymmetry_profile
scenario_consistency
conflict_flags
force_investment_domains
engine_fit
no_go_rules
review_contract
authority
```

`capital-constitution-report.schema.json` must require exactly eight ordered report sections plus `report_claims[]`, where every claim has `claim_id`, `text`, `source_questions`, `source_domain_evidence`, `inference_type`, `confidence`, and `contradiction_flags`.

- [ ] **Step 4: Create the canonical 36-question JSON bank from the accepted spec**

Each question object must contain:

```json
{
  "question_id": "CV-04",
  "section": "conviction",
  "prompt_zh": "对于自己的核心投资信念，我能够明确说出‘什么事实出现，我就承认自己错了’。",
  "response_type": "likert_1_5",
  "semantic_tags": ["falsifiability"],
  "scored": true
}
```

Scenario questions use `response_type: "single_choice"` with the exact A–E (or A–C for SC-03) option text accepted in the spec.

- [ ] **Step 5: Run contract tests and validate all schemas with jsonschema**

Add a schema self-check test:

```python
for path in ECAI1_SCHEMA_DIR.glob("*.schema.json"):
    Draft202012Validator.check_schema(load_json(path))
```

Run:

```bash
python -m unittest tests.test_ecai1_three_circle_diagnostic -v
```

Expected: PASS for Task 1 tests.

- [ ] **Step 6: Commit Task 1**

```bash
git add packages/contracts/schemas/ecai1 docs/architecture/ecai1/ECAI1-GOLD-DIAGNOSTIC-v0.1.json tests/test_ecai1_three_circle_diagnostic.py
git commit -m "ECAI1: add diagnostic contracts and question bank"
```

---

### Task 2: Implement Deterministic Three-Circle Interpretation Without a Global Score

**Files:**
- Create: `docs/architecture/ecai1/ECAI1-PROFILE-RULES-v0.1.json`
- Create: `scripts/ecai1_diagnostic.py`
- Modify: `tests/test_ecai1_three_circle_diagnostic.py`

**Interfaces:**
- Consumes: `QuestionnaireResponse` validated by Task 1.
- Produces: `interpret_response(response: dict, rules: dict) -> dict` returning an `EntrepreneurCapitalProfile`-shaped dictionary.

- [ ] **Step 1: Write failing tests for ordinal circle labels and no global score**

```python
class ECAI1ProfileInterpretationTests(unittest.TestCase):
    def test_interpreter_emits_three_circle_profiles_without_global_score(self):
        response = make_response(default_likert=4)
        profile = ecai1.interpret_response(response, load_json(PROFILE_RULES))
        self.assertIn(profile["conviction_profile"]["level"], ALLOWED_LEVELS)
        self.assertIn(profile["specialization_profile"]["level"], ALLOWED_LEVELS)
        self.assertIn(profile["asymmetry_profile"]["level"], ALLOWED_LEVELS)
        self.assertNotIn("global_score", profile)
        self.assertNotIn("investment_ability_score", profile)

    def test_capital_context_remains_constraint_not_circle(self):
        profile = ecai1.interpret_response(make_response(), load_json(PROFILE_RULES))
        self.assertNotIn("capital_context", profile["circle_levels"])
        self.assertEqual(set(profile["circle_levels"]), {"conviction", "specialization", "asymmetry"})
```

- [ ] **Step 2: Run tests and verify RED**

```bash
python -m unittest tests.test_ecai1_three_circle_diagnostic.ECAI1ProfileInterpretationTests -v
```

Expected: FAIL because interpreter and rules do not exist.

- [ ] **Step 3: Create deterministic profile rules**

Use internal Likert means only for pattern detection. Map each circle to ordinal labels with these v0.1 deterministic thresholds:

```json
{
  "level_thresholds": [
    {"min": 4.25, "level": "strong"},
    {"min": 3.75, "level": "mature"},
    {"min": 3.00, "level": "developing"},
    {"min": 1.00, "level": "weak"}
  ],
  "conflict_override": "conflicted",
  "missing_required_answer": "unknown"
}
```

Store sub-dimension membership exactly as specified in the Written Spec. The numeric means remain internal fields named `diagnostic_signal` and must be excluded from the human-facing report schema.

- [ ] **Step 4: Implement `scripts/ecai1_diagnostic.py` core functions**

Required signatures:

```python
def load_json(path: Path) -> dict: ...
def validate_answer_completeness(response: dict, question_bank: dict) -> None: ...
def mean_likert(response: dict, question_ids: list[str]) -> float: ...
def level_from_signal(signal: float, thresholds: list[dict]) -> str: ...
def build_circle_profile(response: dict, circle: str, rules: dict) -> dict: ...
def interpret_response(response: dict, rules: dict, question_bank: dict | None = None) -> dict: ...
```

`interpret_response` must never infer domain names and must initialize `force_investment_domains` to `[]` or `unknown` pending Task 4.

- [ ] **Step 5: Add missing-answer and invalid-range tests**

```python
def test_missing_required_answer_fails_closed(self):
    response = make_response()
    del response["answers"]["CV-04"]
    with self.assertRaises(ValueError):
        ecai1.interpret_response(response, load_json(PROFILE_RULES), load_json(QUESTION_BANK))

def test_invalid_likert_range_fails_closed(self):
    response = make_response()
    response["answers"]["AS-05"] = 6
    with self.assertRaises(ValueError):
        ecai1.interpret_response(response, load_json(PROFILE_RULES), load_json(QUESTION_BANK))
```

- [ ] **Step 6: Run Task 2 tests and commit**

```bash
python -m unittest tests.test_ecai1_three_circle_diagnostic -v
git add docs/architecture/ecai1/ECAI1-PROFILE-RULES-v0.1.json scripts/ecai1_diagnostic.py tests/test_ecai1_three_circle_diagnostic.py
git commit -m "ECAI1: implement deterministic three-circle profiles"
```

---

### Task 3: Add Scenario Consistency, Bias Detection, and Conflict Flags

**Files:**
- Modify: `docs/architecture/ecai1/ECAI1-PROFILE-RULES-v0.1.json`
- Modify: `scripts/ecai1_diagnostic.py`
- Modify: `tests/test_ecai1_three_circle_diagnostic.py`

**Interfaces:**
- Consumes: raw answers and Task 2 profiles.
- Produces: `evaluate_scenario_consistency(response, rules) -> dict`, `evaluate_conflicts(response, profile, rules) -> list[str]`.

- [ ] **Step 1: Write failing tests for the eight minimum conflict flags**

The tests must cover these exact IDs:

```text
CF-01 HighConviction_LowFalsifiability
CF-02 HighSpecialization_LowFocus
CF-03 HighRightTail_LowLeftTailDiscipline
CF-04 HighRiskPreference_LowCapitalCapacity
CF-05 HighDIYPreference_LowResearchTime
CF-06 DeclaredDiscipline_ScenarioInconsistency
CF-07 EnterpriseBeta_PortfolioBetaOverlap
CF-08 HighBelief_LowEvidenceDiscipline
```

Example:

```python
def test_high_conviction_low_falsifiability_is_conflicted(self):
    r = make_response(default_likert=5)
    r["answers"]["CV-04"] = 1
    r["answers"]["CV-07"] = 1
    p = ecai1.interpret_response(r, rules(), bank())
    self.assertIn("CF-01", ids(p["conflict_flags"]))
    self.assertEqual(p["conviction_profile"]["level"], "conflicted")
```

- [ ] **Step 2: Write failing tests for behavior-over-self-description**

```python
def test_scenario_inconsistency_overrides_declared_discipline(self):
    r = make_response(default_likert=5)
    r["answers"]["SC-02"] = "A"
    r["answers"]["SC-06"] = "A"
    p = ecai1.interpret_response(r, rules(), bank())
    self.assertIn("CF-06", ids(p["conflict_flags"]))
    self.assertEqual(p["scenario_consistency"]["status"], "conflicted")
```

- [ ] **Step 3: Add behaviorally anchored scenario semantics to rules**

Encode scenario options as semantic signals, not a single score. Example:

```json
"SC-02": {
  "A": ["fomo", "competence_boundary_violation"],
  "B": ["fomo", "partial_boundary_violation"],
  "C": ["competence_boundary_respected"],
  "D": ["price_anchoring"],
  "E": ["delegation_without_due_diligence"]
}
```

For SC-03, option C is `contextual_payoff_literacy`; option B is `right_tail_preference` but must not imply ENG-X fit.

- [ ] **Step 4: Implement bias and conflict evaluators**

Required signatures:

```python
def evaluate_scenario_consistency(response: dict, rules: dict) -> dict: ...
def detect_acquiescence_bias(response: dict) -> bool: ...
def evaluate_conflicts(response: dict, profile: dict, rules: dict) -> list[dict]: ...
def apply_conflict_overrides(profile: dict) -> dict: ...
```

`detect_acquiescence_bias` must flag a response when at least 22 of the 24 Likert items are 4 or 5 **and** at least one scenario shows a material contradiction. This is a quality flag, not a diagnosis.

- [ ] **Step 5: Add hard-negative tests for lottery preference and capacity mismatch**

```python
def test_lottery_preference_is_not_asymmetry_strength(self):
    r = make_response(default_likert=4)
    r["answers"].update({"AS-02": 5, "AS-01": 1, "AS-07": 1})
    p = ecai1.interpret_response(r, rules(), bank())
    self.assertIn("CF-03", ids(p["conflict_flags"]))
    self.assertEqual(p["asymmetry_profile"]["level"], "conflicted")

def test_high_risk_preference_cannot_override_low_capacity(self):
    r = make_response(default_likert=4)
    r["answers"].update({"CC-02": "A", "CC-04": "A", "CC-05": "A", "AS-02": 5})
    p = ecai1.interpret_response(r, rules(), bank())
    self.assertIn("CF-04", ids(p["conflict_flags"]))
```

- [ ] **Step 6: Run tests and commit**

```bash
python -m unittest tests.test_ecai1_three_circle_diagnostic -v
git add docs/architecture/ecai1/ECAI1-PROFILE-RULES-v0.1.json scripts/ecai1_diagnostic.py tests/test_ecai1_three_circle_diagnostic.py
git commit -m "ECAI1: add scenario consistency and conflict engine"
```

---

### Task 4: Implement Force Investment Domain Extraction and C/R/X Engine Fit

**Files:**
- Create: `docs/architecture/ecai1/ECAI1-ENGINE-FIT-RULES-v0.1.json`
- Modify: `scripts/ecai1_diagnostic.py`
- Modify: `tests/test_ecai1_three_circle_diagnostic.py`

**Interfaces:**
- Consumes: interpreted three-circle profile, Capital Context, user-supplied `domain_evidence`.
- Produces: `classify_force_domains(profile, domain_evidence, rules) -> list[dict]`; `infer_engine_fit(profile, rules) -> dict`.

- [ ] **Step 1: Write failing tests that prohibit invented domains**

```python
def test_force_domain_is_unknown_without_user_domain_evidence(self):
    r = make_response(default_likert=5)
    r.pop("domain_evidence", None)
    p = ecai1.interpret_response(r, rules(), bank())
    self.assertEqual(p["force_investment_domains"], [])
    self.assertEqual(p["domain_status"], "unknown")

def test_force_domain_only_uses_user_supplied_domain_names(self):
    r = make_response(default_likert=5)
    r["domain_evidence"] = {
        "personal_priors": ["AI adoption"],
        "specialization_domains": ["Enterprise Software"],
        "watch_domains": ["AI Infrastructure"]
    }
    p = ecai1.interpret_response(r, rules(), bank())
    emitted = json.dumps(p["force_investment_domains"], ensure_ascii=False)
    self.assertNotIn("Biotech", emitted)
    self.assertNotIn("Crypto", emitted)
```

- [ ] **Step 2: Write failing tests for engine-fit separation**

```python
def test_asymmetry_circle_does_not_auto_grant_eng_x_fit(self):
    r = make_response(default_likert=5)
    r["answers"]["AS-01"] = 1
    r["answers"]["AS-07"] = 1
    p = ecai1.interpret_response(r, rules(), bank())
    self.assertNotEqual(p["engine_fit"]["ENG-X"], "primary_fit")
```

- [ ] **Step 3: Encode deterministic engine-fit rules**

`ECAI1-ENGINE-FIT-RULES-v0.1.json` must encode only the accepted Genesis Engine IDs.

Minimum v0.1 gates:

```text
ENG-C positive: horizon/focus + mechanism understanding + noise tolerance + price discipline
ENG-R positive: belief separation + revision willingness + scenario update discipline
ENG-X positive: payoff literacy + bounded-loss tolerance + left-tail discipline + expression discipline
```

Negative signals must demote fit before positive signals promote it. Low research time may make `delegate_preferred` even when conceptual fit is otherwise positive.

- [ ] **Step 4: Implement domain and engine-fit functions**

Required signatures:

```python
def classify_force_domains(profile: dict, domain_evidence: dict | None, rules: dict) -> tuple[str, list[dict]]: ...
def infer_engine_fit(profile: dict, response: dict, rules: dict) -> dict[str, str]: ...
```

Domain action ordering is fail-closed:

```text
survival violation -> AVOID
insufficient specialization but strategic relevance -> EXPLORE
useful strategy with weak durable personal edge/time -> DELEGATE
strong three-circle intersection + no hard conflict -> OWN
relevant but insufficient evidence/current action -> WATCH
```

No domain action grants position authority.

- [ ] **Step 5: Add tests for `OWN / DELEGATE / EXPLORE / AVOID / WATCH` coverage**

Create five compact synthetic responses/domain-evidence cases so every action is emitted by at least one test.

- [ ] **Step 6: Run tests and commit**

```bash
python -m unittest tests.test_ecai1_three_circle_diagnostic -v
git add docs/architecture/ecai1/ECAI1-ENGINE-FIT-RULES-v0.1.json scripts/ecai1_diagnostic.py tests/test_ecai1_three_circle_diagnostic.py
git commit -m "ECAI1: add force-domain and return-engine fit"
```

---

### Task 5: Implement the 8-Section Capital Constitution Report Contract and Provenance

**Files:**
- Modify: `scripts/ecai1_diagnostic.py`
- Modify: `tests/test_ecai1_three_circle_diagnostic.py`

**Interfaces:**
- Consumes: interpreted profile plus source response.
- Produces: `build_report(profile, response) -> dict`; `validate_report_provenance(report) -> None`; `validate_no_recommendation_leakage(report) -> None`.

- [ ] **Step 1: Write failing tests for eight sections and provenance**

```python
def test_report_has_exact_eight_sections(self):
    report = ecai1.build_report(gold_profile(), gold_response())
    self.assertEqual([s["section_id"] for s in report["sections"]], [
        "capital_mirror",
        "three_circle_map",
        "force_investment_domain",
        "return_engine_fit",
        "capital_blind_spots",
        "no_go_constitution",
        "capital_books_delegation",
        "ninety_day_review_plan",
    ])

def test_every_personalized_claim_has_provenance(self):
    report = ecai1.build_report(gold_profile(), gold_response())
    for claim in report["report_claims"]:
        self.assertTrue(claim["source_questions"] or claim["source_domain_evidence"])
```

- [ ] **Step 2: Write failing recommendation-leakage tests**

The validator must reject these examples when they appear as report claims or section recommendations:

```python
for text in [
    "建议买入英伟达",
    "建议卖出腾讯",
    "配置30%到黄金",
    "目标价500美元",
    "保证年化收益20%",
    "立即申购该基金",
]:
    report = minimal_report_with_claim(text)
    with self.assertRaises(ValueError):
        ecai1.validate_no_recommendation_leakage(report)
```

The validator must allow governance language such as `OWN`, `DELEGATE`, `EXPLORE`, `AVOID`, `WATCH` when it is explicitly attached to a domain/strategy category rather than a security instruction.

- [ ] **Step 3: Implement report builder with claim provenance**

Required signatures:

```python
def make_claim(claim_id: str, text: str, source_questions: list[str], source_domain_evidence: list[str], inference_type: str, confidence: str, contradiction_flags: list[str]) -> dict: ...
def build_report(profile: dict, response: dict) -> dict: ...
def validate_report_provenance(report: dict) -> None: ...
def validate_no_recommendation_leakage(report: dict) -> None: ...
```

`build_report` is deterministic and structured; v0.1 does not need an LLM to pass validation. Every blind spot and No-Go rule must reference source question IDs.

- [ ] **Step 4: Add `No Source → No Personalized Claim` negative test**

```python
def test_claim_without_source_is_rejected(self):
    report = ecai1.build_report(gold_profile(), gold_response())
    report["report_claims"][0]["source_questions"] = []
    report["report_claims"][0]["source_domain_evidence"] = []
    with self.assertRaises(ValueError):
        ecai1.validate_report_provenance(report)
```

- [ ] **Step 5: Run tests and commit**

```bash
python -m unittest tests.test_ecai1_three_circle_diagnostic -v
git add scripts/ecai1_diagnostic.py tests/test_ecai1_three_circle_diagnostic.py
git commit -m "ECAI1: add capital constitution report contract"
```

---

### Task 6: Add the Fictional Gold Persona, Hard Negatives, and Human-Facing Artifacts

**Files:**
- Create: `docs/architecture/ecai1/fixtures/gold-chen-response.json`
- Create: `docs/architecture/ecai1/fixtures/gold-chen-profile.json`
- Create: `docs/architecture/ecai1/fixtures/gold-chen-report.json`
- Create: `docs/architecture/ecai1/fixtures/hard-negatives.json`
- Create: `docs/human-projection/ECAI1-ENTREPRENEUR-THREE-CIRCLE-DIAGNOSTIC-v0.1.md`
- Create: `docs/human-projection/ECAI1-GOLD-SAMPLE-REPORT-v0.1.md`
- Modify: `tests/test_ecai1_three_circle_diagnostic.py`

**Interfaces:**
- Consumes: Task 1 schemas and Task 2–5 interpreter functions.
- Produces: reproducible Gold input/output pair and 10 hard-negative cases.

- [ ] **Step 1: Write failing Gold replay test**

```python
def test_gold_chen_response_replays_to_frozen_profile_and_report(self):
    response = load_json(GOLD_RESPONSE)
    expected_profile = load_json(GOLD_PROFILE)
    expected_report = load_json(GOLD_REPORT)
    actual_profile = ecai1.interpret_response(response, rules(), bank())
    actual_report = ecai1.build_report(actual_profile, response)
    self.assertEqual(actual_profile, expected_profile)
    self.assertEqual(actual_report, expected_report)
```

- [ ] **Step 2: Create the fictional Chen response fixture**

Use the accepted persona only:

```text
陈先生（虚构）
43岁
企业服务 SaaS 创始人
创业12年
主要财富来源：未上市企业股权 + 金融资产
研究时间：5–7小时/周
核心经验：SaaS、企业软件、AI应用
```

Include domain evidence only for domains explicitly supported by the persona:

```json
{
  "personal_priors": ["AI adoption in enterprise workflows", "software value capture"],
  "specialization_domains": ["Enterprise Software", "SaaS", "AI Applications"],
  "watch_domains": ["AI Infrastructure", "Short-cycle Macro / CTA", "Complex Options"]
}
```

Do not insert a real person, real client, or live portfolio.

- [ ] **Step 3: Freeze expected Gold profile and report**

Expected high-level semantics must match the accepted spec:

```text
Conviction: mature
Specialization: strong in enterprise software / AI applications
Asymmetry: developing, with price-discipline weakness
Primary engine fit: ENG-C
Secondary engine fit: ENG-R
ENG-X: learning_only or delegate_preferred
Primary domain: Enterprise Software × AI Applications × Founder-led Compounders × ENG-C
AI Infrastructure: EXPLORE
Short-cycle Macro / CTA: DELEGATE
Complex Options: DELEGATE
```

The sample identity line is:

```text
你的真正优势不是比市场更快，而是比市场更懂。
```

- [ ] **Step 4: Create the 10 hard-negative fixtures**

`hard-negatives.json` must contain exactly these cases and an expected rejection/flag:

```text
HN-01 High conviction = high expected return
HN-02 Entrepreneur in AI = should own AI stocks
HN-03 High risk tolerance = high risk capacity
HN-04 Strong specialization = good investment at any price
HN-05 Likes asymmetric outcomes = ENG-X fit
HN-06 Poor manager outcome = manager thesis invalid
HN-07 Questionnaire score = scientific personality truth
HN-08 Fit classification = trade recommendation
HN-09 Current constitution = permanent identity
HN-10 Silent engine migration after falsification
```

- [ ] **Step 5: Add tests that every hard negative fails closed or emits its required conflict**

```python
def test_all_hard_negatives_are_covered(self):
    pack = load_json(HARD_NEGATIVES)
    self.assertEqual({c["case_id"] for c in pack["cases"]}, {f"HN-{i:02d}" for i in range(1, 11)})
    for case in pack["cases"]:
        result = ecai1.evaluate_hard_negative(case)
        self.assertEqual(result["status"], case["expected_status"])
```

- [ ] **Step 6: Create the human-facing questionnaire Markdown**

The document must contain:

```text
Purpose and privacy notice
36 numbered questions grouped 6/8/8/8/6
Likert legend
Scenario answer options
Optional domain-evidence follow-up block
Explicit statement: this is not a buy/sell recommendation or risk-tolerance certification
```

- [ ] **Step 7: Create the 8-section Gold sample report Markdown from the frozen fixture**

The report must mirror the structured JSON and contain no security-specific recommendation, target weight, target price, or return promise.

- [ ] **Step 8: Run tests and commit**

```bash
python -m unittest tests.test_ecai1_three_circle_diagnostic -v
git add docs/architecture/ecai1/fixtures docs/human-projection tests/test_ecai1_three_circle_diagnostic.py
git commit -m "ECAI1: add Gold diagnostic fixtures and human projections"
```

---

### Task 7: Add the Fail-Closed ECAI1 Repository Validator

**Files:**
- Create: `scripts/validate_ecai1_three_circle_diagnostic.py`
- Modify: `tests/test_ecai1_three_circle_diagnostic.py`

**Interfaces:**
- Consumes: all ECAI1 schemas, rules, fixtures, human projections, and Git diff from accepted parent `bd18ec6f92131ddb6948b07973a98d1fe69d5cbb`.
- Produces: process exit 0 with `ECAI1 three-circle diagnostic validation: PASS`, otherwise non-zero with `validation_error: ...`.

- [ ] **Step 1: Write failing validator-unit tests**

Test these validator entry points directly:

```python
validate_question_bank()
validate_schemas()
validate_gold_replay()
validate_hard_negatives()
validate_report_provenance()
validate_recommendation_boundary()
validate_scope_paths(paths)
validate_authority_state()
```

- [ ] **Step 2: Implement allowed scope policy**

Allowed exact paths:

```text
docs/superpowers/specs/2026-08-24-ecai1-three-circle-diagnostic-design.md
docs/superpowers/specs/2026-08-24-ecai1-three-circle-diagnostic-self-review.md
docs/superpowers/plans/2026-08-24-ecai1-three-circle-diagnostic.md
scripts/ecai1_diagnostic.py
scripts/validate_ecai1_three_circle_diagnostic.py
tests/test_ecai1_three_circle_diagnostic.py
.github/workflows/ci.yml
```

Allowed prefixes:

```text
packages/contracts/schemas/ecai1/
docs/architecture/ecai1/
docs/human-projection/ECAI1-
```

Explicitly reject changes under:

```text
docs/architecture/me0/
docs/architecture/me1/
packages/contracts/schemas/vnext/
docs/os-vnext/CONSTITUTION.md
```

- [ ] **Step 3: Implement schema and Gold replay validation**

Use `jsonschema.Draft202012Validator` to validate questionnaire response, profile, and report fixtures. Recompute `gold-chen-profile.json` and `gold-chen-report.json` through `ecai1_diagnostic.py` and require exact equality.

- [ ] **Step 4: Implement human-projection and recommendation-boundary validation**

Require the questionnaire projection to contain `信念`, `精专`, `凸性`, `原力投资域`, and `生存不是第四圈`. Require the Gold report to contain all 8 section headings. Scan report text and structured claims for prohibited patterns such as:

```text
建议买入
建议卖出
目标价
保证收益
保证年化
配置[0-9]+%
仓位[0-9]+%
立即申购
```

Do not scan the questionnaire scenarios with this rule because scenario text may mention hypothetical `加仓/退出` behavior for diagnostic purposes.

- [ ] **Step 5: Run validator locally and verify PASS**

```bash
python scripts/validate_ecai1_three_circle_diagnostic.py
```

Expected:

```text
ECAI1 three-circle diagnostic validation: PASS
```

- [ ] **Step 6: Run the full unit suite and commit**

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
git add scripts/validate_ecai1_three_circle_diagnostic.py tests/test_ecai1_three_circle_diagnostic.py
git commit -m "ECAI1: add fail-closed diagnostic validator"
```

---

### Task 8: Add Candidate Governance State, Human Review Card, and CI Gate

**Files:**
- Create: `docs/architecture/ecai1/ECAI1-STATE.json`
- Create: `docs/architecture/ecai1/ECAI1-HUMAN-REVIEW-CARD-v0.1.md`
- Modify: `.github/workflows/ci.yml`
- Modify: `scripts/validate_ecai1_three_circle_diagnostic.py`
- Modify: `tests/test_ecai1_three_circle_diagnostic.py`

**Interfaces:**
- Consumes: implementation artifacts from Tasks 1–7.
- Produces: machine-qualified candidate waiting for explicit Human Acceptance; no merge or capital authority.

- [ ] **Step 1: Write failing governance-state tests**

```python
def test_ecai1_state_is_candidate_only(self):
    state = load_json(ECAI1_STATE)
    self.assertEqual(state["status"], "IMPLEMENTATION_CANDIDATE_AWAITING_HUMAN_REVIEW")
    self.assertFalse(state["authority"]["portfolio_weight_authority"])
    self.assertFalse(state["authority"]["security_recommendation_authority"])
    self.assertFalse(state["authority"]["trade_execution_authority"])
    self.assertFalse(state["authority"]["manager_approval_authority"])
    self.assertFalse(state["authority"]["me0_me1_mutation_authority"])
    self.assertFalse(state["authority"]["automatic_capital_movement_authority"])
```

- [ ] **Step 2: Create `ECAI1-STATE.json`**

Use:

```json
{
  "program": "ECAI1",
  "status": "IMPLEMENTATION_CANDIDATE_AWAITING_HUMAN_REVIEW",
  "design_acceptance": "ACCEPT_ECAI1_THREE_CIRCLE_DIAGNOSTIC_WRITTEN_SPEC",
  "implementation_human_gate": "ACCEPT_ECAI1_THREE_CIRCLE_DIAGNOSTIC_IMPLEMENTATION",
  "authority": {
    "diagnostic_contract_authority": false,
    "portfolio_weight_authority": false,
    "security_recommendation_authority": false,
    "trade_execution_authority": false,
    "manager_approval_authority": false,
    "me0_me1_mutation_authority": false,
    "automatic_capital_movement_authority": false
  }
}
```

`diagnostic_contract_authority` remains false until Human Acceptance and separately authorized merge closure.

- [ ] **Step 3: Create the Human Review Card with 10 decision dimensions**

The card must include exactly these sections:

```text
D1  First-principles fidelity: 信念 × 精专 × 凸性
D2  Capital Context remains a floor, not a fourth circle
D3  36-question usability and <20-minute target
D4  Anti-acquiescence / scenario consistency quality
D5  Force Investment Domain does not invent expertise
D6  ENG-C/R/X fit preserves ME0 semantics
D7  Report provenance: No Source → No Personalized Claim
D8  No recommendation / sizing leakage
D9  Gold fictional persona quality and hard negatives
D10 PIT/versioning and zero-capital-authority boundary
```

Human acceptance threshold is `10/10 PASS`.

- [ ] **Step 4: Extend validator with governance-state and review-card checks**

Require all D1–D10 headings, the implementation gate token, and every authority field to be false.

- [ ] **Step 5: Add the ECAI1 validator to the existing CI workflow**

In `.github/workflows/ci.yml`, add one command in the `contracts` job after the current YIM0 validator and before unit discovery:

```yaml
      - run: python scripts/validate_ecai1_three_circle_diagnostic.py
```

Do not create a new workflow.

- [ ] **Step 6: Run the same checks CI will run**

```bash
python scripts/validate_ecai1_three_circle_diagnostic.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: both commands exit 0.

- [ ] **Step 7: Run existing repository gates that ECAI1 must not regress**

```bash
python scripts/validate_me0_multi_engine_ontology.py
python scripts/validate_me1_state_object_model.py
python scripts/validate_yim0_methodology_projection.py
```

Expected: all PASS.

- [ ] **Step 8: Commit Task 8**

```bash
git add docs/architecture/ecai1/ECAI1-STATE.json docs/architecture/ecai1/ECAI1-HUMAN-REVIEW-CARD-v0.1.md .github/workflows/ci.yml scripts/validate_ecai1_three_circle_diagnostic.py tests/test_ecai1_three_circle_diagnostic.py
git commit -m "ECAI1: add candidate governance and CI gate"
```

---

### Task 9: Final Machine Qualification and Human-Gate Handoff

**Files:**
- Modify only if validation exposes a concrete defect in an ECAI1-owned file from Tasks 1–8.
- Do not create an acceptance receipt before the user supplies the implementation-acceptance token.

**Interfaces:**
- Consumes: exact implementation branch HEAD.
- Produces: machine qualification evidence and a Human Review request; no merge authorization.

- [ ] **Step 1: Run complete ECAI1 verification from a clean working tree**

```bash
git status --short
python scripts/validate_ecai1_three_circle_diagnostic.py
python -m unittest tests.test_ecai1_three_circle_diagnostic -v
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: clean status before commands; all tests PASS.

- [ ] **Step 2: Run preserved architecture gates**

```bash
python scripts/validate_yip0_philosophy.py
python scripts/validate_me0_multi_engine_ontology.py
python scripts/validate_me1_state_object_model.py
python scripts/validate_yim0_methodology_projection.py
```

Expected: all PASS.

- [ ] **Step 3: Verify the implementation diff is scope-clean**

```bash
git diff --name-only bd18ec6f92131ddb6948b07973a98d1fe69d5cbb...HEAD
```

Expected: every path is accepted by `validate_scope_paths` and no ME0/ME1/Constitution artifact is modified.

- [ ] **Step 4: Open or update a Draft implementation PR with machine evidence**

The PR body must include:

```text
Accepted design token: ACCEPT_ECAI1_THREE_CIRCLE_DIAGNOSTIC_WRITTEN_SPEC
Machine validator: PASS
Unit suite: PASS
ME0/ME1/YIM0 regression gates: PASS
Capital authority: NONE
Required Human token: ACCEPT_ECAI1_THREE_CIRCLE_DIAGNOSTIC_IMPLEMENTATION
```

- [ ] **Step 5: Stop at the Human Gate**

Do not merge. Do not set `diagnostic_contract_authority` true. Do not create portfolio, recommendation, sizing, manager-approval, trading, or capital-movement authority.

Required next user token after Human Review:

```text
ACCEPT_ECAI1_THREE_CIRCLE_DIAGNOSTIC_IMPLEMENTATION
```

---

## Self-Review Against the Accepted Spec

### Spec coverage

- 36-question Gold Diagnostic: Tasks 1 and 6.
- Three-circle semantics and ordinal interpretation: Task 2.
- Scenario consistency, social-desirability/acquiescence controls, contradiction surfacing: Task 3.
- Force Investment Domain with no invented expertise: Task 4.
- ENG-C/R/X fit separate from human Asymmetry: Task 4.
- 8-section Capital Constitution report: Task 5.
- Claim provenance and `No Source → No Personalized Claim`: Task 5.
- Fictional Gold persona and 10 hard negatives: Task 6.
- Interval-based capital privacy and no exact net worth: Task 1.
- PIT/versioned profile contract: Tasks 1 and 8.
- Fail-closed recommendation leakage guard: Tasks 5 and 7.
- Validator and CI gate: Tasks 7 and 8.
- Human Review card and zero-capital-authority candidate state: Task 8.
- Regression protection for accepted ME0/ME1/YIM0: Tasks 7–9.

### Placeholder scan

No implementation step relies on unspecified function names, unbounded “appropriate handling”, or undefined test intent. Every task has exact files, interfaces, expected failure/pass conditions, and commit boundaries.

### Type/signature consistency

The plan consistently uses:

```python
interpret_response(response: dict, rules: dict, question_bank: dict | None = None) -> dict
evaluate_scenario_consistency(response: dict, rules: dict) -> dict
evaluate_conflicts(response: dict, profile: dict, rules: dict) -> list[dict]
classify_force_domains(profile: dict, domain_evidence: dict | None, rules: dict) -> tuple[str, list[dict]]
infer_engine_fit(profile: dict, response: dict, rules: dict) -> dict[str, str]
build_report(profile: dict, response: dict) -> dict
validate_report_provenance(report: dict) -> None
validate_no_recommendation_leakage(report: dict) -> None
```

No task introduces a second competing profile or report interface.

---

## Execution Handoff

Plan completion authorizes execution planning choice only. Implementation should begin from an isolated worktree/branch using the accepted spec and this plan.

Two execution modes are valid:

1. **Subagent-Driven (recommended)** — use `superpowers:subagent-driven-development`; a fresh agent executes each task and receives spec-compliance + code-quality review before the next task.
2. **Inline Execution** — use `superpowers:executing-plans`; execute tasks in this session in reviewable batches with checkpoints.

No merge or capital authority is implied by choosing an execution mode.
