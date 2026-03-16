Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RESTRUCTURE
Replacement Target: executed post-v0.0.0 layout migration plan with shim retirement after one stable release

# Future Layout Proposal

This document is a no-move planning artifact for the future repository restructure. It uses the current repository inventory, canon reconciliation, and the existing build/entrypoint surfaces to define a target layout that can be reached incrementally without changing semantics, build outputs, product ids, or install behavior.

## Purpose

- Keep v0.0.0 shippable without churn.
- Define a future physical layout that matches the Constitutional Architecture instead of historical growth.
- Use virtual paths, AppShell entrypoint unification, validation unification, and compatibility shims so later moves are non-breaking.
- Reduce circular dependency risk by making product wrappers and UI/platform adapters physically separate from authoritative engines.

## Inputs Used

- `docs/audit/REPO_REVIEW_2_FINAL.md`
- `docs/audit/REPO_REVIEW_3_FINAL.md`
- `docs/audit/ENTRYPOINT_MAP.md`
- `docs/audit/VALIDATION_STACK_MAP.md`
- `docs/audit/MODULE_DUPLICATION_REPORT.md`
- `data/audit/repo_inventory.json`

## Proposed Top-Level Layout

```text
/src
  /core
  /geo
  /astro
  /logic
  /sys
  /proc
  /compat
  /lib
  /appshell
  /platform
  /ui
    /rendered
    /native
  /products
    /engine
    /game
    /client
    /server
    /setup
    /launcher
    /tools

/tools
  /xstack
  /audit
  /mvp
  /compat
  /lib
  /release
  /dist

/data
  /registries
  /profiles
  /locks
  /schemas
  /regression

/packs
  /base
  /official
  /mods

/docs
  /canon
  /audit
  /mvp
  /release
  /restructure
```

## Layering Rules

- `src/core` is the lowest runtime layer. It owns truth-model fundamentals, time, deterministic execution, proof/anchor primitives, and shared runtime kernels.
- `src/geo`, `src/astro`, `src/logic`, `src/sys`, and `src/proc` depend downward on `src/core`, not on product/UI/platform layers.
- `src/compat` and `src/lib` sit beside domain layers and may depend on core/domain contracts, but products and tools must not bypass them.
- `src/appshell` owns bootstrap, command dispatch, IPC, supervisor, TUI, virtual paths, install discovery, and product boot policy.
- `src/platform` contains capability probes and optional OS-family adapters only.
- `src/ui` consumes command descriptors, view artifacts, logs, and UI model state only. It never owns business logic or truth mutation.
- `src/products` contains thin entry wrappers and product-specific composition surfaces. Products compose lower layers; lower layers must not import products.
- `tools/*` remains the non-runtime surface for review, audit, release, migration, and developer workflows.

## Circular Dependency Policy

- Products may depend on `appshell`, `compat`, `lib`, `ui`, `platform`, and domain/core layers.
- `ui` may depend on `appshell` command/view contracts and derived artifacts, not on truth engines.
- `platform` may depend on `appshell`-level interfaces, not on products or truth/domain engines.
- `compat` may inspect domain contracts, but domain engines must not call back into tooling or release surfaces.
- `tools` may depend broadly for analysis and verification; runtime code must not depend on `tools`.

## Mapping Table

The table below maps current module clusters to proposed locations. The stability class here is the move-plan classification for the physical layout, not a change to runtime semantic stability.

