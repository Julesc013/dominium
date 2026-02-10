Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# RepoX Rulesets

RepoX rules are organized into policy packs under `repo/repox/rulesets/`.

## Rulesets

- `repox/core`: non-negotiable invariants (determinism, canon state, process-only mutation, guard runtime).
- `repox/data_first`: schema/data anchoring and anti-silent-default enforcement.
- `repox/abstraction`: anti-one-off and anti-duplication pressure with ratchet support.
- `repox/ui_parity`: command metadata, UI canonical binding, capability matrix integrity.
- `repox/security`: epistemic and anti-cheat checks.
- `repox/change_shape`: repository-shape and ambiguity checks.
- `repox/derived_artifacts`: machine-generated contract surfaces (e.g., solver registry).
- `repox/packaging`: package/distribution governance for `dompkg` and `dist/*`.

Each rule record defines:

- `rule_id`
- `severity` (`WARN` or `FAIL`)
- `scope_paths`
- `documentation`
- `exemption_policy` (`deny` or `allow_with_expiry`)
- optional `ratchet_after` (for WARN -> FAIL progression)

## Exemptions

- Sidecar exemptions: `repo/repox/repox_exemptions.json`.
- Inline exemptions: `@repox:allow(<rule_id>) reason="..." expires="YYYY-MM-DD"`.
- Core rules use `exemption_policy=deny`.
- Non-core exemptions must include reason and expiry; expired exemptions fail RepoX.

## RepoX/TestX Cooperation

- RepoX emits proof requirements to `build/proof_manifests/repox_proof_manifest.json`.
- TestX validates the manifest via `tests/invariant/proof_manifest_tests.py`.
- Required proofs are dynamic and based on changed files in the current diff.
- A required proof missing from TestX is a blocking failure.

See `docs/governance/TESTX_PROOF_MODEL.md` for runtime proof semantics.

## Clip/Voice Artifact Governance

- Bug observations are ingested into `data/logs/bugreports/` using `tools/bugreport/ingest.py`.
- Resolution requires either:
  - `regression_test`, or
  - `deferred_reason`.
- RepoX enforces this with `INV-BUGREPORT-RESOLUTION`.

See `docs/dev/CLIP_DRIVEN_DEVELOPMENT.md` for the workflow.

## Rule References

- `INV-REPOX-STRUCTURE`
- `INV-LOCKLIST-FROZEN`
- `INV-CANON-STATE`
- `INV-CANON-INDEX`
- `INV-CANON-NO-SUPERSEDED`
- `INV-CANON-NO-HIST-REF`
- `INV-CANON-CODE-REF`
- `INV-DOC-STATUS-HEADER`
- `INV-TOOL-NAME-ONLY`
- `INV-TOOLS-DIR-EXISTS`
- `INV-TOOLS-DIR-MISSING`
- `INV-TOOL-UNRESOLVABLE`
- `INV-REMEDIATION-PLAYBOOKS`
- `INV-DET-NO-ANON-RNG`
- `INV-DET-NO-WALLCLOCK`
- `INV-FP-AUTH-BAN`
- `INV-NO-HARDCODED-CONTENT`
- `INV-ENUM-NO-OTHER`
- `INV-NO-RAW-PATHS`
- `INV-PROCESS-REGISTRY`
- `INV-PROCESS-RUNTIME-ID`
- `INV-PROCESS-GUARD-RUNTIME`
- `INV-PROCESS-REGISTRY-IMMUTABLE`
- `INV-REPORT-CANON`
- `INV-SCHEMA-VERSION-BUMP`
- `INV-SCHEMA-MIGRATION-ROUTES`
- `INV-SCHEMA-NO-IMPLICIT-DEFAULTS`
- `INV-SCHEMA-VERSION-REF`
- `INV-CAPABILITY-PACK-METADATA`
- `INV-PREALPHA-PACK-ISOLATION`
- `INV-BUGREPORT-RESOLUTION`
- `DATA_FIRST_BEHAVIOR`
- `NO_SILENT_DEFAULTS`
- `SCHEMA_ANCHOR_REQUIRED`
- `NEW_FEATURE_REQUIRES_DATA_FIRST`
- `INV-MAGIC-NO-LITERALS`
- `NO_SINGLE_USE_CODE_PATHS`
- `DUPLICATE_LOGIC_PRESSURE`
- `INV-COMMAND-CAPABILITY-METADATA`
- `INV-UI-CANONICAL-COMMAND`
- `INV-CAMERA-BLUEPRINT-METADATA`
- `INV-RUNTIME-CAPABILITY-GUARDS`
- `INV-CLIENT-CANONICAL-BRIDGE`
- `INV-CAPABILITY-MATRIX`
- `INV-OBSERVER-FREECAM-ENTITLEMENT`
- `INV-RENDER-NO-TRUTH-ACCESS`
- `INV-CAPABILITY-NO-LEGACY-GATING-TOKENS`
- `INV-SOLVER-CONTRACTS`
- `INV-REPOX-AMBIGUOUS-DIRS`
- `INV-ROOT-MODULE-SHIM`
- `INV-REPOX-RULESET-MISSING`
- `INV-REPOX-EXEMPTION-POLICY`
- `INV-PKG-MANIFEST-FIELDS`
- `INV-PKG-CAPABILITY-METADATA`
- `INV-PKG-SIGNATURE-POLICY`
- `INV-DIST-SYS-SHIPPING`
- `INV-DERIVED-PKG-INDEX-FRESHNESS`
- `INV-PLATFORM-REGISTRY`
- `INV-PLATFORM-ID-CANONICAL`
- `INV-DIST-SYS-DERIVED`
- `INV-PRODUCT-GRAPH-CONSTRAINTS`
- `INV-MODE-BACKEND-REGISTRY`
- `INV-MODE-BACKEND-SELECTION`
- `INV-PORTABLE-RUN-CONTRACT`
- `INV-BUILD-PRESET-CONTRACT`
- `INV-DIST-RELEASE-LANE-GATE`

