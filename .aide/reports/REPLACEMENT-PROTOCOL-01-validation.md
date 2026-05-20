# REPLACEMENT-PROTOCOL-01 Validation

## Initial Sync

```text
git status --short --branch
## main...origin/main

git fetch --all --prune
<no output>

git rev-parse HEAD
5fc894a107d46f8799f86a8b72ce9b5acab6b588

git rev-parse origin/main
5fc894a107d46f8799f86a8b72ce9b5acab6b588

git merge-base --is-ancestor origin/main HEAD
origin_ancestor_head=yes

git merge-base --is-ancestor HEAD origin/main
head_ancestor_origin=yes
```

## AIDE

```text
py -3 .aide/scripts/aide_lite.py doctor
status: PASS

py -3 .aide/scripts/aide_lite.py validate
status: PASS
warnings:
- review packet review ref missing: .aide/verification/latest-verification-report.md
- review packet review ref missing: .aide/verification/review-decision-policy.yaml

py -3 .aide/scripts/aide_lite.py pack --task "REPLACEMENT-PROTOCOL-01"
action: written
budget_status: PASS
```

## Replacement Validator

```text
python -m py_compile tools/validators/repo/check_replacement_packet.py
PASS

python tools/validators/repo/check_replacement_packet.py --repo-root . --strict
Dominium replacement protocol validation
status: pass
replacement_kinds: 19
replacement_statuses: 10
findings: 0
fixtures: valid=4 invalid=4 status=pass

python tools/validators/repo/check_replacement_packet.py --repo-root . --fixtures
Dominium replacement protocol validation
status: pass
replacement_kinds: 19
replacement_statuses: 10
findings: 0
fixtures: valid=4 invalid=4 status=pass

python tools/validators/repo/check_replacement_packet.py --repo-root . --json
status: pass
findings: 0
replacement_kinds_registered: 19
replacement_statuses_registered: 10

python tools/validators/repo/check_replacement_packet.py --repo-root . --inventory
status: pass
files_scanned: 17942
replacement_like: 1824
inventory_status: warning
```

## Touched Registry Checks

```text
python tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict
diagnostics registry: pass
diagnostic_codes: 62
severities: 7
categories: 26
errors: 0
warnings: 0

python tools/validators/contracts/check_capability_refusal.py --repo-root . --strict
capability/refusal: pass
capabilities: 13
refusal_codes: 23
errors: 0
warnings: 0

python tools/validators/repo/check_public_surface.py --repo-root . --strict
public surface validation: PASS
surfaces: 121 stable: 2 kinds: 25 stability_classes: 12

python -m json.tool <touched json files>
json_parse=pass

python -m json.tool <final touched json files>
json_parse_final=pass
```

## Existing Contract Validators

```text
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

python tools/validators/contracts/check_command_surface.py --repo-root . --strict
command_surface: pass
commands: 5
errors: 0
warnings: 0
```

## Repo And Supplemental Validators

```text
python tools/validators/repo/check_dependency_directions.py --repo-root . --strict --max-findings 5
dependency direction validation: FAIL (16335 files scanned, 358 violations, 38 warnings)
first findings:
- apps/client/local_server/local_server_controller.py runtime_to_tools
- apps/server/server_boot.py runtime_to_tools

python tools/validators/abi/check_public_headers.py --repo-root . --strict
public header ABI validation: PASS
headers: 375 errors: 0 warnings: 2851

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

python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT --proof-manifest-out .aide/reports/FAST-STRICT-TEST-TIER-01-repox-proof-manifest.json --profile-out .aide/reports/FAST-STRICT-TEST-TIER-01-repox-profile.json
RepoX governance rules OK.
```

## Fast Strict

First run:

```text
python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/REPLACEMENT-PROTOCOL-01-fast-strict.json --md-out .aide/reports/REPLACEMENT-PROTOCOL-01-fast-strict.md
summary: status=FAIL commands=29 elapsed_seconds=197.344
failure: t1.repox_strict
findings:
- INV-DOC-STATUS-HEADER for replacement docs/audit files
```

Corrective action:

```text
Added status headers to replacement docs and audit.
Added docs/architecture/replacement_protocol.md to docs/architecture/CANON_INDEX.md.
Regenerated docs/archive/audit/identity_fingerprint.json.
python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT ...
RepoX governance rules OK.
```

Final run:

```text
python tools/test/run_fast_strict.py --repo-root . --json-out .aide/reports/REPLACEMENT-PROTOCOL-01-fast-strict.json --md-out .aide/reports/REPLACEMENT-PROTOCOL-01-fast-strict.md
summary: status=PASS commands=32 elapsed_seconds=301.437
```

## Git Checks

```text
git diff --check
PASS

py -3 .aide/scripts/aide_lite.py commit check --latest
Initial replacement commit: FAIL
reason: validation section did not record explicit PASS/WARN/FAIL/NOT RUN outcome tokens.
Disposition: recorded in follow-up commit without amending the original commit.
```
