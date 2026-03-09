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
- `INV-GIT-HOSTED-BLOB-SIZE`
- `INV-TOPOLOGY-MAP-SIZE-BUDGET`
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
- `INV-AUTHORITY_CONTEXT_REQUIRED_FOR_INTENTS`
- `INV-SESSION_SPEC_REQUIRED_FOR_RUN`
- `INV-MVP-PACKS-MINIMAL`
- `INV-PACK-LOCK-REQUIRED`
- `INV-PROFILE-BUNDLE-REQUIRED`
- `INV-SOL-PACK-MINIMAL-SIZE`
- `INV-SOL-PACK-NO-TERRAIN-DATA`
- `INV-NO-IDENTITY-OVERRIDE`
- `INV-NO-CATALOG-REQUIRED`
- `INV-MW-CELL-ON-DEMAND-ONLY`
- `INV-NAMED-RNG-WORLDGEN-ONLY`
- `INV-SYSTEM-INSTANTIATION-VIA-WORLDGEN`
- `INV-NO-EAGER-SYSTEM-GENERATION`
- `INV-L2-OBJECTS-ID-STABLE`
- `INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN`
- `INV-SURFACE-GEN-ROUTED`
- `INV-TILES-ON-DEMAND-ONLY`
- `INV-NO-REAL-DATA-IN-EARTH-STUB`
- `INV-EARTH-GEN-DETERMINISTIC`
- `INV-NO-HARDCODED-MODE-BRANCH`
- `INV-AUTHORITY-CONTEXT-REQUIRED`
- `INV-SURVIVAL-NO-NONDIEGETIC-LENSES`
- `INV-SURVIVAL-DIEGETIC-CONTRACT`
- `INV-MODE-AS-PROFILES`
- `INV-UI-ENTITLEMENT-GATING`
- `INV-NO-TRACKED-WRITES-DURING-GATE`
- `INV-RUNTIME-NO-XSTACK-IMPORTS`
- `INV-AUDITX-PROMOTION-POLICY-PRESENT`
- `INV-REPO-HEALTH-SNAPSHOT-FINALIZATION`
- `INV-PRESENTATION-MATRIX-INTEGRITY`
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
- `INV-REALISM-DETAIL-MUST-BE-MODEL`
- `INV-CROSS-DOMAIN-MUTATION-MUST-BE-MODEL`
- `INV-PHYS-PROFILE-DECLARED`
- `INV-UNREGISTERED-QUANTITY-FORBIDDEN`
- `INV-LOSS-MAPPED-TO-HEAT`
- `INV-ACTION-MUST-HAVE-FAMILY`
- `INV-INFO-ARTIFACT-MUST-HAVE-FAMILY`
- `INV-TIER-CONTRACT-REQUIRED`
- `INV-COST-MODEL-REQUIRED`
- `INV-COUPLING-CONTRACT-REQUIRED`
- `INV-EXPLAIN-CONTRACT-REQUIRED`
- `INV-NO-UNDECLARED-COUPLING`
- `INV-LOSS-MUST-DECLARE-TARGET`
- `INV-ENERGY-TRANSFORM-REGISTERED`
- `INV-NO-DIRECT-ENERGY-MUTATION`
- `INV-ENTROPY-UPDATE-THROUGH-ENGINE`
- `INV-NO-SILENT-EFFICIENCY-DROP`
- `INV-NO-ADHOC-SAFETY-LOGIC`
- `INV-FLUID-USES-BUNDLE`
- `INV-FLUID-SAFETY-THROUGH-PATTERNS`
- `INV-NO-ADHOC-PRESSURE-LOGIC`
- `INV-FLUID-FAILURE-THROUGH-SAFETY-OR-PROCESS`
- `INV-NO-DIRECT-MASS-MUTATION`
- `INV-FLUID-BUDGETED`
- `INV-FLUID-DEGRADE-LOGGED`
- `INV-ALL-FAILURES-LOGGED`
- `INV-CHEM-BUDGETED`
- `INV-CHEM-DEGRADE-LOGGED`
- `INV-ALL-REACTIONS-LEDGERED`

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

### INV-GIT-HOSTED-BLOB-SIZE

