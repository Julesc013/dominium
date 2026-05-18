Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none
Stability: provisional
Task: NAME-00
Machine-Readable Source: `contracts/repo/naming.contract.toml`

# Directory Naming

Directory names encode ownership, not implementation habit.

The current source repository root set remains the post-CONVERGE set governed by `contracts/repo/layout.contract.toml`, `contracts/repo/root_allowlist.toml`, and `contracts/repo/layout_exceptions.toml`:

```text
.aide/
.github/
apps/
engine/
game/
runtime/
contracts/
content/
docs/
tests/
tools/
scripts/
cmake/
external/
release/
archive/
```

Optional future roots remain only `sdk/` and `examples/`, and only after a contract update.

## Root Rule

Do not create top-level roots for implementation convenience, era, status, or temporary project vocabulary.

Forbidden as new top-level source roots:

```text
src/
source/
sources/
code/
impl/
common/
shared/
misc/
new/
old/
modern/
legacy/
classic/
universal/
compat/
```

Allowed term exceptions are narrow:

```text
archive/legacy/
contracts/compatibility/
docs/compatibility/
```

`archive/legacy/` is historical classification. `contracts/compatibility/` and `docs/compatibility/` are real compatibility ownership surfaces.

## Singular And Plural

Use singular names for one ownership plane, subsystem, service family, or contract category:

```text
game/domain/
runtime/render/
runtime/platform/
runtime/shell/
contracts/schema/
contracts/registry/
contracts/package/
contracts/profile/
contracts/protocol/
```

Use plural names for collections of peer artifacts, authored payloads, products, tools, tests, or docs:

```text
apps/
tools/
tests/
docs/domains/
content/domains/
content/packs/
content/profiles/
content/templates/
```

The practical rule is:

```text
singular = one ownership surface
plural = many peer artifacts or authored items
```

## Planned Naming Migrations

These are target names for future reviewed cleanup only:

| Current | Target |
| --- | --- |
| `runtime/appshell/` | `runtime/shell/` |
| `game/domains/` | `game/domain/` |
| `content/domain-data/` | `content/domains/` |
| `contracts/schemas/` | `contracts/schema/` |
| `contracts/registries/` | `contracts/registry/` |
| `contracts/packages/` | `contracts/package/` |
| `contracts/profiles/` | `contracts/profile/` |
| `contracts/protocols/` | `contracts/protocol/` |
| `contracts/projections/` | `contracts/projection/` |

NAME-00 does not authorize applying those renames, creating aliases, moving files, rewriting imports, rewriting references, or retiring layout exceptions.

## Leaf Adapter Rule

API, OS, toolchain, and backend names are allowed as leaf adapters when they name an external interface:

```text
runtime/platform/win32/
runtime/platform/cocoa/
runtime/render/opengl/
runtime/render/direct3d/
cmake/toolchains/msvc/
```

They must not become top-level roots:

```text
win32/
opengl/
visualstudio/
xcode/
```

## Transitional Debt

Existing bad roots under active exceptions remain visible debt. Their presence is not new authority and does not authorize adding new files there.

Future MOVE-BULK refinement must route safe files to ownership-based targets from the naming contract, while deferring identity-sensitive, ABI-sensitive, runtime-sensitive, or policy-sensitive material until proof exists.
