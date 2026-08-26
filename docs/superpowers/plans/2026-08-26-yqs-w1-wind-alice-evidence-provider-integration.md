# YQS-W1 Wind Alice Evidence Provider Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a no-secret, read-only, fail-closed Wind Alice provider adapter that wraps the pinned official Wind transport, produces deterministic Yuanli receipts/evidence candidates, enforces PIT and authority boundaries, and is ready for a separately authorized real canary.

**Architecture:** YQS-W1 lives behind a strict provider anti-corruption layer. Genesis transport wraps the pinned official `Wind-Information-Co-Ltd/wind-skills` Alice CLI; Yuanli owns invocation validation, secret redaction, retry discipline, output hashing, evidence/PIT mapping, attachment policy, and immutable receipts. The implementation must not write directly to Supabase production or promote provider output into accepted evidence; it emits typed records compatible with the YQS0 kernel for later YQS1 persistence.

**Tech Stack:** Python 3.12 standard library, existing `jsonschema==4.25.1` dev dependency, subprocess execution, SHA-256, JSON fixtures, `unittest`; external provider runtime is Node 18+ official Wind `wind-alice` CLI pinned by repository commit.

**Spec:** `docs/superpowers/specs/2026-08-26-yqs-w1-wind-alice-evidence-provider-integration-design.md`

## Global Constraints

- Python runtime remains `>=3.12`.
- Genesis provider implementation is `official_cli_wrapper`, not a native reimplementation of Alice A2A/SSE.
- Provider source is pinned to `Wind-Information-Co-Ltd/wind-skills@858043b90c916b596cd80da01e8dbf381501675d` for qualification evidence.
- Default provider endpoint profile remains `https://mcp.wind.com.cn/skills/alice`; the adapter does not hard-code credentials.
- Real `WIND_API_KEY` must never enter GitHub, ordinary Supabase tables, evidence bodies, persisted receipts, application logs, exception messages, screenshots, or prompts sent to another model.
- User research prompt is preserved verbatim; provider wire prompt/routing is a separate provider concern and is represented only by a hash unless a synthetic fixture is used.
- Wind Skill taxonomy and Yuanli ResearchCapability taxonomy remain separate namespaces.
- Alice output is a `machine_evidence_analyst` artifact and has no Canon, Evidence Admission, Thesis, portfolio, buy/sell/hold, broker, or live-execution authority.
- Alice prose-derived numeric statements do not write directly to `pit.observations` by default.
- A current Alice artifact cannot be backdated into an older replay; `captured_at` cannot prove earlier `known_as_of`.
- Historical source citations returned by Alice require independent historical publication/availability proof before replay eligibility.
- Automatic retry is limited to at most one transport retry before any provider event is observed; after the first provider event no duplicate research task is automatically issued.
- Allowed normalized terminal outcomes are exactly: `success`, `transport_error`, `unauthorized`, `quota_exceeded`, `provider_error`, `stream_incomplete`, `result_missing`, `attachment_partial`, `cancelled`, `unknown`.
- Attachments are downloaded only from a versioned Wind host/path allowlist; secrets are in-memory only; downloaded bytes are hashed while writing to restricted storage.
- No real Alice invocation, secret installation, Supabase production project, cloud migration/write, Evidence Admission, Canon/Registry promotion, capital authority, broker connection, or live execution is authorized by this plan.
- YQS-W1 cannot merge ahead of its YQS0/YQS1 dependencies.

---

## File Structure

Create these focused units:

```text
providers/
  __init__.py
  wind_alice/
    __init__.py              # stable public exports only
    models.py                # typed dataclasses/enums for invocation/result/receipt records
    profile.py               # pinned provider profile loading + validation
    secrets.py               # secret presence contract and redaction utilities
    transport.py             # official CLI subprocess boundary + injectable synthetic runner
    normalize.py             # terminal state classification + deterministic hashes
    retry.py                 # retry decision function; no network logic
    evidence.py              # YQS0-compatible source/snapshot/claim/lineage DTO builders
    pit.py                   # replay eligibility and known-as-of guards
    attachments.py           # host/path allowlist + streaming hash/copy policy
    service.py               # orchestration of the above units; no Supabase persistence

configs/providers/
  wind-alice-v0.1.json       # non-secret provider profile

tests/fixtures/wind_alice/
  success.json
  transport_error.json
  unauthorized.json
  quota_exceeded.json
  stream_incomplete.json
  result_missing.json
  attachment_success.json
  attachment_rejected.json

tests/
  test_yqs_w1_profile.py
  test_yqs_w1_secrets.py
  test_yqs_w1_transport.py
  test_yqs_w1_normalize.py
  test_yqs_w1_retry.py
  test_yqs_w1_evidence_pit.py
  test_yqs_w1_attachments.py
  test_yqs_w1_e2e.py
  test_yqs_w1_authority.py

scripts/
  run_wind_alice_provider.py
  validate_yqs_w1_wind_alice_provider.py

docs/architecture/yqs-w1/
  YQS-W1-STATE.json
  YQS-W1-HUMAN-REVIEW-CARD-v0.1.md
  YQS-W1-LIVE-CANARY-AUTHORIZATION-CARD-v0.1.md
```

