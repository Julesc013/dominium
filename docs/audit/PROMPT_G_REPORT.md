Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# PROMPT G Audit Report





Status: BLOCKING FAIL


Scope: ENGINE/ + GAME/ + SCHEMA/ + DOCS/ + DATA/


Method: static audit only; no runtime tests executed.





## Summary


- Core invariants are documented but not enforced in code; multiple legacy


  systems remain active and conflict with UPS, authority gating, and process


  execution requirements.


- UPS manifest parsing and capability registry exist but are not integrated


  into engine/game startup or content resolution.


- Schema forward-compatibility is violated by strict coredata tooling that


  rejects unknown fields and tags.


- Documentation under docs/architecture and docs/specs remains unarchived and contains


  conflicting guidance.





## Confirmed guarantees


- UPS registry behavior is deterministic for identical manifest inputs


  (`engine/modules/ups/d_ups.c`).


- Canonical UPS pack manifests exist for base and library packs under


  `data/packs/*/pack.manifest` and `data/packs/*/pack_manifest.json`.





## Blocking violations (must be fixed)


- Legacy package systems are active and path-based (manifest.ini, package.toml),


  conflicting with capability-driven UPS resolution.


- Authority tokens, process execution enforcement, and snapshot systems are


  declared but not implemented or wired.


- Coredata compile/validate tooling rejects unknown fields/tags, violating


  forward-compatibility requirements.


- Documentation coherence is broken by unarchived legacy specs that contradict


  canonical architecture docs.





## Findings by audit area





### 1) Invariant enforcement audit


Status: FAIL


Evidence:


- Legacy path-based package scanning (`engine/modules/core/pkg.c`) and


  package registry (`engine/modules/mod/package_registry.c`) remain active.


- Direct content editing tools operate on fixed paths


  (`tools/game_edit/game_edit_core.c`, `tools/world_edit/world_edit_core.c`,


  `tools/save_edit/save_edit_core.c`).


- Authority tokens are declared but not implemented


  (`engine/include/domino/authority.h` with no implementation found).





### 2) Zero-asset boot verification


Status: UNVERIFIED (AT RISK)


Evidence:


- No runtime test executed for zero-pack boot.


- Engine core scans `data/versions/dev` and `mods/` by path; absence is tolerated,


  but tool defaults reference concrete paths (`tools/world_edit/world_edit_core.c`).





### 3) Authority and mutation boundary audit


Status: FAIL


Evidence:


- No implementation or usage of `dom_authority_is_valid` or token checks.


- Editing tools and APIs allow direct mutation without authority gating


  (`game/include/dominium/*_edit_api.h`, `tools/*_edit/*_core.c`).





### 4) Process model completeness check


Status: FAIL


Evidence:


- Process descriptors exist (`engine/include/domino/process.h`) but no executor,


  scheduler, or usage is present in engine/game runtime.





### 5) Field and domain consistency


Status: PARTIAL / UNVERIFIED


Evidence:


- Domain volume runtime exists (`engine/modules/world/domain_volume.cpp`), but


  field layers and topology integration are absent from runtime code.


- No enforcement found for latent/unknown state or representation tiers.





### 6) Snapshot safety and semantics


Status: FAIL


Evidence:


- Snapshot API declared (`engine/include/domino/snapshot.h`) with no implementation.





### 7) Schema forward-compatibility test


Status: FAIL


Evidence:


- Coredata tooling rejects unknown fields and tags:


  `tools/coredata_compile/coredata_load.cpp` (unknown_field errors),


  `tools/coredata_validate/coredata_validate_load.cpp` (unknown_tag errors).


- Strict mode is enforced even when disabled


  (`tools/coredata_compile/coredata_compile_main.cpp`).





### 8) Capability negotiation and degradation


Status: FAIL


Evidence:


- Compatibility negotiation exists but is unused


  (`engine/modules/compat/compat_modes.c` has no callers).


- No runtime integration of `dom_ups_registry_set_compat_decision` or


  capability negotiation with loaded packs.





### 9) Pack isolation and purity


Status: FAIL


Evidence:


- Active legacy package systems use fixed roots and manifest.ini


  (`engine/modules/core/pkg.c`, `docs/specs/SPEC_PACKAGES.md`).


- Secondary package registry uses package.toml scanning


  (`engine/modules/mod/package_registry.c`).


- UPS packs live under `data/packs/` but are not wired into engine startup.





### 10) Save and replay resilience


Status: FAIL / UNVERIFIED


Evidence:


- Save edit tool uses ad-hoc key/value files (`tools/save_edit/save_edit_core.c`).


- No save/replay schema enforcement or compatibility negotiation observed.





### 11) Mod additivity and isolation


Status: FAIL / UNVERIFIED


Evidence:


- Legacy package registry has no explicit supersession or capability checks.


- No warnings or sandboxing observed for superseding mods.





### 12) Documentation coherence check


Status: FAIL


Evidence:


- Legacy architecture/spec files remain unarchived under `docs/architecture` and


  `docs/specs`, and include path-based package guidance


  (`docs/specs/SPEC_PACKAGES.md`).


- Canonical architecture docs exist under `docs/architectureitecture/`, but the


  repository still contains conflicting specifications.





### 13) Future-pressure analysis


Status: BLOCKED


Evidence:


- Adding new galaxy types, exotic matter, network types, institution types,


  climate fields, or process classes should be data-only, but current runtime


  lacks UPS integration, process execution, and schema-preserving loaders.


- Removing a major pack cannot be verified safely because pack resolution and


  compatibility modes are not wired.





## Required fixes (blocking)


- Retire or gate legacy package systems in favor of UPS capability resolution.


- Implement and enforce authority token validation for all mutations.


- Implement process execution core and route all state changes through it.


- Implement snapshot creation/query/release with immutable semantics.


- Update coredata tooling to preserve unknown fields/tags and support forward


  compatibility.


- Archive or mark legacy docs under `docs/architecture` and `docs/specs` per PROMPT 0.





## Verification gaps


- No runtime zero-pack boot test executed.


- No end-to-end compatibility negotiation test executed.


- No save/replay load tests executed.
