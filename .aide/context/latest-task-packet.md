# AIDE Latest Task Packet

## PHASE

Post-package-mount product spine.

## GOAL

`REPLAY-PROOF-SLICE-01` - prove one deterministic command/result/evidence
replay/proof path without implementing full game replay, save runtime, world
runtime, package runtime, provider runtime, gameplay, renderer, native GUI, or
release publication.

## WHY

`PACKAGE-MOUNT-SLICE-01` proved one fixture-level package/profile mount decision
and derived lock/report/evidence shape. The next gap is replay/proof:

```text
deterministic operation
-> evidence/proof record
-> replay or verification
-> same hash/result or typed mismatch refusal
```

## CONTEXT_REFS

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/PACKAGE_MOUNT_SLICE_01.md`
- `.aide/reports/PACKAGE-MOUNT-SLICE-01-summary.md`
- `.aide/queue/current.toml`
- `contracts/command/**`
- `contracts/artifact/**`
- `contracts/diagnostics/**`
- `contracts/refusal/**`
- `contracts/composition/**`
- `contracts/lock/**`
- `contracts/replay/**` if present

## ALLOWED_PATHS

- `contracts/replay/**`
- `contracts/proof/**`
- `contracts/artifact/**`
- `contracts/command/**`
- `contracts/diagnostics/**`
- `contracts/refusal/**`
- `tests/contract/replay/**`
- `tests/contract/proof/**`
- `tests/app/**`
- `tools/validators/contracts/**`
- `docs/repo/audits/REPLAY_PROOF_SLICE_01.md`
- `docs/architecture/**`
- `.aide/reports/REPLAY-PROOF-SLICE-01-*`

## FORBIDDEN_PATHS

- broad game replay runtime
- save runtime
- world runtime
- gameplay/domain implementation
- renderer/native GUI
- package runtime
- provider runtime
- release publication
- CMake targets

## IMPLEMENTATION

- Keep the proof command-driven and deterministic.
- Prefer an existing narrow command/result path if available.
- The replay/proof artifact must be evidence, not source truth.
- A mismatch must produce typed diagnostics/refusals, not silent fallback.
- Do not claim full replay runtime, save runtime, or game simulation support.

## VALIDATION

- targeted replay/proof validators and tests added by the slice
- command, diagnostic, refusal, artifact, public-surface, and dependency checks
- docs/build/UI/ABI sanity checks where touched
- AIDE doctor/validate
- `git diff --check`
- fast strict if touched inputs affect fast-strict scope

## EVIDENCE

- changed files
- command/result/proof IDs used
- replay/proof fixture refs
- validators and tests run
- warnings and deferred runtime gaps

## NON_GOALS

- No broad replay runtime.
- No save/world/gameplay runtime.
- No package runtime.
- No provider runtime.
- No Workbench shell.
- No renderer/native GUI.
- No release publication.

## ACCEPTANCE

- One deterministic command/result/evidence proof path can be verified or
  replay-checked with a stable result/hash.
- Mismatch/refusal behavior is typed.
- Broad feature blockers remain explicit.

## NEXT_AFTER

Expected alternate/follow-up: `BAREBONES-CLIENT-SHELL-01`.

## OUTPUT_SCHEMA

Return compact closeout with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`,
`VALIDATION`, `WARNINGS`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 900
- budget_status: PASS