Do not copy Wind provider source into this repository. The runtime path to a separately installed/pinned provider checkout is supplied through configuration/environment.

---

### Task 1: Freeze Provider Profile and Typed Contracts

**Files:**
- Create: `providers/__init__.py`
- Create: `providers/wind_alice/__init__.py`
- Create: `providers/wind_alice/models.py`
- Create: `providers/wind_alice/profile.py`
- Create: `configs/providers/wind-alice-v0.1.json`
- Test: `tests/test_yqs_w1_profile.py`

**Interfaces:**
- Produces: `ProviderProfile`, `Invocation`, `TransportResult`, `ProviderReceipt`, `ProviderOutcome`, `load_provider_profile(path: Path) -> ProviderProfile`.
- Consumed by: Tasks 2–9.

- [ ] **Step 1: Write the failing profile/contract tests**

```python
from pathlib import Path
from providers.wind_alice.models import ProviderOutcome
from providers.wind_alice.profile import load_provider_profile


def test_provider_profile_is_pinned_and_non_authoritative():
    profile = load_provider_profile(Path("configs/providers/wind-alice-v0.1.json"))
    assert profile.provider_id == "wind-alice-a2a"
    assert profile.transport == "official_cli_wrapper"
    assert profile.provider_repo == "Wind-Information-Co-Ltd/wind-skills"
    assert profile.provider_repo_commit == "858043b90c916b596cd80da01e8dbf381501675d"
    assert profile.secret_ref == "WIND_ALICE_API_KEY"
    assert profile.canon_authority is False
    assert profile.evidence_admission_authority is False
    assert profile.thesis_authority is False
    assert profile.live_execution_authority is False


def test_outcome_enum_is_exact():
    assert {v.value for v in ProviderOutcome} == {
        "success", "transport_error", "unauthorized", "quota_exceeded",
        "provider_error", "stream_incomplete", "result_missing",
        "attachment_partial", "cancelled", "unknown",
    }
```

- [ ] **Step 2: Run the tests and verify they fail because the package does not exist**

Run:

```bash
python -m unittest tests.test_yqs_w1_profile -v
```

Expected: import/module failure.

- [ ] **Step 3: Implement the minimal dataclasses/enums**

`models.py` must define immutable/frozen dataclasses. Use this exact public shape:

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Mapping

class ProviderOutcome(str, Enum):
    SUCCESS = "success"
    TRANSPORT_ERROR = "transport_error"
    UNAUTHORIZED = "unauthorized"
    QUOTA_EXCEEDED = "quota_exceeded"
    PROVIDER_ERROR = "provider_error"
    STREAM_INCOMPLETE = "stream_incomplete"
    RESULT_MISSING = "result_missing"
    ATTACHMENT_PARTIAL = "attachment_partial"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class ProviderProfile:
    provider_id: str
    provider_class: str
    transport: str
    provider_repo: str
    provider_repo_commit: str
    skill_path: str
    api_endpoint_default: str
    auth_scheme: str
    secret_ref: str
    stream_protocol: str
    rpc_protocol: str
    rpc_method: str
    result_field: str
    timezone: str
    attachment_allowlist: tuple[str, ...]
    canon_authority: bool
    evidence_admission_authority: bool
    thesis_authority: bool
    live_execution_authority: bool

@dataclass(frozen=True)
class Invocation:
    invocation_id: str
    invocation_intent_id: str
    attempt_id: str
    requested_at: datetime
    provider_id: str
    user_prompt_original: str
    prompt_sha256: str
    skill_requested: str | None
    provider_profile_version: str
    purpose: str
    caller_role: str
    research_target_id: str | None = None
    capability_id: str | None = None
    replay_case_id: str | None = None
    knowledge_cutoff: datetime | None = None

