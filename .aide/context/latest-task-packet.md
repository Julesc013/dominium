# AIDE Latest Task Packet

## PHASE

Post-Foundation product spine after `PHASE-REVIEW-02`.

## GOAL

`PACKAGE-MOUNT-SLICE-01` - prove one narrow, fixture-driven package/profile/content mount decision without implementing broad package runtime.

## WHY

Foundation Lock remains `PASS_WITH_WARNINGS`. The post-Foundation wave now has
command/result/refusal, service conformance, document/patch/transaction,
project graph, composition resolver, doctrine recovery, Workbench validation,
and command-result-view projection proofs. The next product-spine gap is a
small package mount proof that consumes existing composition, artifact,
capability/refusal, diagnostics, evidence, and trust law.

## CONTEXT_REFS

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/PHASE_REVIEW_02.md`
- `docs/repo/audits/COMPOSITION_RESOLVER_LAW_01.md`
- `docs/repo/audits/COMMAND_RESULT_VIEW_SLICE_01.md`
- `contracts/composition/**`
- `contracts/artifact/**`
- `contracts/capability/**`
- `contracts/refusal/**`
- `contracts/diagnostics/**`
- `contracts/lock/**`
- `contracts/trust/**`
- `.aide/queue/current.toml`
- `.aide/context/latest-context-packet.md`

## EXPECTED_OUTPUT

- pack mount plan fixture
- lock/report fixture
- capability/refusal report
- diagnostics/evidence packet
- CLI/headless validation command or fixture proof if command runtime remains out of scope

## ALLOWED_PATHS

- contract and fixture additions needed for a narrow mount proof
- documentation and AIDE evidence for `PACKAGE-MOUNT-SLICE-01`
- targeted validators and tests for composition/package/trust/capability surfaces

## FORBIDDEN_PATHS

- broad package runtime
- mod loader
- arbitrary pack execution
- provider runtime
- runtime module loader
- Workbench shell/UI
- renderer or native GUI
- gameplay/domain implementation
- release publication
- CMake target additions

## IMPLEMENTATION

- Treat composition lockfiles as derived evidence, not source truth.
- Keep missing capabilities as explicit refusals or degradations.
- Use existing composition, artifact, capability/refusal, diagnostics, and trust laws.
- Do not make packs executable.
- Do not promote package runtime implementation claims.

## VALIDATION

- targeted package/composition/trust/capability validators
- public surface and dependency-direction strict validators
- docs/build/UI/ABI sanity checks where touched
- AIDE doctor/validate
- `git diff --check`
- fast strict if touched inputs affect fast-strict scope

## EVIDENCE

- changed files
- package/profile/content artifact IDs used
- mount decision, lock/report, refusal, diagnostic, and evidence fixture refs
- validators and tests run
- warnings and deferred runtime gaps

## NON_GOALS

- No broad package runtime.
- No provider runtime.
- No runtime module loader.
- No Workbench shell.
- No rendered GUI.
- No native GUI.
- No gameplay.
- No release publication.

## ACCEPTANCE

- One pack/profile/content artifact can be resolved into a fixture-level mount
  decision, lock/report, refusals/degradations, diagnostics, and evidence.
- Broad feature blockers remain explicit.

## NEXT_AFTER

Expected alternate/follow-up: `REPLAY-PROOF-SLICE-01`.

## OUTPUT_SCHEMA

Return compact closeout with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`,
`VALIDATION`, `WARNINGS`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 1000
- budget_status: PASS