## Key Rule Notes

### INV-ROOT-MODULE-SHIM

- Fails when a tracked top-level directory behaves as a redirect-only CMake shim.
- Fails for top-level `shared_*` module directories.
- Prevents reintroduction of ad-hoc root module wrappers instead of using canonical subsystem paths.

### INV-TOOL-NAME-ONLY / INV-TOOLS-DIR-EXISTS / INV-TOOLS-DIR-MISSING / INV-TOOL-UNRESOLVABLE

- Enforces canonical tool invocation by name only.
- Enforces in-process PATH canonicalization to `dist/sys/<platform>/<arch>/bin/tools`.
- Enforces explicit missing-directory failure (`INV-TOOLS-DIR-MISSING`) with remediation hint.
- Enforces discoverability probes for required canonical tools at RepoX runtime.
- Detailed policy: `docs/governance/REPOX_TOOL_RULES.md`.

### INV-REMEDIATION-PLAYBOOKS

- Fails when remediation playbook schema/registry are missing or invalid.
- Fails when required blocker playbooks are missing.
- Enforces deterministic strategy class declarations for autonomous gate remediation.

### INV-PLATFORM-ID-CANONICAL

- Fails when non-canonical platform aliases appear in platform registries, package manifests, or dist platform roots.
- Allowed platform IDs are declared in `docs/distribution/PLATFORM_ID_CANON.md`.

### INV-DIST-SYS-DERIVED

- Fails when packaging input is sourced from `dist/sys`.
- Enforces `dist/pkg` as shipping source and `dist/sys` as realized output only.

### INV-MODE-BACKEND-SELECTION

- Fails on hardcoded backend literals in runtime sources.
- Backend availability and fallback order must come from `data/registries/mode_backend.json`.

### INV-PORTABLE-RUN-CONTRACT

- Fails when setup/launcher CLI surfaces do not expose explicit portable/install contract arguments.
- Contract reference: `docs/dev/PORTABLE_TESTING.md`.

### INV-BUILD-PRESET-CONTRACT

- Fails when required configure/build presets are missing from `CMakePresets.json`.
- Fails when required build presets do not point at mandated lane targets (`all_runtime`, `verify_fast`, `verify_full`, `dist_all`).
- Fails when VSCode default tasks drift from the canonical Windows dev/verify lane mapping.

### INV-DIST-RELEASE-LANE-GATE

- Fails when `dist_*` targets are not guarded by `dom_dist_release_lane_guard`.
- Fails when the release-lane guard does not enforce explicit release build kinds and non-`none` GBN.
- Fails when `testx_all` hard-depends on packaging targets, which would force release packaging from dev lane execution.

### INV-CLIENT-CANONICAL-BRIDGE

- Fails when canonical client command bridge sources are missing.
- Fails when `client/app/main_client.c` does not call `client_command_bridge_prepare`.
- Fails when required `client.*` command families are absent from `client/core/client_commands_registry.c`.
- Fails when bridge refusal semantics are missing capability/unavailable refusal markers.

### INV-PREALPHA-PACK-ISOLATION

- Fails if pre-alpha packs are missing explicit disposable markers.
- Fails if runtime code paths reference pre-alpha pack IDs directly.
- Keeps disposable content churn isolated to data/pack surfaces.