@dataclass(frozen=True)
class TransportResult:
    exit_code: int
    stdout: str
    stderr: str
    started_at: datetime
    completed_at: datetime
    first_event_observed: bool
    provider_task_id: str | None = None
    provider_context_id: str | None = None
    event_count: int = 0
    metadata: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class ProviderReceipt:
    invocation_id: str
    attempt_id: str
    provider_id: str
    provider_profile_version: str
    provider_repo_commit: str
    prompt_sha256: str
    skill_requested: str | None
    skill_resolved: str | None
    outcome: ProviderOutcome
    request_started_at: datetime
    response_completed_at: datetime
    first_event_observed: bool
    provider_task_id: str | None
    provider_context_id: str | None
    event_count: int
    agent_result_sha256: str | None
    output_locator: str | None
    failure_code: str | None
    authority: Mapping[str, bool]
```

- [ ] **Step 4: Create the non-secret provider profile**

`configs/providers/wind-alice-v0.1.json` must contain the accepted values and an explicit allowlist such as:

```json
{
  "profile_version": "wind-alice-v0.1",
  "provider_id": "wind-alice-a2a",
  "provider_class": "machine_evidence_analyst",
  "transport": "official_cli_wrapper",
  "provider_repo": "Wind-Information-Co-Ltd/wind-skills",
  "provider_repo_commit": "858043b90c916b596cd80da01e8dbf381501675d",
  "skill_path": "skills/wind-alice",
  "api_endpoint_default": "https://mcp.wind.com.cn/skills/alice",
  "auth_scheme": "bearer",
  "secret_ref": "WIND_ALICE_API_KEY",
  "stream_protocol": "sse",
  "rpc_protocol": "jsonrpc-2.0",
  "rpc_method": "message/stream",
  "result_field": "agentResult.value",
  "timezone": "Asia/Shanghai",
  "attachment_allowlist": ["alice.wind.com.cn", "aliceexp.wind.com.cn"],
  "canon_authority": false,
  "evidence_admission_authority": false,
  "thesis_authority": false,
  "live_execution_authority": false
}
```

`load_provider_profile` must reject missing keys, unknown authority `true` values, a mutable/empty provider commit, or a secret value appearing in the profile.

- [ ] **Step 5: Run the tests and verify PASS**

```bash
python -m unittest tests.test_yqs_w1_profile -v
```

- [ ] **Step 6: Commit**

```bash
git add providers configs/providers tests/test_yqs_w1_profile.py
git commit -m "feat(yqs-w1): add pinned Wind Alice provider contracts"
```

---

### Task 2: Implement Secret Boundary and Redaction

**Files:**
- Create: `providers/wind_alice/secrets.py`
- Test: `tests/test_yqs_w1_secrets.py`

**Interfaces:**
- Consumes: `ProviderProfile.secret_ref`.
- Produces: `SecretUnavailable`, `read_secret_from_environment(secret_ref: str, environ: Mapping[str, str]) -> str`, `redact_secrets(text: str, secret_values: tuple[str, ...]) -> str`, `assert_secret_absent(payload: object, secret_values: tuple[str, ...]) -> None`.

- [ ] **Step 1: Write failing tests**

```python
from providers.wind_alice.secrets import (
    SecretUnavailable, assert_secret_absent, read_secret_from_environment, redact_secrets,
)


def test_missing_key_fails_closed():
    try:
        read_secret_from_environment("WIND_ALICE_API_KEY", {})
    except SecretUnavailable as exc:
        assert str(exc) == "provider_secret_unavailable:WIND_ALICE_API_KEY"
    else:
        raise AssertionError("missing key must fail closed")


def test_redaction_removes_key_from_text_and_nested_payload():
    key = "ak_test_DO_NOT_USE"
    assert key not in redact_secrets(f"Bearer {key}", (key,))
    try:
        assert_secret_absent({"stderr": f"Authorization: Bearer {key}"}, (key,))
    except ValueError as exc:
        assert "secret_material_detected" in str(exc)
    else:
        raise AssertionError("nested secret must be detected")
```

- [ ] **Step 2: Verify tests fail**

```bash
python -m unittest tests.test_yqs_w1_secrets -v
```

- [ ] **Step 3: Implement using only environment lookup and deterministic replacement**

Requirements:

```python
class SecretUnavailable(RuntimeError):
    pass


def read_secret_from_environment(secret_ref, environ):
    value = environ.get(secret_ref, "")
    if not value:
        raise SecretUnavailable(f"provider_secret_unavailable:{secret_ref}")
    return value
