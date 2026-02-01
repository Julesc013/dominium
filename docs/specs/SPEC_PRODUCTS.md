Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- None. Game consumes engine primitives where applicable.

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Dominium Product Contracts

## Product Overview
- Every product is a Domino-based binary located under `repo/products/<product>/<product_version>/core-<core_version>/<OSFam-Arch>/bin/`.
- Each binary self-identifies via a manifest (schema defined elsewhere) and exposes a minimal introspection protocol for the launcher.
- Products must operate solely through Domino abstractions (sim, IO, dgfx/dsys) and repository manifests; no hard-coded paths or platform shortcuts.

## Game
- Single game binary with display modes: GUI, TUI, headless. All modes share the same deterministic sim and IO behaviors.
- Server roles: off/client-only, listen-server, dedicated server. Mode/role selection does not alter simulation determinism or data formats.
- Demo mode is a content/feature restriction only; core logic and save/net/replay formats remain identical.
- Domino responsibilities: simulation loop, world IO (saves/replays), deterministic RNG, and net protocol semantics. Game code must not replace these with platform-native substitutes.
- High-level CLI contract (parsing deferred to later specs):
  - `--mode=gui|tui|headless`
  - `--server=off|listen|dedicated`
  - `--demo`
  - `--instance=<id>`
- Game must run identically when launched directly or via the launcher with the same flags and instance id.

## Launcher
- Responsibilities: discover `DOMINIUM_HOME`, enumerate available products via manifests, launch products with requested actions/modes, and maintain per-instance records (config/saves/logs).
- Launcher never hard-codes game/setup/tools paths; it resolves them from manifests and an introspection call (`--introspect-json` or equivalent).
- Launcher is the primary UX entry point but runtimes remain runnable without it; behaviors must match when flags are equivalent.
- Launcher supervises instance lifecycle and records launcher session/instance IDs but does not modify simulation semantics.

## Setup
- Installs, repairs, uninstalls, and imports products/packs/mods into `DOMINIUM_HOME` without destructive side effects.
- Multiple versions may coexist; Setup must not clobber existing builds or instances. GC removes unused builds/packs safely.
- Repair/uninstall respects existing instances (configs, saves, logs) and leaves them intact unless explicitly removed by user action.
- Setup is itself a product, discoverable and invocable via the launcher and manifests.

## Tools (modcheck, editors, future)
- Tools are first-class products discoverable via manifests and runnable through the launcher.
- modcheck (minimum tool): validates manifests, pack structures, and compatibility against the declared compatibility profile.
- Future tools: asset compiler, pack/world editors, replay analyzers, test harnesses. All must rely on Domino abstractions and repository manifests, not bypass them.

## CLI Modes & Flags (high-level)
- Common platform selection: `--platform=<backend>` mapping to dsys backends (`win32`, `posix_x11`, `posix_wayland`, `posix_headless`, `sdl1`, `sdl2`, `dos16`, `dos32`, `cpm80`, `cpm86`, `android`, `web`, `null`).
- Product-specific flags (conceptual): `--mode`, `--server`, `--demo`, `--instance`, plus future tool/setup options defined in their own specs.
- Flag parsing and validation will be defined in CLI-specific documents; this spec establishes expected presence and semantics.

## Introspection & Protocols
- Each product must support a non-interactive introspection endpoint (e.g., `--introspect-json`) that emits a machine-readable description:
  - product name and type (game/launcher/setup/tool)
  - product version and required Domino core version
  - supported actions/modes (play, dedicated server, install, validate, etc.)
  - supported display/backends and any platform constraints
- Introspection output is versioned and part of the compatibility profile; launcher uses it to present options and enforce compatibility.
- Products must honour introspection declarations; mismatches between declared and actual capabilities are forbidden.

## Instances & DOMINIUM_HOME Integration
- Instance data lives under `instances/<instance_id>/` inside `DOMINIUM_HOME`, containing at minimum config, saves, and logs; products may add subdirectories but must stay within the instance root.
- Launcher selects or creates instances and passes `--instance=<id>` (and optionally launcher session/instance identifiers) to products.
- Products must respect the provided instance id for all writable data; no writes outside the resolved `DOMINIUM_HOME`/instance tree without explicit user consent.
- Instance handling must be deterministic: identical instance content plus identical inputs yield identical outputs, regardless of platform or invocation path.