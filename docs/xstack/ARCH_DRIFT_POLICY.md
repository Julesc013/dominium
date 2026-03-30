Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-7
Replacement Target: superseded by a later explicit architecture-update governance revision only

# Architecture Drift Policy

Xi-6 froze the architecture graph. Xi-7 makes intentional change explicit and accidental drift actionable.

## Intentional Architecture Changes

To change the frozen architecture graph:

1. prepare a ControlX plan with `python -B tools/controlx/tool_plan_arch_change.py --repo-root .`
2. attach the required tag: `ARCH-GRAPH-UPDATE`
3. update `data/architecture/architecture_graph.v1.json` and companion Xi-6 artifacts deliberately
4. pass the `FULL` Xi-7 CI profile

## New Modules

Adding a new module requires:

1. update `data/architecture/module_registry.v1.json`
2. update `data/architecture/architecture_graph.v1.json`
3. pass `STRICT`
4. pass `FULL`

## New Dependencies

Adding a new dependency requires:

1. update `data/architecture/module_boundary_rules.v1.json`
2. verify the dependency remains constitutionally valid
3. pass `STRICT`
4. pass `FULL`

## Prompt Governance

- prompts are untrusted
- CI is authoritative
- bad prompt output must be rejected by RepoX, AuditX, TestX, or validation gates before merge

## Review Standard

- architecture drift without `ARCH-GRAPH-UPDATE` is invalid
- boundary changes without updated rules are invalid
- duplicate semantic engines are invalid
- new module roots without registration are invalid