- Fails when a tracked file exceeds the standard Git-hosted hard blob limit (`100 MiB`).
- Keeps the current tracked tree below hosted-remote hard blob rejection limits.

### INV-GIT-HOSTED-HISTORY-BLOB-SIZE

- Fails when outgoing history (`@{upstream}..HEAD`, `origin/main..HEAD`, or `HEAD` when no upstream exists) contains a blob above the standard Git-hosted hard blob limit (`100 MiB`).
- Prevents later-deleted oversized artifacts from remaining latent push blockers in local history.

### INV-TOPOLOGY-MAP-SIZE-BUDGET

- Fails when `docs/audit/TOPOLOGY_MAP.json` exceeds the repository topology budget (`99 MiB` canonical JSON including trailing newline).
- Preserves headroom below hosted-remote hard limits so topology regeneration remains push-safe.

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

### INV-AUTHORITY_CONTEXT_REQUIRED_FOR_INTENTS

- Fails when authority-context schema is missing required enforcement fields.
- Fails when client intent/session command bridge does not carry authority-context markers.
- Fails when server-side authority checks are not context-aware for authoritative sessions.

### INV-SESSION_SPEC_REQUIRED_FOR_RUN

- Fails when session launch schema omits required deterministic/session-binding fields.
- Fails when client launch flow lacks session-spec creation markers.
- Fails when session default template registry is missing required reconstruction keys.

### INV-MVP-PACKS-MINIMAL

- Fails when `locks/pack_lock.mvp_default.json` does not resolve to exactly the three MVP install-visible pack IDs.
- Fails when `dist/packs/**/pack.alias.json` contains extra alias packs outside the canonical MVP default set.
- Prevents v0.0.0 bundle drift from accreting non-minimal install-visible content.

### INV-PACK-LOCK-REQUIRED

- Fails when the canonical MVP pack lock artifact is missing or omits `pack_lock_hash`.
- Fails when `data/session_templates/session.mvp_default.json` does not record the canonical `pack_lock_hash`.
- Fails when the MVP runtime entry surface omits the explicit `--pack_lock` CLI contract.

### INV-PROFILE-BUNDLE-REQUIRED

- Fails when the canonical MVP profile bundle artifact is missing or malformed.
- Fails when shipped dist artifacts omit `dist/profiles/bundle.mvp_default.json`.
- Fails when the MVP runtime entry surface omits the explicit `--profile_bundle` CLI contract.

### INV-NO-CATALOG-REQUIRED

- Fails when runtime Milky Way generation surfaces reference Milky Way catalog or real-data files directly.
- Fails when the analytic Milky Way priors registry required for MW-0 base generation is missing.
- Preserves overlay-safe procedural base generation with no catalog dependency.

### INV-MW-CELL-ON-DEMAND-ONLY

- Fails when the MW generator surface loses the explicit cell-addressed generation markers.
- Fails when eager whole-galaxy generation tokens appear in the Milky Way runtime generator path.
- Preserves MW-0 as an on-demand GEO-cell refinement layer, not a bulk-instantiated galaxy pass.

### INV-NAMED-RNG-WORLDGEN-ONLY

- Fails when the Milky Way worldgen surfaces omit the named galaxy/system RNG markers.
- Fails when nondeterministic RNG or wall-clock style tokens appear in the governed Milky Way runtime files.
- Preserves replay-stable MW cell generation and cross-platform hash expectations.

### INV-SYSTEM-INSTANTIATION-VIA-WORLDGEN

- Fails when MW-1 star-system artifact instantiation markers are missing from the canonical worldgen surfaces.
- Fails when teleport/query/runtime proof surfaces drift away from the `process.worldgen_request` -> `process.camera_teleport` contract.
- Preserves process-only authoritative star-system creation and replay-safe artifact attachment.

### INV-NO-EAGER-SYSTEM-GENERATION

- Fails when MW-1 system discovery/query surfaces lose their explicit cell-bounded enumeration markers.
- Fails when eager whole-galaxy or all-system generation tokens appear in governed MW-1 files.
- Preserves on-demand system discovery and bounded nearest-query behavior.

### INV-L2-OBJECTS-ID-STABLE

