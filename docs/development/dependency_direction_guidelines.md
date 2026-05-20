Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Owner: contracts.repo

# Dependency Direction Guidelines

Run the dependency direction validator before closing work that changes
includes, imports, CMake references, public headers, contracts, tools, or root
ownership:

```powershell
python tools/validators/repo/check_dependency_directions.py --repo-root . --strict
```

For normal task closeout, run the fast strict gate:

```powershell
python tools/test/run_fast_strict.py --repo-root .
```

## Practical Rules

Keep `engine/` below everything else. Engine code must not include or import
runtime, game, apps, tools, release, content, or archive paths.

Keep `runtime/` out of product shells. Runtime may use engine and contracts, but
must not depend on `apps/`.

Keep `game/` focused on domain law. Game may use engine/contracts and declared
content interfaces, but should not reach host/platform/render/UI providers
directly.

Keep `apps/` thin. App code composes runtime, game, and contracts. Shared logic
belongs in the appropriate owner, not in an app and not in tools.

Keep `contracts/` pure. Contract files can describe paths and IDs, but must not
include or import implementation roots.

Keep `content/` as data. Content may reference schemas/contracts, but should not
import runtime/game/engine code.

Keep `tools/` one-way. Tools may inspect everything. Product/runtime/engine/game
code must not depend on tools.

Keep `archive/` inactive. Active source must not include, import, or build
against archived material.

## Adding A Dependency

Before adding a dependency, decide which of these it really is:

- A law/data contract: add or reference a contract surface.
- An implementation helper: move it to the owner that needs it.
- A platform/provider service: place it behind runtime/provider boundaries.
- A product composition detail: keep it in apps and avoid pushing it downward.
- A test or tool inspection: keep it under tests/tools and out of runtime code.

If a temporary violation is unavoidable, add a precise exception in
`contracts/repo/dependency_direction_exceptions.toml`. The exception must name
the exact path, source root, target root, edge type, owner, reason, status, and
retirement task. Broad exceptions are not allowed.

## Fixing Violations

When the validator reports a violation:

1. Confirm whether it is a real include/import edge or a false-positive path
   reference.
2. If it is real, prefer removing the dependency or moving code to the correct
   owner.
3. If the dependency represents a missing contract, create that contract in a
   later bounded governance task.
4. If immediate removal is unsafe, record a narrow exception and a repair task.

Do not rename tests, delete checks, or weaken validators to make the graph look
clean.