```

`redact_secrets` must replace exact secret values with `<REDACTED>` and also redact `Authorization: Bearer ...` / `Bearer ...` forms without echoing the candidate token in exceptions.

- [ ] **Step 4: Run tests**

```bash
python -m unittest tests.test_yqs_w1_secrets -v
```

- [ ] **Step 5: Commit**

```bash
git add providers/wind_alice/secrets.py tests/test_yqs_w1_secrets.py
git commit -m "feat(yqs-w1): enforce Wind Alice secret boundary"
```

---

### Task 3: Build the Official CLI Transport Boundary with Synthetic Injection

**Files:**
- Create: `providers/wind_alice/transport.py`
- Create: `tests/fixtures/wind_alice/success.json`
- Create: `tests/fixtures/wind_alice/transport_error.json`
- Create: `tests/fixtures/wind_alice/unauthorized.json`
- Create: `tests/fixtures/wind_alice/quota_exceeded.json`
- Create: `tests/fixtures/wind_alice/stream_incomplete.json`
- Create: `tests/fixtures/wind_alice/result_missing.json`
- Test: `tests/test_yqs_w1_transport.py`

**Interfaces:**
- Consumes: `Invocation`, `ProviderProfile`.
- Produces: `TransportRunner` protocol/callable and `OfficialCliTransport.invoke(invocation, secret, runner=subprocess.run) -> TransportResult`.

- [ ] **Step 1: Write failing tests for command construction and prompt preservation**

```python
from providers.wind_alice.transport import OfficialCliTransport


def test_transport_passes_original_prompt_without_rewrite(profile, invocation, fake_runner):
    transport = OfficialCliTransport(profile, skill_root="/opt/wind-skills/skills/wind-alice")
    transport.invoke(invocation, "ak_test_DO_NOT_USE", runner=fake_runner)
    argv = fake_runner.calls[0][0]
    assert "--prompt" in argv
    assert argv[argv.index("--prompt") + 1] == invocation.user_prompt_original
    assert argv[argv.index("--skill") + 1] == invocation.skill_requested
```

Also assert the secret is supplied via child environment, never argv.

- [ ] **Step 2: Verify tests fail**

```bash
python -m unittest tests.test_yqs_w1_transport -v
```

- [ ] **Step 3: Implement `OfficialCliTransport`**

Required command form:

```python
argv = [
    "node",
    str(skill_root / "scripts" / "wind-alice.mjs"),
    "--prompt",
    invocation.user_prompt_original,
]
if invocation.skill_requested:
    argv += ["--skill", invocation.skill_requested]
```

The child environment receives `WIND_API_KEY`; the parent process never serializes the key into `TransportResult`. Reject a missing `wind-alice.mjs`, an unverified provider checkout commit marker, or a skill root outside the configured provider checkout.

For Genesis qualification, add `provider_checkout_commit` as an explicit constructor argument and require it equals the pinned profile commit before invocation.

- [ ] **Step 4: Add synthetic runner fixtures instead of network calls**

Fixture format must be simple JSON, for example:

```json
{
  "exit_code": 0,
  "stdout": "agentResult.value: 事实核验完成：示例内容",
  "stderr": "",
  "first_event_observed": true,
  "event_count": 4,
  "provider_task_id": "task-fixture-1",
  "provider_context_id": "context-fixture-1"
}
```

Tests must cover success, transport error, unauthorized, quota exhaustion, incomplete stream, and missing result without making a real Wind request.

- [ ] **Step 5: Run tests**

```bash
python -m unittest tests.test_yqs_w1_transport -v
```

- [ ] **Step 6: Commit**

```bash
git add providers/wind_alice/transport.py tests/fixtures/wind_alice tests/test_yqs_w1_transport.py
git commit -m "feat(yqs-w1): add pinned official CLI transport boundary"
```

---

### Task 4: Normalize Provider Outcomes, Hashes, and Retry Decisions

**Files:**
- Create: `providers/wind_alice/normalize.py`
- Create: `providers/wind_alice/retry.py`
- Test: `tests/test_yqs_w1_normalize.py`
- Test: `tests/test_yqs_w1_retry.py`

**Interfaces:**
- Consumes: `TransportResult`.
- Produces: `extract_agent_result(stdout: str) -> str | None`, `classify_outcome(result: TransportResult) -> ProviderOutcome`, `sha256_text(text: str) -> str`, `should_retry(outcome, first_event_observed, attempt_number) -> bool`.

- [ ] **Step 1: Write failing normalization tests**

```python
from providers.wind_alice.models import ProviderOutcome
from providers.wind_alice.normalize import classify_outcome, extract_agent_result, sha256_text


def test_agent_result_extraction_is_stable():
    text = "noise\nagentResult.value: hello world\n"
    assert extract_agent_result(text) == "hello world"
    assert sha256_text("hello world") == sha256_text("hello world")


def test_quota_is_not_success(quota_transport_result):
    assert classify_outcome(quota_transport_result) == ProviderOutcome.QUOTA_EXCEEDED
