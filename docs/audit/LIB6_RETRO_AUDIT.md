Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# LIB6_RETRO_AUDIT

## Scope

Retro audit for LIB-6 export/import and clone tooling before the authoritative bundle contract is introduced.

Relevant invariants reviewed:

- `docs/canon/constitution_v1.md` A1
- `docs/canon/constitution_v1.md` A9
- `docs/canon/constitution_v1.md` A10
- `INV-ARTIFACTS-CONTENT-ADDRESSED`
- `INV-INSTANCE-USES-PACK-LOCK`
- `INV-SAVE-PINS-CONTRACTS`
- `INV-PROVIDES-RESOLUTION-DETERMINISTIC`

## Existing Clone Behavior

Current local instance clone exists in [tools/ops/ops_cli.py](/d:/Projects/Dominium/dominium/tools/ops/ops_cli.py).

- `instances clone` copies an instance root locally and rewrites `instance_id`.
- Clone already preserves `pack_lock_hash`, `profile_bundle_hash`, and save references.
- Fork-only behavior exists and can copy only portable embeddings.
- The implementation is operationally useful, but it is not isolated behind a reusable `src/lib/instance/instance_clone.*` library surface yet.
- Clone behavior is filesystem-driven rather than explicitly modeled as a first-class LIB-6 primitive.

## Existing Export / Import Behavior

Current bundle export/import lives in [tools/share/share_cli.py](/d:/Projects\Dominium\dominium\tools\share\share_cli.py).

- There is a generic `export` / `inspect` / `import` CLI.
- There is a specialized instance export/import path already present.
- Current bundle container file is `bundle.container.json`.
- Current bundles are directory-based, not archive-based.
- Current content verification checks per-file SHA-256 entries from `contents_index`.
- Current instance import can switch between `portable` and `linked` modes and can insert embedded artifacts into the store.

Gaps relative to LIB-6:

- No authoritative `bundle.manifest.json`.
- No canonical `bundle_hash` over ordered item hashes.
- No dedicated bundle item schema.
- No dedicated save import/export engine.
- No dedicated pack import/export engine.
- No standalone verification tool for deterministic bundle hashes.
- Current container format is functional but ad hoc.

## Existing Save Export / Import Behavior

Current save handling is only partial.

- `share_cli export --bundle-type save` can copy a save payload file plus lockfile and compat metadata into a bundle directory.
- `share_cli import` can inspect and copy generic save bundles, but it does not materialize a first-class LIB-3 save import path.
- Save import does not currently route through a dedicated `src/lib/import/import_engine.*`.
- Save export does not currently vendor packs through an authoritative LIB-6 contract; it only copies explicit bundle inputs.

## Existing Pack / Modpack Export / Import Behavior

Current pack/modpack handling is also partial.

- `share_cli export --bundle-type modpack` supports generic bundle creation with optional embedded pack directories.
- Generic import can copy such a directory bundle back out.
- There is no dedicated pack export/import command in `setup`.
- There is no authoritative pack bundle schema or pack import engine that inserts packs into the CAS using the LIB-0 store contract.

## Current Store Layout

Current CAS/store layout is already defined by LIB-0 in [docs/architecture/CONTENT_AND_STORAGE_MODEL.md](/d:/Projects/Dominium/dominium/docs/architecture/CONTENT_AND_STORAGE_MODEL.md) and implemented in [tools/lib/content_store.py](/d:/Projects/Dominium/dominium/tools/lib/content_store.py).

- Reusable artifacts live under `store/<category>/<hash>/`.
- Portable instances vendor reusable artifacts under `embedded_artifacts/<category>/<hash>/`.
- Instances and saves already pin authoritative artifact identity by content hash instead of path.
- Current store helpers already support JSON artifacts, tree artifacts, verification, and linked/portable materialization.

## PACK-COMPAT Availability

PACK-COMPAT-1 is already present.

Primary implementation:

- [src/packs/compat/pack_verification_pipeline.py](/d:/Projects/Dominium/dominium/src/packs/compat/pack_verification_pipeline.py)
- [src/packs/compat/pack_compat_validator.py](/d:/Projects/Dominium/dominium/src/packs/compat/pack_compat_validator.py)

Current capabilities:

- verifies pack compat manifests
- builds verified lock payloads
- pins required provides ids and provider selections
- surfaces explicit refusal codes for missing or ambiguous providers
- emits provider-implied capability requirements for CAP-NEG

This means LIB-6 import does not need to invent pack validation. It needs to route imported bundle content through the existing PACK-COMPAT pipeline and preserve its refusal/degrade semantics.

## Current Setup / Launcher Integration

Current `setup` exposure in [tools/setup/setup_cli.py](/d:/Projects/Dominium/dominium/tools/setup/setup_cli.py):

- `setup instance create`
- `setup instance clone`
- `setup instance edit`
- `setup instance export`
- `setup instance import`

Current gaps:

- no `setup save export`
- no `setup save import`
- no `setup pack export`
- no `setup pack import`
- no top-level `setup export/import/clone` doctrine

Current launcher in [tools/launcher/launcher_cli.py](/d:/Projects/Dominium/dominium/tools/launcher/launcher_cli.py) already performs install, instance, save, profile, pack, and provides preflight validation. It does not yet expose a dedicated imported-bundle compatibility preview surface or bundle verification command.

## LIB-6 Starting Point Summary

Reusable foundations already exist:

- CAS storage and verification from LIB-0
- install / instance / save validation from LIB-1 through LIB-3
- shareable artifact manifest validation from LIB-4
- deterministic provider resolution from LIB-5
- partial instance bundle export/import in `share_cli`
- partial local clone in `ops_cli`

Required LIB-6 work remains:

- replace the ad hoc container format with authoritative bundle contracts
- compute and validate deterministic bundle hashes
- add save and pack engines
- centralize export/import/clone logic into library modules
- expose setup/launcher-facing verification and preview flows
- add RepoX/AuditX/TestX enforcement for deterministic bundles
