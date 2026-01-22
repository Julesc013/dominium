# Headless and Zero-Pack Boot

All products must boot and provide CLI-only functionality with zero packs
installed. No assets are embedded in executables.

## Zero-pack expectations
- `--help`, `--version`, `--build-info`, `--status`, and `--smoke` never require
  packs or content installs
- Content packs are only loaded when explicitly requested by the game runtime
  or tooling workflows

## Headless behavior
- Server is headless by design; no windowing/GPU/audio dependencies
- Client supports CLI-only modes and an explicit null renderer path
- Tools and setup use CLI-only smoke/status paths

## Render and cache policy
- Renderer backends are selected at runtime; explicit selection must fail if
  unavailable
- Shader caches are optional and disposable; boot must not depend on caches

