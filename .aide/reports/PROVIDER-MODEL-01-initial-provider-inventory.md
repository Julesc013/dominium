# PROVIDER-MODEL-01 Initial Provider Inventory

Inventory is descriptive only. PROVIDER-MODEL-01 defines provider law and does
not migrate current runtime systems, Workbench modules, validators, packs, or
tool adapters into provider descriptors.

## Scan Summary

- Files scanned: 17,865 tracked files.
- Classified candidates: 1,396.
- Inventory status: warning.

## Categories

- Backend candidates: 152.
- Service candidates: 96.
- Command handler candidates: 215.
- Workbench module candidates: 97.
- External adapter candidates: 195.
- Capability relationship files: 10.
- Pack hints, not provider runtime: 631.

## Examples

- Backend candidates: `runtime/audio/audio.c`, `runtime/input/input.c`, `runtime/network/d_net.c`.
- Service candidates: `runtime/package/content/d_content.c`, `runtime/package/content/d_content_validate.c`.
- Command handler candidates: `tools/validators/abi/check_public_headers.py`, `tools/validators/check_component_matrices.py`.
- Workbench module candidates: `apps/workbench/module/domain/universe/ue_commands.cpp`, `apps/workbench/module/domain/universe/ue_queries.cpp`.
- External adapter candidates: `tools/package/compatibility/tool_apply_migration.py`, `tools/package/artifactmeta/tool_artifactmeta.c`.
- Pack hints: `content/packs/**` capability and manifest files.

## Registration Decision

Registered now:

- `domino.provider.render.null`
- `domino.provider.render.software`
- `domino.provider.storage.local`
- `domino.provider.package.validator`
- `dominium.provider.workbench.validation`

Deferred:

- Platform, network, audio, input, native, external process, and Workbench module provider descriptors.
- Runtime provider resolver and dynamic loader implementation.
- Provider conformance suites beyond registry and fixture scaffolding.
- Mod/native trust integration.

## Risks

- Existing backend and service implementations remain path-shaped and are not
  migrated by this task.
- Pack capability declarations are content hints, not provider runtime truth.
- Provider selection, fallback, and degradation remain law-only until future
  implementation tasks.