| Current Path | Proposed Path | Module Role | Stability Class | Dependencies | Risk |
| --- | --- | --- | --- | --- | --- |
| `src/core`, `src/runtime`, `src/time`, `src/meta`, `src/reality`, `src/universe` | `/src/core/*` | truth kernel, determinism, time, proof primitives | `provisional` | none upward; base runtime only | `high` |
| `src/field`, `src/fields` | `/src/core/fields/*` | canonical field model and field execution surfaces | `provisional` | core, geo, proc | `high` |
| `src/geo/*` | `/src/geo/*` | topology, metric, projection, overlay merge | `provisional` | core, time | `medium` |
| `src/worldgen/mw/*` | `/src/astro/mw/*` | galaxy/system procedural refinement | `provisional` | core, geo, time | `medium` |
| `src/worldgen/earth/*` | `/src/astro/earth/*` | Earth climate, hydrology, terrain, lighting, material proxies | `provisional` | core, geo, astro shared | `high` |
| `src/worldgen/galaxy/*` | `/src/astro/gal/*` | galaxy metadata and compact-object stubs | `provisional` | core, geo, astro shared | `medium` |
| `src/astro/*` | `/src/astro/shared/*`, `/src/astro/sol/*` | shared ephemeris, illumination, orbit views | `provisional` | core, geo, time | `medium` |
| `src/logic/*` | `/src/logic/*` | logic L1/L2 compile/eval/fault tooling | `provisional` | core, geo, proc | `medium` |
| `src/system/*` | `/src/sys/*` | system composition, collapse/stabilization | `provisional` | core, proc, logic | `high` |
| `src/process/*` | `/src/proc/*` | process definitions, capsules, authoritative mutation | `provisional` | core, geo, logic, sys | `high` |
| `src/pollution/*` | `/src/astro/earth/pollution/*` | bounded Earth pollution/advection domain | `provisional` | core, geo, proc | `medium` |
| `src/compat/*` | `/src/compat/*` | semantic contracts, negotiation, pack compatibility, descriptor emission | `stable interface / provisional placement` | core, geo contracts, lib | `high` |
| `src/lib/*` | `/src/lib/*` | store, installs, instances, saves, exports, bundles | `stable interface / provisional placement` | compat, appshell paths | `high` |
| `src/appshell/*` | `/src/appshell/*` | bootstrap, command engine, TUI, IPC, supervisor, virtual paths | `stable interface / provisional placement` | compat, lib, platform | `high` |
| `src/platform/*` | `/src/platform/*` | platform capability probe and adapter hooks | `provisional` | appshell contracts only | `low` |
| `src/ui/*` | `/src/ui/*` | shared UI model and adapter contracts | `provisional` | appshell command/view contracts | `medium` |
| `src/client/ui/*`, `src/client/render/*` | `/src/ui/rendered/*` | rendered client UI adapters and renderer consumers | `provisional` | ui shared, appshell, derived views | `medium` |
| native adapter stubs under launcher/setup/client surfaces | `/src/ui/native/*` | Win32/GTK/Cocoa thin adapters | `provisional` | ui shared, appshell, platform | `low` |
| `src/server/*` | `/src/products/server/*` plus `/src/appshell/*` for shared control surfaces | product wrapper and headless/runtime composition | `provisional` | appshell, compat, proc, sys | `medium` |
| `tools/mvp/runtime_entry.py` | `/src/products/client/entry.py` | client product entry wrapper | `provisional` | appshell, ui/rendered | `medium` |
| `tools/launcher/launch.py` | `/src/products/launcher/entry.py` | launcher product entry wrapper | `provisional` | appshell, lib, ui/native or tui | `low` |
| `tools/setup/setup_cli.py` | `/src/products/setup/entry.py` | setup product entry wrapper | `provisional` | appshell, compat, lib | `low` |
| `tools/appshell/product_stub_cli.py` | `/src/products/engine/entry.py`, `/src/products/game/entry.py`, `/src/products/tools/entry.py` | thin product stubs | `provisional` | appshell only | `low` |
| `tools/appshell/supervisor_service.py`, `tools/appshell/supervised_product_host.py` | `/src/appshell/supervisor/hosts/*` | supervisor-owned hosted runtime glue | `provisional` | appshell supervisor, compat | `medium` |
| `tools/review/*` | `/tools/review/*` | repository inventory and reconciliation tooling | `provisional` | audit data only | `low` |
| `tools/audit/*`, `tools/auditx/*` | `/tools/audit/*` | architecture/repo/document audit stack | `provisional` | runtime inspection only; no runtime importers | `low` |
| `tools/mvp/*` | `/tools/mvp/*` | release-gate smoke/stress/product boot tooling | `provisional` | appshell, compat, lib | `low` |
| `tools/compatx/*`, `tools/pack/*`, `tools/validation/*`, `tools/validate/*` | `/tools/compat/*` and `/tools/release/*` | validation and compatibility adapters | `provisional` | compat, lib, schema data | `medium` |
| `tools/xstack/*` | `/tools/xstack/*` | CI/test/orchestration meta-layer | `provisional` | may depend broadly; never runtime | `medium` |
| `schema/*` and `schemas/*` | `/data/schemas/*` | source schemas and generated schema mirrors | `provisional` | validators, compat, release tooling | `high` |
| `data/registries/*` | `/data/registries/*` | canonical runtime registries | `stable semantics / provisional placement` | consumed by compat, lib, appshell, domains | `low` |
| `dist/profiles/*`, `dist/locks/*` | `/data/profiles/*`, `/data/locks/*` with dist mirrors retained via vpath | portable install runtime data | `provisional` | appshell paths, install discovery | `medium` |
| `dist/packs/*` | `/packs/*` with portable mirrors retained via vpath | pack storage and distribution content | `provisional` | lib, pack-compat, install discovery | `medium` |
| layout and architecture docs under `docs/architecture/*` | `/docs/restructure/*` or `/docs/archive/*` | historical layout references | `legacy_reference_only` | canon map only | `low` |

## Migration Strategy

### Phase 1: Namespace Wrappers and Redirects

- Introduce namespace-only wrappers, include-path shims, and import aliases before any physical moves.
- Keep product entrypoints, virtual paths, and `dom` command routing stable.
- Generate mapping-aware documentation so developers stop adding new code to historical buckets.

### Phase 2: Move Leaf Modules First

- Move review, audit, release, and thin adapter leaves first.
- Move product entry wrappers before moving deeper engines.
- Prefer physical relocation of modules with no authoritative truth logic and shallow import graphs.

### Phase 3: Move Core Runtime Clusters With Shims

- Move `compat`, `lib`, `appshell`, UI adapters, and worldgen/astro leaves only after import wrappers are already in place.
- Move `sys`, `proc`, and `core` last among runtime packages.
- Keep old paths as compatibility shims for one stable release window.

### Phase 4: Shim Retirement

- Remove transitional wrappers only after one stable release proves downstream tools, import paths, and product wrappers are clean.
- Re-run convergence gates after each shim-removal batch.

## Guard Rails For Future Move Work

- No semantic changes in move-only pull requests.
- Move one subsystem per pull request.
- Preserve import-path compatibility through explicit wrappers or shims.
- Keep executable names, product ids, pack ids, install ids, and virtual roots unchanged during moves.
- Re-run convergence gates after every subsystem move:
  - AppShell/entrypoint checks
  - validation pipeline
  - product boot matrix
  - supervisor/IPC lanes if affected
  - smoke/stress gates if affected

## Shipping Constraint

No immediate moves are required to ship v0.0.0. The current repo can ship with:

- virtual path resolution in place
- install discovery in place
- AppShell entrypoint unification in place
- unified validation/tool surfaces in place
- compatibility shims in place

This proposal exists to make later physical cleanup incremental instead of disruptive.
