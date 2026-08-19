# Canonical Research Dependency Graph vNext

## Purpose

The canonical research dependency graph organizes the sequence of research questions:

`P → Xs → N → V → Xa → Xp → S`

with `E` attached horizontally to every node.

This graph is a **research dependency graph**, not a claim that market reality always follows a one-way causal law. Reflexivity, feedback, reverse causality and simultaneous interactions are allowed and expected.

## Node semantics

| Node | Research object | Core question |
|---|---|---|
| P | Structural Reality Transition | Is the world structurally changing? |
| Xs | Structural Value Capture | If it changes, why should value concentrate here? |
| N | Belief Diffusion Dynamics | How is belief spreading, saturating or reversing? |
| V | Price-Implied Expectations | How much future is already embedded in price? |
| Xa | Conditional Tail State | How are conditional right/left tails changing? |
| Xp | Payoff Geometry | Does the chosen instrument capture the desired asymmetry? |
| S | Portfolio Survival | If wrong, does the system preserve the right to compound? |

## E horizontalization

Every node may emit claims. Every claim must be independently inspectable through an `EvidenceClaim`.

`E` is therefore not a final score or a separate vertex. It is the epistemic control plane over the entire graph.

## State representation

The machine-readable canonical state should be a `ResearchStateVector` containing typed node states and evidence-claim references. Human labels are derived projections.

## Reflexive edges

The graph permits explicit reflexive annotations, for example:

- price → narrative contagion;
- narrative → capex;
- capex → technological diffusion;
- price → financing capacity;
- financing capacity → issuer survival;
- market stress → correlation and liquidity.

Any such edge must be represented as a hypothesis or evidence-backed mechanism, not silently assumed.
