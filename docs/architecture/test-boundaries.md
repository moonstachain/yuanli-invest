# Test boundaries for the gold research loop

Current contracts test behavior and public compatibility. The `contracts` check
runs from a shallow checkout without a database account. New tests automatically
join this scope, including new tests added to historical test files.

`tests/check-scopes.json` lists each historical test by its full ID. Those tests
verify archived acceptance receipts, frozen fixtures, historical documentation,
and old SQL artifacts; they do not describe today's product availability or prove
deployed permissions. `governance` runs them when their inputs or validators change,
and on releases and manual audits. Both protected check names always run on PRs.

| Previous assertion | Disposition | Reason or replacement |
| --- | --- | --- |
| YIOS0 exactly 13 layers / 8 services and sequential internal IDs | Deleted from validator and tests | No observable behavior depends on this organization. Authority and evidence behavior tests remain. The original architecture document is preserved. |
| YIM0 exact heading order | Deleted | Editorial order is not a runtime contract. Historical source and acceptance records remain. |
| G1 validator command and unittest command spelled exactly in CI | Replaced | Parsed workflow tests verify required check names, current-suite execution and that secret-bearing jobs require trusted main/manual execution. |
| Current root README must contain R0/R1 mission strings | Redirected | R0/R1 audits read the README at the accepted R1 merge `bfd1576e08dc836869b359773b09b3a169d09512`, never the current product README. |
| Bootstrap counts, stage admissions, accepted SHAs and frozen examples | Historical assertions | Verify the specific past artifact; do not require new research to remain at a past bootstrap stage. |
| Historical SQL contains `service_role`, RLS or specific function words | Historical assertions | Retained only as archive checks. Runtime's executable PostgreSQL role/transaction tests validate the new database behavior. |
| Live diagnostics and database credentials in PR workflows | Removed from PR execution | Operator diagnostics require manual dispatch on `main`. No repository marker can authorize a PR job to use production credentials. |

Run locally:

```sh
python -m pip install -e '.[dev]'
python -m scripts.run_checks --scope current
python -m scripts.run_checks --scope historical
```

The historical suite intentionally needs repository history for the original
bootstrap receipt and accepted README. The research Python package does not.
