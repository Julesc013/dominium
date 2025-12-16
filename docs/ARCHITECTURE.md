# Architecture (High-Level)

Dominium is structured as a layered system:
- **Domino**: deterministic, fixed-point simulation engine and supporting runtime subsystems.
- **Dominium**: product layer hosting UI, platform integration, and content workflows on top of Domino.

This document provides a high-level map of the layers and the allowed direction
of dependencies. Detailed subsystem behavior lives in `docs/SPEC_*.md`.

## Directory/Layers (Authoritative)
- Public headers (contracts): `include/domino/**`, `include/dominium/**`
- Implementations: `source/domino/**`, `source/dominium/**`
- Tools: `tools/**`, `source/tools/**`
- Tests: `tests/**`, `source/tests/**`

See `docs/DIRECTORY_CONTEXT.md` for the authoritative layout contract.

## Layering Model
### Deterministic core (Domino)
- Deterministic simulation logic is C90 and must follow `docs/SPEC_DETERMINISM.md`.
- Deterministic paths must not depend on OS time, floating-point math, or platform APIs
  (`docs/LANGUAGE_POLICY.md`).

### Platform/system integration (Domino system layer)
- Platform backends live under `source/domino/system/**` and provide OS/window/files/process abstractions.
- Platform code may be non-deterministic, but must not influence authoritative simulation decisions.

### Product layer (Dominium)
- Product code lives under `source/dominium/**` and is C++98/C89 as configured.
- Dominium hosts UI and runtime loops and interacts with Domino via the public contracts in `include/**`.

## Extension Points
Extension mechanisms are specified per subsystem (see `docs/SPEC_*.md`). Common patterns:
- Versioned POD interfaces across module boundaries (`docs/SPEC_ABI_TEMPLATES.md`, `include/domino/abi.h`).
- Backend selection / facades for platform and renderer subsystems (`docs/SPEC_FACADES_BACKENDS.md`).

## Further Reading
- `docs/OVERVIEW_ARCHITECTURE.md` (narrative overview)
- `docs/SPEC_DOMINIUM_LAYER.md` (Dominium layering rules)
- `docs/SPEC_DOMINO_SUBSYSTEMS.md` (Domino subsystem map)

