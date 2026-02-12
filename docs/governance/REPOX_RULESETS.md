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
- `repox/derived_artifacts`: machine-generated contract surfaces (e.g., solver registry, AuditX derived reports).
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
- `INV-NO-DIRECT-GATE-CALLS`
- `INV-REMEDIATION-PLAYBOOKS`
- `INV-FAILURE-CLASS-COVERAGE`
- `INV-IDENTITY-FINGERPRINT`
- `INV-IDENTITY-CHANGE-EXPLANATION`
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
- `INV-SECUREX-TRUST-POLICY-VALID`
- `INV-SECUREX-PRIVILEGE-MODEL`
- `INV-UNLOCKED-DEPENDENCY`
- `INV-TOOL-VERSION-MISMATCH`
- `INV-SOLVER-CONTRACTS`
- `INV-DERIVED-ARTIFACT-CONTRACT`
- `INV-AUDITX-ARTIFACT-HEADERS`
- `INV-AUDITX-DETERMINISM`
- `INV-AUDITX-NONRUNTIME`
- `INV-AUDITX-OUTPUT-STALE`
- `INV-GLOSSARY-TERM-CANON`
- `WARN-GLOSSARY-TERM-CANON`
- `INV-UNIVERSE_IDENTITY_IMMUTABLE`
- `INV-NO-HARDCODED-MODE-BRANCH`
- `INV-AUTHORITY-CONTEXT-REQUIRED`
- `INV-MODE-AS-PROFILES`
- `INV-UI-ENTITLEMENT-GATING`
- `INV-DEFAULTS-OPTIONAL`
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

### INV-NO-DIRECT-GATE-CALLS

- Fails when automation scripts invoke raw gate commands directly.
- Raw `check_repox_rules.py`, `tool_ui_bind`, and `ctest` calls must be routed through sanctioned wrappers.
- Canonical wrappers are `scripts/dev/gate.py`, `scripts/dev/gate_shim.py`, `scripts/dev/run_repox.py`, and `scripts/dev/run_testx.py`.

### INV-REMEDIATION-PLAYBOOKS

- Fails when remediation playbook schema/registry are missing or invalid.
- Fails when required blocker playbooks are missing.
- Enforces deterministic strategy class declarations for autonomous gate remediation.

### INV-FAILURE-CLASS-COVERAGE

- Fails when failure-class schema or registry is missing or malformed.
- Fails when failure classes reference unknown remediation playbooks.
- Fails when failure classes are missing regression tests or explanation docs.
- Fails when listed regression test names are not present in canonical TestX CMake registrations.

### INV-IDENTITY-FINGERPRINT

- Fails when `docs/audit/identity_fingerprint.json` is missing or stale.
- Fingerprint is derived from canon/governance-critical identity inputs.
- Canonical generator: `tools/ci/tool_identity_fingerprint.py`.

### INV-IDENTITY-CHANGE-EXPLANATION

- Fails when identity input changes are not accompanied by explanation artifact updates.
- Explanation artifact: `docs/audit/identity_fingerprint_explanation.md`.

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

### INV-AUDITX-ARTIFACT-HEADERS

- Fails when `docs/audit/auditx/` exists but required artifact files are missing.
- Fails when markdown artifacts are missing RepoX doc headers.
- Fails when canonical JSON artifacts are not marked `artifact_class=CANONICAL`.
- Fails when canonical JSON artifacts include run-meta timestamp keys.
- Fails when `RUN_META.json` is malformed or missing `artifact_class=RUN_META`.

### INV-DERIVED-ARTIFACT-CONTRACT

- Fails when the derived artifact contract schema/registry is missing or invalid.
- Fails when required canonical artifact IDs are missing from the registry.
- Fails when artifact class metadata conflicts with determinism/gating expectations.

### INV-AUDITX-DETERMINISM

- Fails when deterministic scan primitives are missing from AuditX implementation.
- Enforces stable hash/fingerprint/sort contract in graph, model, and output writers.

### INV-AUDITX-NONRUNTIME

- Fails when runtime sources reference `tools/auditx` implementation paths.
- Keeps AuditX tooling strictly out of runtime product code.

### INV-AUDITX-OUTPUT-STALE

- Warns when committed `docs/audit/auditx/FINDINGS.json` lags far behind HEAD.
- Non-gating signal to refresh derived semantic reports.

### INV-SECUREX-TRUST-POLICY-VALID

- Fails when SecureX trust-policy schema/registry are missing or malformed.
- Fails when required subsystem trust entries are absent.
- Ensures trust boundaries are declared in data, not ad-hoc code paths.

### INV-SECUREX-PRIVILEGE-MODEL

- Fails when privilege role registry is missing required roles or malformed.
- Fails when required observer entitlements are missing or elevated roles omit watermark policy.
- Enforces law-profile-driven privilege contracts.

### INV-UNLOCKED-DEPENDENCY

- Fails when dependency manifests use non-pinned version ranges in governed surfaces.
- Prevents silent supply-chain drift through floating dependency ranges.

### INV-TOOL-VERSION-MISMATCH

- Fails when `docs/audit/security/INTEGRITY_MANIFEST.json` is missing, malformed, or stale.
- Fails when recorded tool hashes do not match current tool sources.
- Prevents committing derived artifacts produced by mismatched tool implementations.

### INV-GLOSSARY-TERM-CANON

- Fails when canonical architecture/governance docs use glossary-forbidden synonyms.
- Fails when glossary schema/registry/doc artifacts are missing or malformed.
- Keeps normative terminology stable across canon surfaces.

### WARN-GLOSSARY-TERM-CANON

- Warns when non-canonical docs use glossary-forbidden synonyms.
- Non-gating during migration; intended to ratchet once drift is cleaned up.

### INV-UNIVERSE_IDENTITY_IMMUTABLE

- Fails when universe identity/state schemas are missing required split-contract fields.
- Fails when runtime sources introduce explicit universe identity mutation tokens.
- Keeps UniverseIdentity immutable after creation while UniverseState carries evolution.

### INV-NO-HARDCODED-MODE-BRANCH

- Fails when runtime/governance sources introduce hardcoded mode-flag tokens.
- Enforces profile-driven mode composition and prevents semantic forks.

### INV-AUTHORITY-CONTEXT-REQUIRED

- Fails when `schema/session/session_spec.schema` or `schema/authority/authority_context.schema` are missing.
- Fails when required authority/session wiring fields are absent.

### INV-MODE-AS-PROFILES

- Fails when `ExperienceProfile` entries do not bind to valid `LawProfile` IDs.
- Fails when experiences reference unknown default parameter bundles.
- Ensures mode intent resolves through registries, not ad-hoc runtime flags.

### INV-UI-ENTITLEMENT-GATING

- Fails when entitlement-sensitive UI commands are missing metadata in command registry.
- Fails when bridge-level refusal markers for profile/entitlement checks are missing.
- Locks HUD/overlay/console/freecam surfaces to profile-derived entitlements.

### INV-DEFAULTS-OPTIONAL

- Fails when `bundle.core.runtime` is missing or marked optional.
- Fails when non-core default bundles are not explicitly optional.
- Preserves core boot viability when optional content bundles are removed.
