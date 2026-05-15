# Dominium Existing Tool Preflight

Dominium has mature existing governance/tool systems:

- XStack: `scripts/dev/gate.py`, `tools/xstack/**`, `data/registries/xstack_components.json`.
- AuditX: `tools/auditx/**`, `docs/audit/auditx/**`, `data/registries/auditx_groups.json`.
- RepoX: `repo/repox/**`, `scripts/repox/**`, `scripts/ci/check_repox_rules.py`.
- TestX: `tools/xstack/testx/**`, `tools/xstack/testx_all.py`, `data/registries/testx_groups.json`.
- Build/validation: `CMakeLists.txt`, `CMakePresets.json`, `validation/validation_engine.py`, `tools/ci/**`, `scripts/verify_*.py`.

Q50 must not delete, rename, move, or absorb these systems. Later work should use:

`discover -> classify -> wrap -> adapt -> migrate -> retire with evidence`

Detailed evidence: `.aide/queue/DOMINIUM-AIDE-FRESH-PREFLIGHT-01/evidence/existing-tool-systems.md`.
