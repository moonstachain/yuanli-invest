# YIOS-TG1-PROT0｜Prototype Handoff v0.1

Status: LOW_FI_CREATED × CLICKABLE_FLOW_NEXT
Figma: https://www.figma.com/design/YkP5ooZxDpEP4n3w7uTVSA

## Six-screen sitemap
Today -> Gold -> Decision -> Audit -> Shadow -> Learning

## First-pass low-fi screens created
- Today
- Gold
- Decision
- Audit
- Shadow
- Settlement & Learning

## Prototype-first questions
1. Can the user understand current state within 30 seconds?
2. Is WAIT perceived as a complete result?
3. Are Trigger and Falsifier discoverable without explanation?
4. Are Unknown / DEGRADED visually impossible to miss?
5. Is SHADOW_ONLY clear enough to avoid live-trading interpretation?
6. Can the user understand how a frozen claim becomes a settlement?
7. Can the user understand how settlement becomes future recall?

## Required flow prototypes
A. WAIT: Today -> Gold -> Decision WAIT -> Audit -> Exit
B. PROBE: Today -> Gold -> Decision PROBE -> Audit -> Shadow Admission
C. DEGRADED: Provider Fail -> Today DEGRADED -> Decision reuse denied
D. Settlement: Open Claim -> Settlement Date -> Verdict -> Learning Candidate
E. Recall: New Decision -> Past Learning surfaced -> Decision delta

## High-fi gate
Do not start high-fi until the above flows pass human review.