```

- [ ] **Step 2: Write failing retry tests**

```python
from providers.wind_alice.models import ProviderOutcome
from providers.wind_alice.retry import should_retry


def test_only_one_pre_event_transport_retry():
    assert should_retry(ProviderOutcome.TRANSPORT_ERROR, False, 1) is True
    assert should_retry(ProviderOutcome.TRANSPORT_ERROR, False, 2) is False
    assert should_retry(ProviderOutcome.TRANSPORT_ERROR, True, 1) is False
    assert should_retry(ProviderOutcome.QUOTA_EXCEEDED, False, 1) is False
    assert should_retry(ProviderOutcome.UNAUTHORIZED, False, 1) is False
```

- [ ] **Step 3: Run and verify failure**

```bash
python -m unittest tests.test_yqs_w1_normalize tests.test_yqs_w1_retry -v
```

- [ ] **Step 4: Implement exact failure precedence**

Classify in this order:

```text
unauthorized
quota_exceeded
cancelled
transport_error
provider_error
stream_incomplete
result_missing
success
unknown
```

Do not infer success merely from exit code 0; a success requires a non-empty terminal `agentResult.value`.

- [ ] **Step 5: Run tests**

```bash
python -m unittest tests.test_yqs_w1_normalize tests.test_yqs_w1_retry -v
```

- [ ] **Step 6: Commit**

```bash
git add providers/wind_alice/normalize.py providers/wind_alice/retry.py tests/test_yqs_w1_normalize.py tests/test_yqs_w1_retry.py
git commit -m "feat(yqs-w1): normalize provider outcomes and retry law"
```

---

### Task 5: Map Alice Output into YQS0 Evidence/PIT DTOs without Admission

**Files:**
- Create: `providers/wind_alice/evidence.py`
- Create: `providers/wind_alice/pit.py`
- Test: `tests/test_yqs_w1_evidence_pit.py`
- Test: `tests/test_yqs_w1_authority.py`

**Interfaces:**
- Produces: `build_source_record`, `build_source_snapshot`, `build_candidate_claim`, `build_data_lineage`, `build_run_receipt`, `alice_artifact_replay_eligible(known_as_of, knowledge_cutoff) -> bool`.
- All produced records are plain JSON-serializable dicts matching YQS0 semantic fields; no database connection exists in this task.

- [ ] **Step 1: Write failing PIT tests**

```python
from datetime import datetime, timezone
from providers.wind_alice.pit import alice_artifact_replay_eligible


def test_current_alice_output_cannot_be_backdated_into_old_replay():
    known = datetime(2026, 8, 26, tzinfo=timezone.utc)
    cutoff = datetime(2024, 12, 31, tzinfo=timezone.utc)
    assert alice_artifact_replay_eligible(known, cutoff) is False
```

- [ ] **Step 2: Write failing authority tests**

```python
from providers.wind_alice.evidence import build_candidate_claim


def test_provider_claim_is_candidate_only(source_snapshot):
    claim = build_candidate_claim(
        source_snapshot=source_snapshot,
        text="Example claim",
        claim_type="provider_synthesis",
        extraction_method="synthetic_fixture_v1",
    )
    assert claim["review_state"] == "candidate"
    assert claim["accepted"] is False
    assert "portfolio_weight" not in claim
    assert "trade_instruction" not in claim
```

- [ ] **Step 3: Run and verify failure**

```bash
python -m unittest tests.test_yqs_w1_evidence_pit tests.test_yqs_w1_authority -v
```

- [ ] **Step 4: Implement conservative mapping**

`build_source_snapshot` must include at least:

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

For Alice-generated artifacts use:

```python
available_at = captured_at
known_as_of = captured_at
```

unless an even later conservative availability timestamp is supplied. Never derive `known_as_of` from the subject period discussed in the report.

`build_run_receipt` must explicitly set all authority flags false and include `provider_repo_commit`.

- [ ] **Step 5: Add historical citation rule**

Expose:

```python
def cited_source_requires_independent_pit_proof() -> bool:
    return True