- Fails when MW-2 L2 star, planet, or moon object-id derivation markers drift from the canonical GEO-1 local-subkey contract.
- Fails when runtime persistence or replay proof surfaces stop emitting the canonical L2 star/orbit/basic/summary artifact rows.
- Preserves overlay-safe stable identities for later SOL/catalog pinning and replay-safe L2 refinement.

### INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN

- Fails when MW-2 orbit generation loses the deterministic push-out and periapsis-clamp markers that replace retry sampling.
- Fails when retry-loop tokens are introduced into the governed L2 refinement surface.
- Preserves bounded deterministic orbital-spacing adjustment with no random retry behavior.

### INV-SURFACE-GEN-ROUTED

- Fails when MW-3 surface generation loses the explicit routing and delegation markers from the governed runtime surface.
- Fails when Earth-specific generator selection drifts into runtime code instead of remaining registry-driven.
- Preserves overlay-safe Earth delegation and pack-driven surface specialization.

### INV-TILES-ON-DEMAND-ONLY

- Fails when MW-3 surface refinement loses the explicit tile-scoped generation markers in the canonical runtime path.
- Fails when eager planet-surface expansion tokens appear in the governed MW-3 files.
- Preserves L3 as a single-tile on-demand refinement path with bounded field and geometry initialization.

### INV-NO-REAL-DATA-IN-EARTH-STUB

- Fails when the governed EARTH-0 generator surface loses the explicit low-data Earth parameter markers.
- Fails when DEM, heightmap, shapefile, city, border, or other real-data import tokens appear in the governed EARTH-0 runtime path.
- Preserves EARTH-0 as a procedural, replaceable, data-light Earth baseline instead of a hidden real-data bundle.

### INV-EARTH-GEN-DETERMINISTIC

- Fails when the governed EARTH-0 generator surfaces lose the explicit named-seed, interpolated-noise, and routed-handler markers.
- Fails when nondeterministic RNG or wall-clock style tokens appear in the EARTH-0 runtime or verification path.
- Preserves replay-stable Earth macro generation and cross-platform hash expectations.

### INV-SOL-PACK-MINIMAL-SIZE

- Fails when the canonical Sol pin pack artifacts are missing from the official pack surface.
- Fails when the Sol pin patch count or governed artifact byte size exceeds the bounded SOL-0 heuristic envelope.
- Preserves SOL-0 as a tiny official overlay, not a hidden dataset bundle.

### INV-SOL-PACK-NO-TERRAIN-DATA

- Fails when the Sol pin pack drifts beyond the allowed coarse property classes.
- Fails when terrain, DEM, city, border, or authored-surface tokens appear in the governed Sol patch payload.
- Preserves SOL-0 as a hierarchy-and-constants pin only, leaving Earth/Sol surface detail to later overlays.

### INV-NO-IDENTITY-OVERRIDE

- Fails when the Sol pin documentation or overlay engine loses the immutable-identity guard markers.
- Fails when the Sol patch payload targets immutable identity paths or uses delete-style property operations.
- Preserves GEO-owned object identity while allowing only lawful property refinement through GEO-9 overlays.

### INV-NO-HARDCODED-MODE-BRANCH

- Fails when runtime/governance sources introduce hardcoded mode-flag tokens.
- Enforces profile-driven mode composition and prevents semantic forks.

### INV-AUTHORITY-CONTEXT-REQUIRED

- Fails when `schema/session/session_spec.schema` or `schema/authority/authority_context.schema` are missing.
- Fails when required authority/session wiring fields are absent.

### INV-SURVIVAL-NO-NONDIEGETIC-LENSES

- Fails when survival law profiles do not explicitly permit diegetic lenses.
- Fails when survival law profiles do not explicitly forbid `lens.nondiegetic.*`.
- Enforces diegetic survival contract as data, not UI runtime branching.

### INV-SURVIVAL-DIEGETIC-CONTRACT

- Fails when survival law profiles grant nondiegetic console/freecam entitlements.
- Fails when survival bridge bindings allow HUD-only survival profiles to surface nondiegetic tools.
- Locks survival to diegetic lens surfaces with deterministic entitlement refusal.

### INV-MODE-AS-PROFILES

- Fails when `ExperienceProfile` entries do not bind to valid `LawProfile` IDs.
- Fails when experiences reference unknown default parameter bundles.
- Ensures mode intent resolves through registries, not ad-hoc runtime flags.

