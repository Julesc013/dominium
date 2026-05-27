# Reader Brief — Dominium Architecture III

## What This Chat Was About

This chat developed Dominium’s launcher, platform/render backend, software renderer, script, camera/view, keybinding, and support-tier plans. The launcher became a process-spawning system: it collects settings and executes separate client/server binaries rather than switching modes in-process. The backend/core launcher logic should be C89, while per-binary frontends may use C++98. Client and server binaries may be single-system builds selected by the launcher and scripts.

The chat also replaced the earlier `vector_soft` idea with a single universal `software` renderer that works on every platform and supports both vector primitives and textured graphics. Every renderer should support vector-only and full graphics modes so the user can toggle CAD-style views, full graphics, missing-asset fallback, and performance modes. The latest renderer list is DX9.0c, DX11, GL1.1, GL2, VK1, and software. DX12 remains unresolved because it appeared earlier but was omitted from the latest user list.

The view system requirements expanded to include instant seamless zoom, instant switching between top-down 2D and first-person 3D, vector/graphics modes per view, and arbitrary cameras for free cam, map views, HUD cameras, CCTV, overlays, windows, and content creation. These must remain client/render-side and must not affect deterministic sim state.

The user finalized platform support tiers: Tier 1 is Windows NT 2000 SP4-latest, Mac OS X 10.6-10.14, Linux 3.2-current; Tier 2 extends to Windows 98 SE-Me, Mac OS 9-9.2, Mac OS X 10.6-15.0, Linux 2.6.18-current; Tier 3 covers MS-DOS 3.3-6.2, Windows 3, Windows 95-Me, NT 2000 SP4-latest, Mac OS 8.5-9.2, Mac OS X 10.0-latest, Linux 2.4-current. These are user decisions, but external feasibility must be verified.

## Most Important Things to Know

- Launcher executes separate client/server binaries.
- Launcher backend/core is C89.
- Frontends may use C++98.
- Primary scripts: `dominium`, `setup`, `dom-client`, `dom-server`.
- `setup` supports install/repair/uninstall.
- `vector_soft` is superseded.
- Universal `software` renderer is required.
- Every renderer supports vector and graphics modes.
- Latest renderers: DX9.0c, DX11, GL1.1, GL2, VK1, software.
- DX12 is unresolved/deferred.
- Latest platform categories: POSIX, SDL1, SDL2, Native.
- X11/Wayland placement is unresolved.
- Instant zoom/2D/3D/vector/graphics switching is required.
- Arbitrary cameras are required.
- Final support tiers are user-defined and must be preserved.
- Uploaded launcher files must be inspected before code changes.

## Active Plans or Workstreams

- Launcher C89 core and C++98 frontends.
- Launch plan and platform spawn API.
- Unified scripts and setup wrappers.
- Universal software renderer.
- Render/view/camera architecture.
- Input/keybinding spec.
- Platform support tiers and capability matrix.
- Uploaded launcher code refactor.

## Decisions Already Made

- Use separate client/server binaries.
- Use C89 launcher backend/core.
- Allow C++98 frontends.
- Use `dominium` and `setup` as primary commands.
- Use universal `software` renderer.
- Every renderer must support vector/full modes.
- Preserve final Tier 1/2/3 OS support ranges.

## Pending Tasks

- Inspect files.
- Resolve platform taxonomy.
- Resolve DX12 status.
- Update docs.
- Implement launcher core/model/viewmodel.
- Implement spawn API.
- Add scripts/CMake rules.
- Implement software renderer and render modes.
- Verify external compatibility claims.

## Open Questions

- Is DX12 in scope?
- Are X11/Wayland explicit platform values or Native subtypes?
- Is POSIX headless-only?
- What launcher config format should be used?
- Are old script names aliases?
- What setup technology will be used?

## Files / Artifacts / Prompts to Preserve

- `/mnt/data/dominium.7z`
- `/mnt/data/dom_launcher_view.c`
- `/mnt/data/dom_launcher_view.h`
- `/mnt/data/CMakeLists.txt`
- `/mnt/data/dom_launcher_main.c`
- Codex prompts for docs/platform/render/scripts, launcher build/test, input/keybindings, uploaded launcher refactor.
- F1-F12 map.
- Support tier table.
- Capability matrix draft.

## What to Verify Before Acting

- Uploaded files and repo state.
- DX12 status.
- X11/Wayland/POSIX/Native taxonomy.
- Linux kernel/libc/toolchain claims.
- SDL/DirectX/OpenGL/Vulkan/Mac OS feasibility.
- Actual CMake target names and existing input/render APIs.

## Best Next Step

Inspect the uploaded launcher files and repo state, then ask/decide the two blocking taxonomy questions: DX12 status and X11/Wayland/POSIX/Native mapping.
