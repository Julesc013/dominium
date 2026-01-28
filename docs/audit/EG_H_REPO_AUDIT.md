# EG-H Repo Audit (Phase 0)

Status: draft.
Scope: audit of current repo surfaces relevant to EG-H; no functional changes applied.
Authority: canonical for Phase 0; later phases must close identified gaps.

## What exists (current surfaces)

### Canon docs (docs/architecture)
Present canonical files required by EG-H:
- `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- `docs/architecture/INVARIANTS.md`
- `docs/architecture/REALITY_LAYER.md`
- `docs/architecture/AUTHORITY_AND_OMNIPOTENCE.md`
- `docs/architecture/LIFE_AND_POPULATION.md`
- `docs/architecture/CIVILIZATION_MODEL.md`
- `docs/architecture/EXECUTION_MODEL.md`
- `docs/architecture/FUTURE_PROOFING.md`

### Engine public headers
- `engine/include/domino/` contains extensive public headers, including UI/render/platform facing headers (`ui*`, `gfx.h`, `platform.h`, `render/`).
- `engine/include/render/` exists in the public include surface.
- Prior C89/C++98 baseline check failures are referenced in build logs (inline functions, C99 designators).

### Game public headers
- `game/include/dominium/` exposes game interfaces and content APIs, including UI and path headers (`dom_rend.h`, `paths.h`).

### Schemas
- `schema/` contains the canonical schema set and governance docs (versions, validation, migration).

### Data
- `data/packs/` contains optional packs (base, worldgen, realities, examples).
- `data/worldgen/real/` now contains canonical real-world refinement data (Milky Way, Sol system, Earth).
- `data/registries/`, `data/standards/`, and `data/defaults/` exist.

### Docs beyond canon
- `docs/architectureitecture/` contains prior canonical-style docs from earlier prompts.
- `docs/worldgen/` contains refinement contract and worldgen philosophy.
- `docs/content/` contains UPS overview and fallback docs.
- `docs/modding/` now contains mod authoring rules.
- `docs/tools/` contains offline worldgen tooling docs.

### Tests and tooling
- `engine/tests`, `game/tests`, and `tools/tests` exist.
- CMake exposes a TESTX labeling helper in `cmake/DomIntegration.cmake` (`dom_add_testx`), but no concrete TESTX command or manifest was found.

## Missing vs canon (Phase 0 findings)

- **TESTX discovery**: No TESTX scripts, targets, or documentation found; only a label helper exists.
- **Version governance**: `version/build.txt`, `engine.version`, and `game.version` are missing in repo.
- **Version printing**: No evidence that test binaries print engine/game/build/protocol versions.
- **UPS canonical doc**: Required `docs/content/UPS.md` is not present (closest is `docs/content/UPS_OVERVIEW.md`).

## Conflicts with canon

- **Dual canon trees**: `docs/architecture/` is declared canonical by EG-H, but `docs/architectureitecture/` contains overlapping authoritative docs. These may conflict and require archival or clear cross-linking.
- **Public headers include platform/render/UI**: The engine public headers expose render/UI/platform details, conflicting with the boundary hygiene and content-agnostic invariants.
- **Header language guarantees**: Prior baseline header checks indicate non-C89/C++98 constructs in public headers, conflicting with ABI canon.

## Ambiguities

- **Worldgen data location**: `data/worldgen/real/` is outside `data/packs/`, so it is unclear whether this is intended to be UPS pack data or a separate canonical data root.
- **Pack manifests**: `.gitignore` only allows `pack.manifest` under `data/packs/**`. `data/worldgen/real/` currently uses `pack_manifest.json` only; manifest conventions for this path are undefined.
- **TESTX scope**: Expected taxonomy and enforcement responsibilities for TESTX are undocumented.

## Proposed minimal fixes (Phase 1+)

1. **TESTX definition**: Locate or define TESTX entry points, commands, and coverage taxonomy; document in `docs/audit/TESTX_COVERAGE_REPORT.md`.
2. **Version files**: Add `version/build.txt`, `engine.version`, `game.version` and enforce printing in all test binaries.
3. **Canon consolidation**: Identify conflicts between `docs/architecture/` and `docs/architectureitecture/`; archive or cross-link legacy docs.
4. **Public header hygiene**: Separate public/private headers, remove render/UI/platform from the engine public surface.
5. **C89/C++98 compliance**: Eliminate inline logic and C99 features from public headers; enforce via TESTX.
6. **Worldgen data root**: Decide whether `data/worldgen/real/` is a UPS pack root or a canonical data root; adjust manifests and docs accordingly.
7. **UPS docs**: Add `docs/content/UPS.md` (or rename/alias `UPS_OVERVIEW.md`) and align references.

## Phase 0 conclusion

Phase 0 is complete. The repo contains the required canonical docs in `docs/architecture/`, but TESTX, version governance, and public header hygiene are missing or ambiguous. These gaps must be addressed in later phases without weakening canon.
