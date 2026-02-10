Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Gate Autonomy Policy

RepoX and TestX must self-canonicalize their tool environment. Manual `PATH` setup is optional for convenience only.

## Canonical Contract

- Canonical tools are discovered from `dist/sys/<platform>/<arch>/bin/tools/`.
- RepoX prepends this directory to its own process `PATH` at run start.
- TestX tool-invocation tests use the same canonicalization helpers.
- Missing canonical tools directory is a hard failure (`INV-TOOLS-DIR-MISSING`) with remediation guidance.

## Manual vs Autonomous Invocation

- Supported direct invocation (no shell pre-step required):
  - `python scripts/ci/check_repox_rules.py --repo-root .`
  - `cmake --build out/build/vs2026/verify --config Debug --target testx_all`
- Optional convenience pre-step:
  - `scripts/dev/env_tools.*`

## Canonical Gate Runner

Use `scripts/dev/gate.py` (or `python scripts/dev/dev.py gate ...`) as the preferred entrypoint:

- `gate dev`
- `gate verify`
- `gate dist`
- `gate doctor`
- `gate remediate`

Behavior:

- self-canonicalizes `PATH`
- runs RepoX, strict build, and TestX in one flow
- attempts deterministic tool-discovery remediation when `INV-TOOLS-DIR-MISSING` occurs
- writes remediation artifacts to `docs/audit/remediation/...`

## Remediation Discipline

- Mechanical failures are remediated automatically.
- Remediation follows `docs/governance/REMEDIATION_STATE_MACHINE.md`.
- Semantic escalations follow `docs/governance/SEMANTIC_ESCALATION_POLICY.md`.
