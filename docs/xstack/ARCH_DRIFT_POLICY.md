Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-8
Replacement Target: later explicit policy revision only

# Architecture Drift Policy

Intentional architecture and repository-structure change requires deliberate process rather than prompt drift.

## Architecture Graph Updates

1. prepare a ControlX architecture plan with `python -B tools/controlx/tool_plan_arch_change.py --repo-root .`
2. attach `ARCH-GRAPH-UPDATE`
3. update the Xi-6 frozen architecture artifacts deliberately
4. pass the `FULL` CI profile

## New Modules

1. update `data/architecture/module_registry.v1.json`
2. update `data/architecture/architecture_graph.v1.json`
3. update `data/architecture/repository_structure_lock.json` if a new top-level root is involved
4. pass `STRICT` and `FULL`

## New Dependencies

1. update `data/architecture/module_boundary_rules.v1.json`
2. preserve constitutional architecture
3. pass `STRICT` and `FULL`

## Repository Structure Updates

- top-level roots are frozen by Xi-8 lock hash `f419ce454578b60f2229d909e78e90cc1bb9dfd16d3ea721a8f7a185c13774b5`
- sanctioned source-like roots may change only through explicit Xi-5/Xi-8 policy refresh
- generic `src/` and `source/` dumping grounds remain forbidden

Prompts are untrusted.
CI and frozen artifacts are authoritative.