```

and test that no Alice citation helper returns historical replay eligibility on its own.

- [ ] **Step 6: Run tests**

```bash
python -m unittest tests.test_yqs_w1_evidence_pit tests.test_yqs_w1_authority -v
```

- [ ] **Step 7: Commit**

```bash
git add providers/wind_alice/evidence.py providers/wind_alice/pit.py tests/test_yqs_w1_evidence_pit.py tests/test_yqs_w1_authority.py
git commit -m "feat(yqs-w1): map Alice output to candidate evidence with PIT guards"
```

---

### Task 6: Implement Attachment Allowlist and Streaming Hash Policy

**Files:**
- Create: `providers/wind_alice/attachments.py`
- Create: `tests/fixtures/wind_alice/attachment_success.json`
- Create: `tests/fixtures/wind_alice/attachment_rejected.json`
- Test: `tests/test_yqs_w1_attachments.py`

**Interfaces:**
- Produces: `AttachmentRejected`, `validate_attachment_url(url, allowlist)`, `store_attachment_stream(chunks, target_path) -> AttachmentRecord`.

- [ ] **Step 1: Write failing host/path tests**

```python
from providers.wind_alice.attachments import AttachmentRejected, validate_attachment_url


def test_non_wind_host_is_rejected():
    try:
        validate_attachment_url("https://evil.example/report.pdf", ("alice.wind.com.cn",))
    except AttachmentRejected as exc:
        assert str(exc) == "attachment_host_not_allowed"
    else:
        raise AssertionError("arbitrary provider-emitted URL must be rejected")
```

- [ ] **Step 2: Write failing hash test**

```python
from hashlib import sha256
from providers.wind_alice.attachments import store_attachment_stream


def test_streamed_attachment_hash_is_content_hash(tmp_path):
    payload = b"synthetic licensed fixture"
    record = store_attachment_stream([payload[:5], payload[5:]], tmp_path / "fixture.bin")
    assert record.sha256 == sha256(payload).hexdigest()
    assert record.size_bytes == len(payload)
```

- [ ] **Step 3: Run and verify failure**

```bash
python -m unittest tests.test_yqs_w1_attachments -v
```

- [ ] **Step 4: Implement allowlist and streaming write**

Use `urllib.parse.urlparse`. Require `https`, exact hostname membership, no embedded credentials, and provider-approved path prefixes when configured. The stream function receives bytes from an already-authenticated caller; it never receives or logs the API key.

- [ ] **Step 5: Run tests**

```bash
python -m unittest tests.test_yqs_w1_attachments -v
```

- [ ] **Step 6: Commit**

```bash
git add providers/wind_alice/attachments.py tests/fixtures/wind_alice/attachment_*.json tests/test_yqs_w1_attachments.py
git commit -m "feat(yqs-w1): enforce restricted Wind attachment policy"
```

---

### Task 7: Compose the Read-Only Provider Service and Synthetic End-to-End Qualification

**Files:**
- Create: `providers/wind_alice/service.py`
- Modify: `providers/wind_alice/__init__.py`
- Create: `scripts/run_wind_alice_provider.py`
- Test: `tests/test_yqs_w1_e2e.py`

**Interfaces:**
- Consumes all prior task interfaces.
- Produces: `WindAliceProviderService.invoke(invocation, *, secret_environ, runner) -> ProviderExecution` where `ProviderExecution` contains `receipt`, optional `source_snapshot`, candidate `claims`, and `lineage`; no Supabase side effects.

- [ ] **Step 1: Write failing synthetic E2E test**

```python

def test_synthetic_success_produces_receipt_snapshot_and_candidate_claim(service, invocation, fake_success_runner):
    execution = service.invoke(
        invocation,
        secret_environ={"WIND_ALICE_API_KEY": "ak_test_DO_NOT_USE"},
        runner=fake_success_runner,
    )
    assert execution.receipt.outcome.value == "success"
    assert execution.source_snapshot["known_as_of"] == execution.source_snapshot["captured_at"]
    assert execution.claims[0]["review_state"] == "candidate"
    serialized = execution.to_json()
    assert "ak_test_DO_NOT_USE" not in serialized
