Status: RETRO_AUDIT
Last Reviewed: 2026-03-11

# LIB7_RETRO_AUDIT

## Scope

Audit target:

- install manifests and registries
- instance manifests and clone/export/import flows
- save manifests and open-policy enforcement
- pack compatibility and provider resolution
- deterministic bundle verification and replay surfaces

Relevant invariants and canon:

- `docs/canon/constitution_v1.md` A1, A6, A9, A10
- `INV-BUNDLES-DETERMINISTIC`
- `INV-NO-PATH-BASED-SEMANTICS`
- `INV-IMPORT-VALIDATES-HASHES`
- `INV-PROVIDES-RESOLUTION-DETERMINISTIC`

## Findings

1. Deterministic bundle ordering is present, but there is no single library-envelope stress toolchain.
   - LIB-6 established deterministic bundle hashing and validation in `src/lib/bundle/bundle_manifest.py`, `src/lib/export/export_engine.py`, and `src/lib/import/import_engine.py`.
   - What is missing is a canonical LIB-wide scenario generator/harness that proves repeated install/instance/save/provider/export-import behavior together.

2. Import paths run PACK-COMPAT previews, but launcher preflight/start does not rerun the full PACK-COMPAT verifier.
   - `src/lib/import/import_engine.py` calls `verify_pack_set(...)` before materializing imported content.
   - `tools/launcher/launcher_cli.py` validates pinned lock/profile/provider data and required pack presence, but it currently does not invoke `verify_pack_set(...)` during preflight/start.
   - This is a verification-surface gap, not a bundle-hash gap.

3. Save contract-pin enforcement is present and explicit.
   - `src/lib/save/save_validator.py` refuses contract mismatches unless explicit read-only fallback is allowed.
   - `tools/launcher/launcher_cli.py` already records `degrade_logged` and `degrade_reasons` for read-only fallback.
   - No silent save migration was found.

4. path-based semantics are mostly contained, but path search order still exists in lookup helpers.
   - `resolve_save_manifest_path(...)`, `resolve_instance_manifest_path(...)`, and launcher/install lookup helpers search deterministic candidate roots.
   - Hashes and fingerprints do not depend on those absolute paths, but the lookup order remains an environment-sensitive operational surface that should be covered by stress tests.
   - LIB-7 should normalize/separate path spelling from content identity and exercise both forward and backward slash-mode variants.

5. Provider resolution is deterministic, but there is no committed regression lock for provider outcomes inside the full LIB envelope.
   - `src/lib/provides/provider_resolution.py` records `selection_mode`, `selection_logged`, and deterministic fingerprints.
   - LIB-5 and launcher tests cover ambiguity refusal and deterministic lowest-pack-id selection.
   - Missing piece: one committed baseline that pins those outcomes alongside bundle hashes and save open behavior.

6. Portable/shareable flows are implemented, but proof surfaces are fragmented.
   - `tools/lib/tool_verify_bundle.py` verifies bundle roots.
   - `tools/compat/tool_replay_negotiation.py` replays CAP-NEG decisions.
   - There is no equivalent deterministic replay surface yet for LIB save-open policy decisions, and no envelope report tying provider resolution, pack verification, save open, and bundle verification together.

## Confirmed Good Surfaces

- CAS content hashing and immutable storage roots are deterministic.
- Bundle item ordering and hash verification are deterministic.
- Provider ambiguity refusal and deterministic fallback policies are explicit.
- Save contract mismatch handling remains explicit and auditable.
- Portable imports validate content before writing destination roots.

## Fix List

1. Add a shared deterministic LIB stress scenario builder used by tools and tests.
2. Add `tool_generate_lib_stress` to materialize canonical installs, instances, saves, packs, and provider-conflict scenarios from a fixed seed.
3. Add `tool_run_lib_stress` to exercise:
   - pack verification
   - provider resolution policies
   - instance/save export-import
   - save-open compatibility outcomes
   - bundle verification replay
4. Add a save-open replay tool so read-only fallback and refusal outcomes can be recomputed from pinned inputs.
5. Add a committed regression lock at `data/regression/lib_full_baseline.json` gated by `LIB-REGRESSION-UPDATE`.
6. Extend RepoX/AuditX with LIB-envelope invariants:
   - deterministic LIB envelope
   - no path semantics in canonical outputs
   - export/import verified
   - provider resolution recorded
7. Add LIB-specific TestX coverage for deterministic scenario generation, roundtrip hashes, provider policies, strict ambiguity refusal, read-only fallback logging, and cross-platform hash stability.

## Audit Conclusion

LIB-0 through LIB-6 established the core portable/content-addressed lifecycle, but the repository does not yet have one committed stress/proof/regression envelope for the whole install-instance-save-pack-provider stack. LIB-7 should add that envelope without changing prior schema meaning or weakening existing refusals.