### INV-UI-ENTITLEMENT-GATING

- Fails when entitlement-sensitive UI commands are missing metadata in command registry.
- Fails when bridge-level refusal markers for profile/entitlement checks are missing.
- Locks HUD/overlay/console/freecam surfaces to profile-derived entitlements.

### INV-PRESENTATION-MATRIX-INTEGRITY

- Fails when `data/registries/presentation_matrix.json` is missing or schema-mismatched.
- Fails when matrix rows reference unknown law profiles or lens IDs/prefixes.
- Fails when survival rows expose nondiegetic lenses/panels.
- Fails when console/debug overlay panels are exposed without required entitlements.
- Requires observer law rows to declare watermark enforcement.

### INV-AUDITX-PROMOTION-POLICY-PRESENT

- Fails when `docs/governance/AUDITX_PROMOTION_POLICY.md` is missing.
- Fails when the policy omits promotion thresholds, flow, sign-off requirements, or retirement contract.
- Prevents silent promotion of AuditX findings into blocking RepoX rules.

### INV-REPO-HEALTH-SNAPSHOT-FINALIZATION

- Applies only when `docs/audit/system/GOVERNANCE_FINAL_REPORT.md` is part of the change.
- Requires `docs/audit/system/REPO_HEALTH_SNAPSHOT.json` and `docs/audit/system/REPO_HEALTH_SNAPSHOT.md` in the same change.
- Requires snapshot json to declare `artifact_class=CANONICAL` and `git_status_clean=true`.

### INV-DEFAULTS-OPTIONAL

- Fails when `bundle.core.runtime` is missing or marked optional.
- Fails when non-core default bundles are not explicitly optional.
- Preserves core boot viability when optional content bundles are removed.

### INV-NO-TRACKED-WRITES-DURING-GATE

- Fails when `gate.py verify|strict|full|doctor` tracked-write enforcement is missing.
- Fails when `.xstack_cache/gate/TOUCHED_FILES_MANIFEST.json` is malformed.
- Fails when non-snapshot gate runs report tracked file mutations.
- Allows tracked audit writes only through `gate.py snapshot`.

### INV-RUNTIME-NO-XSTACK-IMPORTS

- Fails when runtime source trees (`engine/`, `game/`, `client/`, `server/`) reference `tools/xstack`.
- Fails when runtime CMake roots reference `tools/xstack`.
- Keeps XStack removable without affecting runtime build or runtime execution paths.

### INV-REALISM-DETAIL-MUST-BE-MODEL

- STRICT/FULL fail when inline realism response-curve logic is present outside constitutive model pathways.
- Transitional exceptions require explicit `data/registries/deprecation_registry.json` mapping entries with source path + line.
- Prevents bespoke domain response logic drift.

### INV-CROSS-DOMAIN-MUTATION-MUST-BE-MODEL

- STRICT/FULL fail on direct cross-domain state writes (for example ELEC writing THERM keys, THERM writing MECH keys).
- Requires coupling through constitutive model outputs and process/effect/hazard pathways.

### INV-PHYS-PROFILE-DECLARED

- STRICT/FULL fail when SessionSpec omits top-level `physics_profile_id`.
- STRICT/FULL fail when session creation fixtures/examples omit declared physics profile identity.
- Keeps physics profile selection explicit at session composition boundary.

### INV-UNREGISTERED-QUANTITY-FORBIDDEN

- STRICT/FULL fail when runtime/sessionx/registry surfaces reference `quantity.*` identifiers not present in `data/registries/quantity_registry.json`.
- Prevents silent ad hoc quantity channels and enforces MAT-1/PHYS registration discipline.

### INV-LOSS-MAPPED-TO-HEAT

- STRICT/FULL fail when modeled loss pathways are not mapped to canonical heat targets (`quantity.heat_loss` or explicit temperature effects).
- Profile policy can require hard mapping or explicit logged exception pathway.

### INV-ACTION-MUST-HAVE-FAMILY

- STRICT/FULL fail when exposed actions/processes/tasks are missing template or family mappings.
- Keeps META-ACTION coverage complete and deterministic.

### INV-INFO-ARTIFACT-MUST-HAVE-FAMILY

