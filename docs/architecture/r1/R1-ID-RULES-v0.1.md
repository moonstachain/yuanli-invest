# R1 Registry ID Rules v0.1

IDs are immutable semantic addresses. Renaming a title does not change an ID; a breaking semantic change requires a new ID or explicit major version.

## Canonical patterns

```text
THEORY-{AUTHOR}-{YEAR}-{SLUG}
HYP-{DOMAIN}-{NNN}-{SLUG}
FACTOR-{DOMAIN}-{SLUG}
ALG-{DOMAIN}-{FAMILY}-{SLUG}
BENCH-{DOMAIN}-{SLUG}-V{N}
SKILL-{RUNTIME}-{SLUG}-V{N}
FIELD-{NAMESPACE}-{SLUG}
PROVIDER-{NAME}-{SLUG}
CAP-{DOMAIN}-{NNN}-{SLUG}
```

`DOMAIN ∈ {P,N,XS,XA,XP,V,S,E,CROSS}`.

`RUNTIME ∈ {WIND,CODEX,REFQ,GENERIC}`.

## Rules

1. IDs use uppercase ASCII, digits and hyphen only.
2. IDs are globally unique within their object class.
3. `CAP-*` numeric sequence is stable; deleted/deprecated IDs are never recycled.
4. Vendor names are prohibited in `FIELD-*`; vendor specificity belongs in `PROVIDER-*`.
5. A provider adapter may map one canonical field to multiple vendor fields with transformation metadata, but may not redefine the canonical economic meaning.
6. A published/canon object may not be edited into a meaningfully different concept under the same ID.
7. `canon` is a maturity state, not an ID namespace and not trading authority.

## Examples

```text
THEORY-SHILLER-2017-NARRATIVE-ECONOMICS
HYP-N-003-MARGINAL-NARRATIVE-ACCELERATION
FACTOR-N-ATTENTION-VELOCITY
ALG-N-HAWKES-CONTAGION-INTENSITY
BENCH-N-TURNING-POINT-V1
SKILL-WIND-NARRATIVE-VELOCITY-V1
FIELD-MARKET-MARKET-CAP
PROVIDER-WIND-MARKET-CAP
CAP-N-003-NARRATIVE-VELOCITY
```