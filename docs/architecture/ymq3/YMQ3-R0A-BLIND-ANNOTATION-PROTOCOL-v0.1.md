# YMQ3-R0A｜Blind Annotation Protocol v0.1

**Stage:** `YMQ3-R0A`  
**Status:** `PROTOCOL_FROZEN / NOT_EXECUTED`  
**Authority:** annotation procedure only; no case label or scientific result is created by this document.

## 1｜Purpose

YMQ3-R0 eventually evaluates the D0–D4 research-state vocabulary. The primary annotation risk is circularity: researchers may already believe a Narrative theory and then label history in a way that makes the theory look correct.

R0A therefore freezes a blind two-annotator process before any D0–D4 phase label is generated.

## 2｜Admission prerequisite

A case may enter blind annotation only if its Evidence Admission verdict is `READY` for the intended annotation evidence packet. `READY_WITH_LIMITATIONS`, `BLOCKED` and `INDETERMINATE` cases do not become primary R0 labels merely because an annotator can tell a plausible historical story.

The current R0A evidence settlement contains no `READY` case. Therefore this protocol is frozen but not executed in the current run.

## 3｜What annotators may see

Both annotators receive the same immutable admitted packet containing only:

- source identities and evidence locators allowed by the Evidence Gate;
- contemporaneous chronology within the permitted annotation boundary;
- admitted official anchors;
- admitted contemporaneous media/news/broadcast evidence;
- declared missingness and uncertainty;
- source/publisher identity after alias consolidation;
- publication/availability timestamps needed to understand chronology.

Every packet carries a hash and an `as_of` boundary.

## 4｜What annotators must not see

Before independent labels are frozen, neither annotator may inspect:

- CSAD, CCK beta2 or dependency-network features;
- any Story/Narrative feature score;
- candidate or baseline model output;
- held-out predictions;
- future returns or future macro releases beyond the packet boundary;
- the other annotator's labels, notes or confidence;
- any later adjudication outcome.

## 5｜Independent label objects

Annotator A and Annotator B each create an append-only label object per annotation interval:

```text
annotation_id
case_id
annotator_id
packet_hash
start_week
end_week
state_label
cause_tag
confidence
uncertainty_reason
evidence_refs
created_at
```

Allowed `state_label` values:

- `D0_DISPERSED`
- `D1_AGGREGATING`
- `D2_REFLEXIVE_ACCELERATION`
- `D3_CROWDED_SATURATION`
- `D4_BREAK`
- `ANNOTATION_UNCERTAIN`

Allowed cause tags remain orthogonal to state labels and include Narrative-heavy, common-shock, forced-deleveraging and mixed Reality/Narrative interpretations defined by the R0 Written Spec.

`ANNOTATION_UNCERTAIN` is a first-class result. Annotators are never forced to choose D0–D4 when the admitted evidence does not support one.

## 6｜Agreement and adjudication

Only after both independent label sets are frozen may the coordinator calculate agreement.

The coordinator records:

- exact state-label agreement rate;
- transition-boundary distance where applicable;
- cause-tag agreement;
- uncertainty disagreement;
- intervals requiring adjudication.

Adjudication creates a third projection. It does not overwrite either independent label set.

The adjudicator receives the two frozen label objects plus the same admitted evidence packet. No model output or future outcome is introduced during adjudication.

## 7｜No silent relabeling

After Story/Herding features or model predictions are revealed:

- phase boundaries cannot move;
- D0–D4 labels cannot be replaced;
- uncertain weeks cannot be deleted;
- a difficult case cannot be dropped;
- the original A/B labels and adjudication projection remain preserved.

Any revision requires a new preregistration version and a complete rerun from admitted Evidence.

## 8｜Current run settlement

Current R0A program evidence status is `INSUFFICIENT_EVIDENCE_INDETERMINATE` candidate state. Consequently:

`BLIND_ANNOTATION_EXECUTION = NOT_AUTHORIZED`

This is not a missing task. It is the intended fail-closed consequence of the Evidence Gate.