- STRICT/FULL fail when action-template produced artifacts are not mapped to canonical META-INFO families.
- Mapping source: `data/registries/info_artifact_family_registry.json`.

### INV-TIER-CONTRACT-REQUIRED

- STRICT/FULL fail when mandatory tier contracts are missing for baseline governed domains.
- Registry source: `data/registries/tier_contract_registry.json`.
- Enforces explicit tier support, deterministic downgrade order, and shard-safety declarations.

### INV-COST-MODEL-REQUIRED

- STRICT/FULL fail when tier contracts omit `cost_model_id`.
- Registry source: `data/registries/tier_contract_registry.json`.
- Enforces deterministic budget arbitration binding for each governed subsystem/process family.

### INV-COUPLING-CONTRACT-REQUIRED

- STRICT/FULL fail when required baseline cross-domain coupling declarations are missing.
- Registry source: `data/registries/coupling_contract_registry.json`.
- Couplings must declare class, from/to domains, and mechanism type/ID.

### INV-EXPLAIN-CONTRACT-REQUIRED

- STRICT/FULL fail when hazard/failure explainability declarations are missing.
- Registry source: `data/registries/explain_contract_registry.json`.
- Explain contracts must declare event-kind mapping, artifact type, and required causal inputs.

### INV-NO-UNDECLARED-COUPLING

- STRICT/FULL fail when baseline coupling mechanisms are used without declared coupling contracts.
- STRICT/FULL fail when direct cross-domain coupling writes are detected outside model/process pathways.
- Prevents hidden coupling drift and keeps topology + proof impacts auditable.

### INV-LOSS-MUST-DECLARE-TARGET

- STRICT/FULL fail when loss pathways are not explicitly mapped to heat-loss quantity or temperature-effect targets.
- Prevents silent energy disappearance in cross-domain loss accounting.

### INV-ENERGY-TRANSFORM-REGISTERED

- STRICT/FULL fail when authoritative energy conversions do not reference `data/registries/energy_transformation_registry.json`.
- Requires PHYS-3 runtime pathways to route conversion writes through deterministic ledger transformation helpers.
- Missing required baseline transforms (`kinetic_to_thermal`, `electrical_to_thermal`, `chemical_to_thermal`, `potential_to_kinetic`, `external_irradiance`) is blocking.

### INV-NO-DIRECT-ENERGY-MUTATION

- STRICT/FULL fail when domain/runtime sources directly mutate `quantity.energy_*` channels outside energy-ledger helpers.
- Enforces process-only mutation for canonical energy totals and prevents silent energy creation/destruction.
- Allowed mutation surfaces are limited to PHYS-3 ledger engine/runtime orchestration codepaths.

### INV-ENTROPY-UPDATE-THROUGH-ENGINE

- STRICT/FULL fail when entropy state/event mutation bypasses PHYS-4 entropy runtime helper pathways.
- Requires entropy updates to route through deterministic engine functions (`record_entropy_contribution`, `apply_entropy_reset`) and associated artifact/hash-chain updates.
- Prevents ad hoc direct writes to `entropy_state_rows` and entropy event streams.

### INV-NO-SILENT-EFFICIENCY-DROP

- STRICT/FULL fail when machine/efficiency degradation is introduced without entropy-policy or model-mediated linkage.
- Maintenance degradation pathways must derive from entropy effect evaluation or explicit model outputs, not inline hidden multipliers.
- Enforces auditable degradation provenance for PHYS-4 irreversibility hooks.

### INV-NO-ADHOC-SAFETY-LOGIC

- STRICT/FULL fail when protection logic bypasses SafetyPattern evaluation.
- Covers breaker/overtemp/LOTO patterns and requires process-mediated safety execution.

### INV-FLUID-USES-BUNDLE

- STRICT/FULL fail when `bundle.fluid_basic` is missing or does not bind `quantity.mass_flow` and `quantity.pressure_head`.
- STRICT/FULL fail when canonical FLUID quantity IDs are absent from quantity registries.
- Keeps FLUID substrate declarations aligned to QuantityBundle governance.

### INV-FLUID-SAFETY-THROUGH-PATTERNS

