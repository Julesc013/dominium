# Integration Hooks (APRX)

This document enumerates the integration hooks required by the RepoX
automation and integration metadata tests.

## Required Artifacts

- Product registration via CMake (`dom_register_product`).
- Renderer backend registration via CMake (`dom_register_renderer_backend`).
- Platform backend registration via CMake (`dom_register_platform_backend`).
- CLI contracts documented in `docs/app/CLI_CONTRACTS.md`.

## Notes

- Registrations must occur during CMake configuration so the integration
  metadata report can be generated deterministically.
- Hook definitions are declarative only; no runtime behavior is implied.