```

- [ ] **Step 2: Add failure E2E tests**

For unauthorized/quota/stream incomplete/result missing, assert:

```text
receipt exists
source_snapshot is None for false-success cases
claims == []
secret absent
no automatic admission
```

- [ ] **Step 3: Run and verify failure**

```bash
python -m unittest tests.test_yqs_w1_e2e -v
```

- [ ] **Step 4: Implement service orchestration**

Order must be:

```text
validate invocation
-> read runtime secret
-> call official transport
-> redact stdout/stderr
-> classify terminal outcome
-> if success: extract terminal result
-> hash terminal result
-> build receipt
-> build source snapshot
-> build candidate claim(s)
-> build lineage
-> assert secret absent in every persistable object
-> return ProviderExecution
```

No step may call Supabase, mutate Canon, assign portfolio weights, or invoke a broker.

- [ ] **Step 5: Implement no-secret CLI mode**

`scripts/run_wind_alice_provider.py` supports only two modes in this PR:

```text
--fixture <path>     synthetic qualification; permitted
--live               exits with live_canary_not_authorized
```

The script must never accept an API key as a CLI argument.

- [ ] **Step 6: Run E2E tests**

```bash
python -m unittest tests.test_yqs_w1_e2e -v
```

- [ ] **Step 7: Run the synthetic CLI fixture**

```bash
python scripts/run_wind_alice_provider.py --fixture tests/fixtures/wind_alice/success.json
```

Expected stdout contains a sanitized JSON receipt with `outcome=success` and no secret material.

- [ ] **Step 8: Verify live mode fails closed**

```bash
python scripts/run_wind_alice_provider.py --live
```

Expected exit non-zero with exactly `live_canary_not_authorized` and no credential lookup.

- [ ] **Step 9: Commit**

```bash
git add providers/wind_alice/service.py providers/wind_alice/__init__.py scripts/run_wind_alice_provider.py tests/test_yqs_w1_e2e.py
git commit -m "feat(yqs-w1): complete synthetic Wind Alice provider qualification"
```

---

### Task 8: Add Fail-Closed Repository Validation and CI Gate

**Files:**
- Create: `scripts/validate_yqs_w1_wind_alice_provider.py`
- Modify: `.github/workflows/ci.yml`
- Test: extend `tests/test_yqs_w1_authority.py`

**Interfaces:**
- Validator returns exit 0 only when all YQS-W1 invariants and required files are present.

- [ ] **Step 1: Write validator tests/fixtures first**

The validator must check:

```text
provider commit pinned exactly
profile authority flags all false
secret_ref present but no secret-looking key body in tracked YQS-W1 files
no Authorization header fixture containing a real token
no write path to pit.observations in provider package
no accepted evidence state emitted by provider package
no portfolio/broker/live execution call sites
live CLI mode remains blocked
synthetic fixtures cover all required normalized failure outcomes
```

Use repository text scans plus direct unit calls; do not rely only on string absence for semantic checks.

- [ ] **Step 2: Implement validator**

Required terminal message:

```text
YQS-W1 Wind Alice provider validation: PASS
```

On error print `validation_error: ...` and exit 1.

- [ ] **Step 3: Run validator locally**

```bash
python scripts/validate_yqs_w1_wind_alice_provider.py
```

Expected: PASS.

- [ ] **Step 4: Run all YQS-W1 tests**

```bash
python -m unittest \
  tests.test_yqs_w1_profile \
  tests.test_yqs_w1_secrets \
  tests.test_yqs_w1_transport \
  tests.test_yqs_w1_normalize \
  tests.test_yqs_w1_retry \
  tests.test_yqs_w1_evidence_pit \
  tests.test_yqs_w1_attachments \
  tests.test_yqs_w1_e2e \
  tests.test_yqs_w1_authority -v
```

Expected: all PASS.

- [ ] **Step 5: Add CI step before generic unit discovery**

Add to `.github/workflows/ci.yml`:

```yaml
      - run: python scripts/validate_yqs_w1_wind_alice_provider.py
```

Place it after the YQS0 validator and before `python -m unittest discover ...` so YQS-W1 failures remain easy to diagnose.

- [ ] **Step 6: Run full repository validation**

```bash
python scripts/validate_repository.py
python scripts/leak_guard.py
python scripts/check_governance.py
python scripts/validate_yqs0_supabase_kernel.py
python scripts/validate_yqs_w1_wind_alice_provider.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

If an unrelated pre-existing gate fails, record it separately; do not weaken that gate to make YQS-W1 green.

- [ ] **Step 7: Commit**

```bash
git add scripts/validate_yqs_w1_wind_alice_provider.py .github/workflows/ci.yml tests/test_yqs_w1_authority.py
git commit -m "ci(yqs-w1): gate Wind Alice provider qualification"
```

---

### Task 9: Freeze Candidate State, Human Review, and Separate Live Canary Gate

**Files:**
- Create: `docs/architecture/yqs-w1/YQS-W1-STATE.json`
- Create: `docs/architecture/yqs-w1/YQS-W1-HUMAN-REVIEW-CARD-v0.1.md`
- Create: `docs/architecture/yqs-w1/YQS-W1-LIVE-CANARY-AUTHORIZATION-CARD-v0.1.md`
- Modify: PR #64 body/comment only after exact-head CI evidence is available.

**Interfaces:**
- Produces no runtime authority; documentation records qualification state and next human gate.

- [ ] **Step 1: Write `YQS-W1-STATE.json` as candidate-only**

Required fields:

