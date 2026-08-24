# YMA55-H0.1｜YIM0 Validator Lifetime Scope Repair v0.1

**Status:** `machine_qualified_on_candidate_branch`  
**Date:** 2026-08-24  
**Repository:** `moonstachain/yuanli-invest`  
**Branch:** `yma55-h1-h3-causal-prior-hardening`  
**Capital / trading authority:** none

## 0. Problem

The accepted YIM0 validator was correct during the YIM0 implementation PR but had a lifecycle bug after YIM0 merged.

It computed scope with:

```text
git diff --name-only 877c3bbc...HEAD
```

Because `877c3bbc...` is the pre-YIM0 base, every legitimate repository file created after YIM0 was interpreted as if it were part of YIM0's own change set. PR #57 therefore failed at `validate_yim0_methodology_projection.py` even though the YMA55 files did not violate YIM0 semantics.

Observed failing workflow before repair:

- run: `#403`
- workflow id: `32689731485`
- governance: `success`
- contracts: `failure`
- failing step: `python scripts/validate_yim0_methodology_projection.py`
- error class: `N11/N12 YIM0 scope violation`

## 1. Root Cause

`validate_scope_paths()` is a historical change-set guard, but `changed_paths_from_git()` used a moving end point (`HEAD`).

The invariant should be:

> Once YIM0 has a recorded semantic merge commit, YIM0's historical scope is immutable even while the repository continues to evolve.

Therefore current YIM0 content/state remains validated at current HEAD, while YIM0's original changed-path scope is evaluated only through its recorded `semantic_merge_commit`.

## 2. Minimal Repair

Added:

```python
def scope_end_ref_for_state(state: dict) -> str:
    semantic_merge_commit = state.get("semantic_merge_commit")
    return semantic_merge_commit if semantic_merge_commit else "HEAD"
```

Changed:

```python
def changed_paths_from_git(end_ref: str = "HEAD") -> list[str]:
    ... f"{BASE_SHA}...{end_ref}" ...
```

And `main()` now evaluates:

```text
current YIM0 artifacts/state at current HEAD
+
YIM0 historical scope at BASE_SHA...semantic_merge_commit
```

Candidate/unmerged YIM0 states still use `HEAD`, preserving the original implementation-time guard.

## 3. Regression Tests

Added tests that require:

1. merged YIM0 state resolves scope end to `semantic_merge_commit`;
2. candidate state resolves scope end to `HEAD`;
3. explicit `end_ref` is passed to the Git diff command.

No YIM0 authority, Constitution, ME0/ME1 semantics, CANON-STATUS semantics, or scope allowlist was broadened.

## 4. Qualification Evidence

Post-repair exact-head candidate commit:

`90199d27302031e4fdb6114945796470cea7b725`

GitHub Actions:

- workflow: `repository-gates`
- run number: `408`
- run id: `32693067909`
- conclusion: `success`
- `governance`: PASS
- `contracts`: PASS
- `python scripts/validate_yim0_methodology_projection.py`: PASS
- full `python -m unittest discover -s tests -p 'test_*.py' -v`: PASS

## 5. Settlement

`YMA55-H0.1 = MACHINE_QUALIFIED_CANDIDATE_REPAIR`

The cross-program CI pollution blocker is removed on this candidate branch.

This settlement does **not** authorize merge. The next authorized work is YMA55-H4 reference implementation and controlled Duration × Credit × Scarcity replay migration under the accepted H1/H2/H3 contracts.
