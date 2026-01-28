# Universal Pack System (UPS) Overview

This document is canonical for content-level UPS behavior. It MUST be read
alongside `docs/architectureitecture/INVARIANTS.md` and `docs/architectureitecture/TERMINOLOGY.md`.

## Core Contract

- Executables MUST be content-agnostic and MUST boot with zero packs installed.
- Pack manifests MUST be loaded independently of pack contents.
- Content MUST be resolved by capability only; file paths and pack names are not
  resolution keys.
- Capability resolution MUST be deterministic for the same inputs.
- Precedence MUST be explicit and data-driven; the engine MUST NOT hardcode
  tier ordering.

## Zero-Asset Boot Guarantee

- Engine and game binaries MUST run with no packs present.
- Missing capabilities MUST trigger explicit degradation, not silent coercion.
- All fallback behavior MUST be code-level and deterministic.

## Capability Resolution Rules

- Packs declare capabilities they provide and capabilities they require.
- Multiple packs MAY provide the same capability; providers are ordered by
  explicit precedence and deterministic tie-breaks.
- If a required capability is missing, the system MUST either:
  - downgrade compatibility mode, or
  - disable the dependent feature, or
  - activate a documented fallback.

## Save and Replay Portability

- Saves and replays MUST reference pack IDs and capability requirements only.
- Manifest hashes MUST be recorded for verification.
- No file paths are permitted in save/replay metadata.

## Derived Data and Caches

- Generated data MUST be written to `build/cache/assets/`.
- Packs MUST contain source/open formats only.
- Cache deletion MUST be tolerated at any time.

## Mod Additivity and Supersession

- Mods MUST be additive by default.
- Mods MAY add capabilities, schemas, or data.
- Mods MUST NOT remove core schemas or redefine existing semantics.
- Any supersession MUST be declared explicitly; runtime MUST warn and sandbox.

## References

- Pack manifest format: `docs/pack_format/PACK_MANIFEST.md`
- Engine UPS API: `docs/engine/UPS_RUNTIME.md`