```json
{
  "schema_version": "0.1.0",
  "stage": "YQS_W1_WIND_ALICE_EVIDENCE_PROVIDER_INTEGRATION",
  "status": "synthetic_qualification_candidate",
  "provider_profile": "configs/providers/wind-alice-v0.1.json",
  "provider_repo_commit": "858043b90c916b596cd80da01e8dbf381501675d",
  "design_acceptance": "ACCEPT_YQS_W1_WIND_ALICE_EVIDENCE_PROVIDER_DESIGN",
  "synthetic_qualification_required": true,
  "live_canary_authorized": false,
  "secret_installation_authorized": false,
  "supabase_production_write_authorized": false,
  "evidence_admission_authorized": false,
  "portfolio_authority": false,
  "live_execution_authorized": false,
  "next_gate": "YQS_W1_SYNTHETIC_QUALIFICATION_HUMAN_REVIEW"
}
```

- [ ] **Step 2: Create the Human Review Card**

Require explicit PASS/FAIL for at least:

```text
D1 provider pin verified
D2 prompt immutability
D3 secret redaction
D4 synthetic failure semantics
D5 retry/cost discipline
D6 PIT no-backdating
D7 candidate-only evidence
D8 attachment allowlist/hash
D9 authority zero-capital boundary
D10 full CI exact-head status
D11 dependency order with YQS0/YQS1
D12 live canary still blocked
```

- [ ] **Step 3: Create a separate Live Canary Authorization Card**

It must state that a future canary requires all of:

```text
YQS0/YQS1 substrate ready for the intended mapping path
synthetic qualification PASS
exact provider commit/profile frozen
secret installed outside chat/repo
one low-cost non-trading Fact Check prompt frozen
maximum one real invocation unless separately reauthorized
no automatic retry after first provider event
receipt + redaction + PIT mapping reviewed
```

Reserve but do not exercise a future token:

```text
AUTHORIZE_YQS_W1_WIND_ALICE_LIVE_CANARY
```

- [ ] **Step 4: Run final repository gates and inspect exact-head CI**

Local commands are the same as Task 8. Push and wait for GitHub Actions. Do not claim machine qualification unless both YQS-W1 validator and relevant repository jobs pass at the exact PR head.

- [ ] **Step 5: Update PR #64 with evidence, not conclusions beyond the evidence**

Record:

```text
head SHA
workflow run id/number
YQS-W1 validator result
unit-test result
governance result
any upstream/pre-existing blocker
```

Do not mark the PR merge-ready if YQS0/YQS1 dependency gates are not satisfied.

- [ ] **Step 6: Commit**

```bash
git add docs/architecture/yqs-w1
git commit -m "docs(yqs-w1): freeze synthetic qualification review gates"
```

---

## Plan Self-Review Result

### Spec coverage

- Provider classification / authority boundary: Tasks 1, 5, 8, 9.
- Official CLI wrapper / pinned provider commit: Tasks 1, 3, 8.
- Prompt immutability and Skill namespace separation: Tasks 1, 3.
- Secret law and logging redaction: Tasks 2, 7, 8.
- Evidence mapping into YQS0: Task 5.
- PIT no-backdating and historical-source independence: Task 5.
- SSE/stream terminal semantics through the official transport boundary: Tasks 3, 4, 7.
- Retry/cost discipline: Task 4.
- Attachments / allowlist / hashing: Task 6.
- Failure semantics: Tasks 3, 4, 7.
- Synthetic qualification and authority tests: Tasks 7, 8.
- Live canary separated behind explicit authorization: Tasks 7, 9.
- YQS0/YQS1 sequencing / no premature merge: Global Constraints + Task 9.

### Placeholder scan

No `TBD`, `TODO`, "implement later", unspecified error handling, or placeholder code paths are permitted by this plan.

### Type/interface consistency

All tasks use the same public objects from Task 1 (`ProviderProfile`, `Invocation`, `TransportResult`, `ProviderReceipt`, `ProviderOutcome`). Persistence-facing outputs remain JSON-serializable DTOs; no task introduces a Supabase production client or a parallel evidence ontology.

## Exit Condition

This implementation plan is complete when YQS-W1 has a no-secret synthetic adapter candidate that:

```text
preserves original prompt
+ wraps exact pinned official Wind runtime
+ never serializes the real key
+ classifies failure/success deterministically
+ constrains retries
+ hashes provider result/artifacts
+ emits YQS0-compatible candidate evidence/lineage/receipt DTOs
+ rejects historical backdating
+ rejects arbitrary attachments
+ passes exact-head validation
+ still refuses real live invocation without a separate authorization
```

Synthetic qualification is **not** evidence that Alice research quality or investment alpha is good; it only qualifies the integration contract and safety/authority behavior.
