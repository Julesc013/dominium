# AIDE Latest Task Packet

## PHASE

Post-product-spine governance hardening.

## GOAL

`AIDE-WORKFLOW-LAW-01` - define the minimum AIDE task operating system law before the next large parallel wave.

The task should cover branch roles, task lifecycle states, blocker taxonomy, work-unit/evidence expectations, repair/resume behavior, and dev/main/checkpoint promotion policy.

## WHY

The post-Foundation product spine is now coherent:

```text
command/result/view proof
-> package mount proof
-> replay/proof proof
-> barebones client shell proof
```

The next risk is coordination, not product capability. AIDE needs explicit law for task branches, shared dev integration, repair work, checkpoint gates, warning policy, and promotion to main before larger parallel work begins.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/current.toml`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/PHASE_REVIEW_02.md`
- `docs/repo/audits/PACKAGE_MOUNT_SLICE_01.md`
- `docs/repo/audits/REPLAY_PROOF_SLICE_01.md`
- `docs/repo/audits/BAREBONES_CLIENT_SHELL_01.md`
- `docs/repo/audits/PRODUCT_SPINE_REVIEW_01.md`
- `.aide/reports/PRODUCT-SPINE-REVIEW-01-summary.md`
- `.aide/reports/latest-warning-disposition.md`

## ALLOWED_PATHS

- `contracts/aide/**` if schemas are introduced
- `docs/aide/**` if AIDE workflow law docs are introduced
- `.aide/queue/**`
- `.aide/context/**`
- `.aide/reports/AIDE-WORKFLOW-LAW-01-*`
- `docs/repo/audits/AIDE_WORKFLOW_LAW_01.md`
- repo status docs only if coordinator closeout requires it

## FORBIDDEN_PATHS

- no product runtime implementation
- no package runtime
- no replay runtime
- no provider runtime
- no runtime module loader
- no Workbench shell
- no renderer/native GUI
- no gameplay/domain implementation
- no release publication
- no force-push or direct main-promotion automation

## IMPLEMENTATION

- Keep the task governance/control-plane focused.
- Define law before automation.
- Prefer schemas and docs that can be validated without live provider/network calls.
- Preserve existing broad feature blockers.
- Do not mutate product/runtime behavior.

## VALIDATION

- AIDE doctor/validate
- docs sanity
- public surface and dependency-direction checks if public surfaces are added
- JSON/TOML parse checks for touched machine-readable files
- fast strict if queue/status or governance surfaces change substantially

## EVIDENCE

- changed files
- task lifecycle and blocker taxonomy refs
- branch/checkpoint/promotion policy refs
- validators run
- known warnings and non-goals

## NON_GOALS

- No product/runtime feature work.
- No live provider/model/network calls.
- No broad Workbench UI.
- No runtime module loader.
- No package/provider/replay runtime.
- No gameplay, renderer, native GUI, or release publication.

## ACCEPTANCE

- Branch roles and promotion gates are explicit.
- Task lifecycle and blocker classes are machine-readable or precisely documented.
- Partial work, repairs, checkpoints, and evidence packets have clear handling rules.
- Development remains non-blocking, while promotion remains evidence-blocked.
- Broad feature blockers remain visible.

## NEXT_AFTER

Expected alternate/follow-up: `PRESENTATION-CONTRACT-01`.

## OUTPUT_SCHEMA

Return compact closeout with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, `WARNINGS`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 650
- budget_status: PASS
