# VERSION-DEPRECATION-LAW-01 Validation

Task: `VERSION-DEPRECATION-LAW-01`

## Initial State

```text
git status --short --branch
## main...origin/main

git rev-parse HEAD
e6527e5d87e50453e4b27c0d96fb9fcf5aa5718e

git rev-parse origin/main
e6527e5d87e50453e4b27c0d96fb9fcf5aa5718e

merge-base checks
origin/main is ancestor of HEAD: yes
HEAD is ancestor of origin/main: yes
```

## AIDE Preconditions

```text
py -3 .aide/scripts/aide_lite.py doctor
PASS

py -3 .aide/scripts/aide_lite.py validate
PASS with existing review-reference warnings

py -3 .aide/scripts/aide_lite.py pack --task "VERSION-DEPRECATION-LAW-01"
PASS; task packet generated and later replaced with VERSION-DEPRECATION-LAW-01-specific packet
```

## Version Validator

```text
python -m py_compile tools/validators/contracts/check_version_deprecation.py
PASS

python tools/validators/contracts/check_version_deprecation.py --repo-root . --strict
version/deprecation law: pass
lifecycle_states: 9
errors: 0
warnings: 0
fixtures: pass valid=3 invalid=4

python tools/validators/contracts/check_version_deprecation.py --repo-root . --json
status: pass
errors: 0
warnings: 0
lifecycle_states_registered: 9

python tools/validators/contracts/check_version_deprecation.py --repo-root . --fixtures
version/deprecation law: pass
lifecycle_states: 9
errors: 0
warnings: 0
fixtures: pass valid=3 invalid=4

python tools/validators/contracts/check_version_deprecation.py --repo-root . --inventory
version/deprecation law: pass
lifecycle_states: 9
errors: 0
warnings: 0
inventory: warning files_scanned=17970 version_like=2479
- artifact_with_version: 8
- command_with_version: 4
- descriptor_with_version: 24
- fixture_schema: 584
- historical_or_audit_lifecycle: 76
- release_surface_with_version: 177
- replacement_policy_with_version: 9
- schema_protocol_with_version: 1593
- surface_with_version: 4
```

## Parse Checks

```text
python -m json.tool <touched versioning/fixture/diagnostic/refusal JSON files>
JSON parse touched files: PASS

python tools/validators/contracts/check_version_deprecation.py --repo-root . --strict > $null
TOML parse via version validator: PASS
```

## Cross Validators

```text
python tools/validators/repo/check_replacement_packet.py --repo-root . --strict
Dominium replacement protocol validation
status: pass
replacement_kinds: 19
replacement_statuses: 10
findings: 0
fixtures: valid=4 invalid=4 status=pass

python tools/validators/contracts/check_module_descriptors.py --repo-root . --strict
module descriptors: pass
module_kinds: 12
errors: 0
warnings: 0

python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict
workbench workspaces: pass
errors: 0
warnings: 0

python tools/validators/contracts/check_app_descriptors.py --repo-root . --strict
app descriptors: pass
errors: 0
warnings: 0

python tools/validators/contracts/check_provider_model.py --repo-root . --strict
provider model: pass
providers: 5
provider_kinds: 15
errors: 0
warnings: 0

python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict
capability/refusal: pass
capabilities: 13
refusal_codes: 29
errors: 0
warnings: 0

python tools/validators/contracts/check_schema_protocol_evolution.py --repo-root . --strict
schema/protocol evolution: pass
errors: 0
warnings: 0

python tools/validators/contracts/check_artifact_identity.py --repo-root . --strict
artifact identity: pass
artifact_kinds: 23
lifecycle_states: 11
errors: 0
warnings: 0

python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict
diagnostics registry: pass
diagnostic_codes: 70
severities: 7
categories: 26
errors: 0
warnings: 0

python tools/validators/contracts/check_command_surface.py --repo-root . --strict
command_surface: pass
commands: 5
errors: 0
warnings: 0

python tools/validators/repo/check_public_surface.py --repo-root . --strict
public surface validation: PASS
surfaces: 133 stable: 2 kinds: 25 stability_classes: 12

python tools/validators/repo/check_dependency_directions.py --repo-root . --strict --max-findings 5
dependency direction validation: FAIL (16363 files scanned, 358 violations, 38 warnings)
Known existing dependency-direction debt from DEPENDENCY-DIRECTION-01; not hidden by this task.

python tools/validators/abi/check_public_headers.py --repo-root . --strict
public header ABI validation: PASS
headers: 375 errors: 0 warnings: 2851
Known provisional ABI warning debt; no ABI is promoted stable.
```

## Repo And Supplemental Validators

```text
python tools/validators/check_repo_layout.py --repo-root . --strict
Strict-mode result: pass

python tools/validators/check_root_allowlist.py --repo-root . --strict
Strict-mode result: pass

python tools/validators/check_distribution_layout.py --repo-root . --strict
Strict-mode result: pass

python tools/validators/check_component_matrices.py --repo-root . --strict
Strict-mode result: pass

python scripts/verify_docs_sanity.py --repo-root .
Docs sanity OK.

python scripts/verify_build_target_boundaries.py --repo-root .
BOUNDARY-OK: build boundary checks passed

python scripts/verify_ui_shell_purity.py --repo-root .
UI shell purity OK.

python scripts/verify_abi_boundaries.py --repo-root .
ABI boundary check OK.

python tools/validators/ci/tool_identity_fingerprint.py --repo-root . --output docs/archive/audit/identity_fingerprint.json
PASS; identity fingerprint refreshed after CANON_INDEX update
```

## Fast Strict

```text
python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/VERSION-DEPRECATION-LAW-01-fast-strict.json --md-out .aide/reports/VERSION-DEPRECATION-LAW-01-fast-strict.md
summary: status=PASS commands=32 elapsed_seconds=308.563
```

First fast strict attempt failed at `t1.repox_strict` because
`docs/architecture/versioning_and_deprecation.md` was listed in CANON_INDEX but
had `Status: DERIVED`. The doc status was corrected to `CANONICAL`, the
identity fingerprint was refreshed, and the rerun passed.

## Git Checks

```text
git diff --check
PASS

git diff --cached --check
PASS
```
