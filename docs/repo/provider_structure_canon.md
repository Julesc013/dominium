Status: CANONICAL
Last Reviewed: 2026-05-23
Supersedes: PROVIDER-MODEL-01 path guidance where this file is more specific
Superseded By: none
Stability: provisional
Task: PROVIDER-STRUCTURE-CANON-01

# Provider Structure Canon

Dominium service identity is first-party. Provider implementation is
replaceable. Profiles select providers. Third-party types are fenced. Apps do
not hardwire providers. Contracts define the law.

## Structure Law

Service roots use Dominium-owned names:

- `runtime/platform`
- `runtime/input`
- `runtime/render`
- `runtime/audio`
- `runtime/asset`
- `runtime/script`
- `runtime/ui`
- `runtime/storage`
- `runtime/diagnostics`
- `runtime/command`
- `runtime/view`
- `runtime/projection`

Provider implementations live under the service root:

```text
runtime/<service>/providers/<provider>/
```

Provider folders name the exact implementation API when that matters:

- `sdl2`, not `sdl`, when the implementation is SDL2-specific.
- `lua54` or `lua55`, not `lua`, when the ABI/runtime version matters.
- `opengl33`, not a loose OpenGL bucket, for an OpenGL 3.3 provider.
- `direct3d11`, not DirectX, for a Direct3D 11 provider.
- `raylib`, `rlgl`, `rlsw`, `raygui`, and `raudio` only inside their service
  provider roots.

Provider IDs are versioned semantic IDs:

```text
domino.provider.<service>.<provider>.v<N>
dominium.provider.<service>.<provider>.v<N>
```

The implementation path is a locator, not identity.

## Third-Party Policy

Third-party source belongs under:

```text
external/upstream/<dependency>/
external/licenses/
external/manifests/
external/patches/<dependency>/
```

Do not create both `external/upstream` and `external/vendor` for the same source
without an explicit split between pristine upstream and patched vendored copies.

Third-party headers, ABI types, and object handles must not appear in contracts,
saves, replays, pack schemas, public ABI, game deterministic law, or engine
state. Translate to Dominium-owned types inside provider code.

## Contracts And Profiles

Provider law belongs under:

```text
contracts/service/
contracts/provider/
contracts/capability/
contracts/schema/runtime/<service>/
contracts/profile/
```

Provider choices belong in profiles:

```text
release/profiles/
content/profiles/
```

`release/profiles` contains build, dev, release, and validation recipes.
`content/profiles` contains authored runtime, user, and game profile payloads.
Do not add a top-level `profiles/`.

## App Rule

Apps remain generic product shells:

```text
apps/client/
apps/workbench/
apps/launcher/
apps/setup/
apps/server/
```

Do not create app-variant roots such as `apps/client/rendered/raylib` or
`apps/workbench/raylib`. Temporary proofs, when explicitly authorized, must stay
under `apps/<product>/proof/<provider>_boot` with a retirement note.

## Current Provider Split

The render null and software providers are canonicalized as:

```text
runtime/render/providers/null/
runtime/render/providers/software/
```

The current provider folders contain the existing C provider surfaces and the
Python snapshot provider modules:

```text
runtime/render/providers/null/d_gfx_null.c
runtime/render/providers/null/d_gfx_stub.c
runtime/render/providers/null/null_renderer.py
runtime/render/providers/software/d_gfx_soft.c
runtime/render/providers/software/software_renderer.py
```

Other provider-like service surfaces, such as storage and package validation,
remain explicit pending splits unless a later task proves a clean provider
boundary. Do not move broad service implementations into `providers/` just to
satisfy naming.

## Non-Goals

This policy does not implement provider loading, automatic selection, dynamic
libraries, raylib/SDL/Lua integrations, renderer behavior, native GUI behavior,
Workbench UI, package mounting, or product runtime features.