- STRICT/FULL fail when required FLUID safety patterns are missing from SafetyPattern registry.
- Required baseline patterns include relief, burst-disk, fail-safe stop, and LOTO coverage.
- Prevents FLUID protection behavior from drifting into ad-hoc domain-local branching.

### INV-NO-ADHOC-PRESSURE-LOGIC

- STRICT/FULL fail when pressure/head/valve write logic appears outside allowed model/process pathways.
- Interior compartment pressure bookkeeping remains INT-owned and allowed in canonical interior flow engine files.
- Enforces FLUID pressure behavior through constitutive models, FlowSystem, and process-mediated mutation only.

### INV-FLUID-FAILURE-THROUGH-SAFETY-OR-PROCESS

- STRICT/FULL fail when FLUID containment-failure pathways bypass safety patterns or deterministic process helpers.
- Burst/leak/relief handling must route through `process.burst_event`, `process.start_leak`, `process.leak_tick`, and SAFETY pattern events.
- Prevents hidden catastrophic branching and preserves auditable failure provenance.

### INV-NO-DIRECT-MASS-MUTATION

- STRICT/FULL fail when FLUID/INT mass-state writes appear outside approved process/runtime mutation boundaries.
- Direct writes to tank/interior mass channels are forbidden unless performed by canonical engines/process runtime.
- Enforces process-only mutation for containment failures and leak coupling.

### INV-FLUID-BUDGETED

- STRICT/FULL fail when FLUID stress/solve surfaces do not expose deterministic budget controls.
- Requires explicit bounded inputs for edge processing, model cost, failure limits, and per-tick envelope pressure behavior.
- Prevents unbounded FLUID network solves under large-network load.

### INV-FLUID-DEGRADE-LOGGED

- STRICT/FULL fail when FLUID degradation pathways are missing deterministic reason codes or emitted decision-log rows.
- Required degradation chain is tick-bucket -> subgraph F0 -> deferred non-critical model bindings -> leak evaluation cap.
- Ensures budget pressure behavior is auditable and replay-stable.

### INV-ALL-FAILURES-LOGGED

- STRICT/FULL fail when FLUID containment failures are not represented through explicit relief/leak/burst artifacts and safety pattern events.
- Requires proof/replay hash-chain surfaces for `fluid_flow`, `relief`, `leak`, and `burst`.
- Requires a committed FLUID regression lock (`data/regression/fluid_full_baseline.json`) gated by `FLUID-REGRESSION-UPDATE`.

### INV-CHEM-BUDGETED

- STRICT/FULL fail when CHEM stress/solve surfaces do not expose deterministic per-tick budget controls.
- Requires explicit caps for reaction evaluations, total cost, model cost, and emission-event production.
- Prevents unbounded CHEM reaction graph evaluation under large-factory MMO-scale load.

### INV-CHEM-DEGRADE-LOGGED

- STRICT/FULL fail when CHEM degradation pathways omit deterministic degrade reason codes or decision-log artifacts.
- Required degradation chain is tick-bucket -> reaction downgrade to C0 -> deferred non-critical yield detail -> evaluation cap.
- Ensures budget-pressure behavior is auditable, replay-stable, and deterministic.

### INV-ALL-REACTIONS-LEDGERED

- STRICT/FULL fail when CHEM reaction mutations are not paired with explicit energy-ledger artifacts and proof hash-chain surfaces.
- Requires canonical reaction/emission/degradation proof chains and replay-window verification coverage.
- Requires a committed CHEM regression lock (`data/regression/chem_full_baseline.json`) gated by `CHEM-REGRESSION-UPDATE`.

### INV-STATE-VECTOR-DECLARED-FOR-SYSTEM

- STRICT/FULL fail when SYS/COMPILE/PROC state-vector baseline artifacts are missing.
- Requires declared state-vector definitions and snapshots plus deterministic hash-chain surfaces.
- Requires collapse/expand/compile pathways to serialize and deserialize owner state vectors through STATEVEC engine helpers.

### INV-NO-UNDECLARED-STATE-MUTATION

- STRICT/FULL fail when output-affecting state is mutated outside declared state-vector pathways.
- Requires debug guard coverage (`detect_undeclared_output_state`) and violation logging before collapse.
- Requires state-vector row mutation to remain constrained to canonical runtime/process paths.
