Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Task: AIDE-CAPABILITY-REALITY-LEDGER-01
Result: PASS_WITH_WARNINGS
Stability: provisional
Binding Sources: `.aide/policy/workflow_law.md`, `.aide/policy/dev_main_policy.md`, `.aide/policy/checkpoint_loop_law.md`, `.aide/schema/capability_reality_record.schema.json`, `.aide/ledgers/capability_reality.jsonl`

# AIDE-CAPABILITY-REALITY-LEDGER-01

## Status

`PASS_WITH_WARNINGS`

This task defines the minimum AIDE Capability Reality Ledger so future docs,
queues, audits, Workbench projections, and agents do not overstate
implementation status.

It ran in parallel-lane mode. Coordinator update deferred to
checkpoint/coordinator task.

## Baseline

| Field | Value |
| --- | --- |
| branch | `main` |
| baseline commit | `acebb0f4f aide: define checkpoint loop policy` |
| worktree at intake | clean |
| coordinator state | latest queue/status still points at earlier AIDE tasks |
| full CTest | not run; T4/full-gate debt |

## Files Inspected

- `git status --short --branch`
- `git log --oneline -n 12`
- `.aide/queue/current.toml`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/PRODUCT_SPINE_REVIEW_01.md`
- `docs/repo/audits/AIDE_WORKFLOW_LAW_01.md`
- `docs/repo/audits/AIDE_WORKUNIT_SCHEMA_01.md`
- `docs/repo/audits/AIDE_DEV_MAIN_POLICY_01.md`
- `docs/repo/audits/AIDE_CHECKPOINT_LOOP_01.md`
- `docs/repo/audits/PACKAGE_MOUNT_SLICE_01.md`
- `docs/repo/audits/REPLAY_PROOF_SLICE_01.md`
- `docs/repo/audits/BAREBONES_CLIENT_SHELL_01.md`
- `docs/repo/audits/WORKBENCH_VALIDATION_SLICE_01.md`
- `docs/repo/audits/COMMAND_RESULT_VIEW_SLICE_01.md`
- `docs/repo/audits/CAPABILITY_REFUSAL_LAW_01.md`
- `docs/repo/audits/PROVIDER_MODEL_01.md`
- `docs/repo/audits/MODULE_COMPOSITION_LAW_01.md`
- `docs/repo/audits/PUBLIC_SURFACE_REGISTRY_01.md`
- `.aide/policy/workflow_law.md`
- `.aide/policy/dev_main_policy.md`
- `.aide/policy/checkpoint_loop_law.md`
- `.aide/schema/work_unit.schema.json`
- `.aide/schema/evidence_packet.schema.json`
- `.aide/schema/warning_disposition.schema.json`
- `.aide/schema/capability_reality_record.schema.json`
- `contracts/capability/capability.registry.json`
- `contracts/provider/provider.registry.json`
- `contracts/public_surface/**`
- `contracts/workbench/workbench_surface.contract.toml`
- `contracts/platform/renderer_portability.matrix.json`
- `docs/runtime/render/SOFTWARE_RENDERER.md`
- `docs/runtime/render/README.md`
- `runtime/render/software/d_gfx_soft.c`
- `docs/architecture/native_architecture_policy.md`
- existing AIDE policy/schema/fixture/validator conventions under `.aide/**`
  and `tools/aide/**`

## Files Changed

- `.aide/schema/capability_reality_record.schema.json`
- `.aide/ledgers/capability_reality.jsonl`
- `.aide/policy/capability_reality_policy.md`
- `.aide/fixtures/capability_reality/valid_planned_capability.json`
- `.aide/fixtures/capability_reality/valid_fixture_only_capability.json`
- `.aide/fixtures/capability_reality/valid_tested_capability.json`
- `.aide/fixtures/capability_reality/invalid_release_supported_without_evidence.json`
- `.aide/fixtures/capability_reality/invalid_unknown_status.json`
- `tools/aide/validate_capability_reality.py`
- `.aide/reports/capability-reality-summary.md`
- `docs/repo/audits/AIDE_CAPABILITY_REALITY_LEDGER_01.md`

No product/runtime behavior changed.

## Schema, Ledger, And Policy Created

- `capability_reality_record.schema.json` now defines the full record shape,
  exact status vocabulary, category vocabulary, support-claim vocabulary, and
  required evidence/status fields.
- `capability_reality.jsonl` seeds a current-state ledger with 15 high-value
  AIDE/product-spine/runtime-blocker capability records.
- `capability_reality_policy.md` defines status semantics, transitions,
  evidence requirements, support-claim rules, relationships to public surface,
  component/portability, module/provider/app, package/pack, and Workbench
  surfaces, plus update rules after future slices.

## Seed Capabilities Recorded

| capability_id | status | support claim | Key guard |
| --- | --- | --- | --- |
| `capability.aide.workflow_law` | `specified` | `internal` | Current stale validator prevents a fresh tested claim. |
| `capability.aide.workunit_schema` | `tested` | `internal` | Schema/fixture support only; no scheduler or automation. |
| `capability.aide.dev_main_policy` | `tested` | `internal` | Policy validated; no branch automation. |
| `capability.aide.checkpoint_loop` | `tested` | `internal` | Checkpoint policy validated; no merge/promotion automation. |
| `capability.package.mount_planning` | `tested` | `dev` | No runtime package mount. |
| `capability.package.runtime_mount` | `planned` | `none` | Not implemented. |
| `capability.replay.command_proof` | `tested` | `dev` | No full game/world/save replay. |
| `capability.client.barebones_shell` | `exposed` | `experimental` | No playable client, renderer, HUD, package runtime, or gameplay. |
| `capability.workbench.validation_projection` | `tested` | `dev` | No Workbench shell. |
| `capability.workbench.shell` | `planned` | `none` | Not implemented. |
| `capability.provider.runtime` | `specified` | `internal` | Provider model exists; runtime resolver/loading not implemented. |
| `capability.module.runtime_loader` | `specified` | `internal` | Module descriptors exist; runtime loader not implemented. |
| `capability.renderer.software` | `stubbed` | `internal` | Software renderer code exists, but no product/golden/release proof. |
| `capability.native_gui` | `planned` | `none` | Not implemented. |
| `capability.gameplay.domain_runtime` | `planned` | `none` | Not implemented. |

## Validator Added

`tools/aide/validate_capability_reality.py` validates:

- schema exists and carries exact status/category/support vocabularies
- seed ledger parses as JSONL
- minimum seed records exist
- duplicate capability IDs are rejected
- statuses are valid
- `release_supported` records require evidence and `support_claim = "release"`
- `planned`, `specified`, `fixture_only`, and `stubbed` cannot claim release
  support
- blocked runtime capabilities are not marked `implemented`, `tested`,
  `exposed`, or `release_supported`
- valid fixtures pass
- invalid fixtures fail
- optional summary generation

## Human-Readable Summary

`.aide/reports/capability-reality-summary.md` was generated from the seed
ledger and lists capability ID, category, status, support claim, blocking gaps,
and next action.

## Validation Commands Run

| Command | Result |
| --- | --- |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS with known review-ref warnings |
| `python -m tools.aide.doctor` | unavailable; module not present |
| `python -m tools.aide.validate` | unavailable; module not present |
| `py -3 tools/aide/validate_capability_reality.py --repo-root . --summary-out .aide/reports/capability-reality-summary.md` | PASS |
| `python -m json.tool .aide/schema/capability_reality_record.schema.json` | PASS |
| JSONL parse check for `.aide/ledgers/capability_reality.jsonl` | PASS after rerun with PowerShell-safe command |
| `git diff --check` | PASS |

`py -3 .aide/scripts/aide_lite.py pack --task "AIDE-CAPABILITY-REALITY-LEDGER-01"`
was not run because it writes `.aide/context/latest-task-packet.md`, and this
parallel-lane task does not own coordinator/latest packet mutation.

Full CTest and broad builds were not run.

## Warnings Preserved

- Full CTest remains T4/full-gate debt.
- Dependency-direction strict warnings remain known prior warning debt with
  zero-violation evidence.
- Latest queue/status packets remain stale relative to recent parallel-lane
  AIDE policy commits.
- AIDE review-packet reference warnings remain known.
- Stale AuditX output remains known RepoX debt.
- Runtime package mount, provider runtime, runtime module loader, Workbench
  shell, renderer product proof, native GUI, gameplay/domain runtime, and
  release publication remain blocked or unsupported as recorded in the ledger.

## Non-Goals Preserved

No capability runtime, provider runtime, module loader, package runtime,
Workbench shell, renderer implementation, native GUI, gameplay, release
publication, product feature work, full AIDE scheduler, branch automation,
promotion automation, source directory move, broad build, or full CTest was
implemented.

## Next Tasks

- `PRESENTATION-CONTRACT-01`
- `PROJECTION-CONFORMANCE-01`
- `POINTER-WIDTH-SERIALIZATION-AUDIT-01`
- `WORKBENCH-SHELL-READONLY-01` later

Coordinator update deferred to checkpoint/coordinator task.
