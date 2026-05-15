# XStack / AuditX / RepoX / TestX

Status: needs_review

Do not delete, rename, move, or retire XStack/AuditX/RepoX/TestX until useful checks are wrapped or migrated with evidence.

## Paths Found

### XStack

- `docs/XSTACK.md`
- `tools/xstack/**`
- `data/registries/xstack_components.json`
- `scripts/dev/gate.py`

### AuditX

- `tools/auditx/**`
- `tools/xstack/auditx/**`
- `docs/audit/auditx/**`
- `data/registries/auditx_groups.json`

### RepoX

- `repo/repox/**`
- `scripts/repox/**`
- `scripts/ci/check_repox_rules.py`
- `tools/xstack/repox/**`
- `docs/audit/repox/**`

### TestX

- `tools/xstack/testx/**`
- `tools/xstack/testx_all.py`
- `scripts/dev/run_xstack_group_tests.py`
- `scripts/dev/testx_proof_engine.py`
- `data/registries/testx_groups.json`
- `data/registries/testx_suites.json`
- `docs/audit/testx/**`
- `tests/testx/**`

## Likely Capabilities

- XStack: validate, audit, repo_policy, docs, build/test orchestration.
- AuditX: audit, docs, repo_policy, validation evidence.
- RepoX: repo_policy, validate, security-sensitive governance.
- TestX: test, validate, proof/evidence execution.

## Immediate Safety Posture

- Preserve all old names and locations.
- Do not run broad legacy commands in Q51.
- Do not migrate or retire any old ontology.
- Treat old generated reports and registries as evidence until a stronger source promotes them.

## Future Wrapper / Adaptation Plan

- Start with read-only status and dry-run wrappers.
- Require a command contract for inputs, outputs, side effects, timeout, and generated evidence path before enabling execution.
- Keep wrappers additive and compatibility-preserving.
- Future migration or retirement requires evidence that useful checks are wrapped or migrated and that references are updated through an explicit reviewed phase.

## What Not To Do

- Do not classify these systems as junk.
- Do not delete old tool files because names are transitional.
- Do not rewrite references to new AIDE command names in Q51.
- Do not execute unknown TestX/XStack/AuditX/RepoX commands.
