# YF3N0-C｜Atomic Preregistration Clarification

Status: `WRITTEN_SPEC_CLARIFICATION`

This clarification is normative for the YF3N0-C written specification.

The conceptual Triple Seal remains:

1. Evidence Seal;
2. Prediction Seal;
3. Resolution Rule Seal.

The machine implementation MUST NOT perform Prediction and Resolution Rule sealing as two independently mutable transactions.

The lawful implementation ordering is:

```text
EvidenceSeal
→ AtomicPreregistrationBundle {
    PredictionContract,
    ResolutionContract
  }
→ seal_timestamp
→ FutureEvidence
→ BlindResolution
→ SettlementRecord
```

The PredictionContract and its ResolutionContract must receive the same preregistration bundle identity and the same effective seal timestamp.

Hard invariants:

```text
PredictionContract.bundle_id == ResolutionContract.bundle_id
PredictionContract.seal_timestamp == ResolutionContract.seal_timestamp
EvidenceSeal.seal_timestamp <= PredictionContract.seal_timestamp
PredictionContract.seal_timestamp < SettlementRecord.resolved_at
```

No ResolutionContract may be first created or materially changed after the corresponding PredictionContract has been sealed.

No outcome evidence may be incorporated before the atomic preregistration bundle is sealed.

This clarification does not change the accepted YF3N0-C architecture. It removes an implementation ambiguity identified during written-spec self-review.
