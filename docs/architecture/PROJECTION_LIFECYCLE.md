Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Projection Lifecycle (REPOX)





Status: binding.


Scope: generation, invalidation, and reproducibility of IDE projections.





## Projection manifest


Each projection emits a manifest:


- Path: `/ide/manifests/<projection_id>.projection.json`


- Schema: `/ide/manifests/projection_manifest.schema.json`





Required fields include:


- `projection_id`, `product`, `ui_shell`


- `toolchain_tier`, `target_os_family`, `target_os_min`, `arch`


- `language_mode`, `sdk_pin`, `crt_policy`


- `generator`, `input_fingerprint`, `output_paths`


- `regeneration_command`, `warnings`





## Invalidation rules


A projection is invalid if any of these change:


- CMakeLists, toolchain files, or projection scripts.


- File lists, include paths, or compiler/linker flags.


- Canon version docs or schema versions.


- Projection manifest schema.





## Regeneration rules


- Projections are regenerated only through deterministic scripts.


- Regeneration must not modify AUTHORITATIVE directories.


- Differences are allowed only under `/ide/**`.


- Deleting `/ide/**` is safe and expected.





## Reproducibility expectations


- Input fingerprint must be stable for a given projection.


- Output paths must be deterministic and relative to `/ide`.


- Regeneration command must be exact and copy-pasteable.





## Cross-references


- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`


- `docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md`
