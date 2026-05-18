Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none
Stability: provisional
Task: NAME-00
Machine-Readable Source: `contracts/repo/naming.contract.toml`

# Language Ownership

Language placement follows ownership and determinism obligations.

## Active Rule

| Root | Allowed by default | Must not own |
| --- | --- | --- |
| `engine/` | C89 and public headers parseable by C++98 | Python runtime behavior, shell runtime behavior, modern C++ without exception |
| `game/` | C89 or C++98 | platform adapters, product shell behavior, modern C++ without exception |
| `runtime/` | C89/C++98; isolated platform adapter language where required | game truth, domain law, process authority |
| `apps/` | C++98/C89 or product-specific thin shell language | simulation truth, domain law, runtime adapter ownership |
| `contracts/` | JSON, TOML, YAML, schema, manifest, registry, policy, matrix, lock | executable runtime behavior |
| `content/` | data, assets, packs, profiles, templates, themes, locale | executable code, truth mutation |
| `tools/` | Python, PowerShell, Bash, CMD, CMake helpers, C89/C++98 tooling, codegen | runtime dependency from product code |
| `scripts/` | thin wrappers in Python, PowerShell, Bash, CMD | product behavior, simulation truth |
| `cmake/` | CMake modules, presets, toolchains | source domain ownership, generated build output |
| `external/` | third-party language as vendored | Dominium-owned source without reclassification |
| `archive/` | historical/superseded/quarantined material | active authority without review |
| `.aide/` | AIDE policy, context, evidence, scripts | secrets, raw provider logs, local cache state |

## Existing Debt

The current repository still contains Python in active `engine/`, `game/`, and `runtime/` paths and active Python in former bad roots such as `core/`, `control/`, `compat/`, `lib/`, `meta/`, `net/`, `validation/`, and related exceptions.

NAME-00 classifies that as transitional debt. It does not convert languages, move files, rewrite imports, create shims, or change runtime behavior.

Current redo counts:

- `engine/**/*.py`: 19 tracked files.
- `game/**/*.py`: 299 tracked files.
- `runtime/**/*.py`: 37 tracked files.
- former bad-root Python placement remains warning-class and deferred to owner-specific MOVE-BULK gates.

These warnings are not final architecture approval. They are a ledger for later conversion, relocation, or isolation work.

## Public Header Rule

Public engine headers must remain C89 and C++98 parseable. This is already stated in `docs/engine/API_SPINE.md` and checked by the build boundary guardrails described in `docs/build/BOUNDARY_ENFORCEMENT.md`.

## Toolchain Rule

Do not couple OS floors to language standards. `docs/build/TRANSITION_DO_NOTS.md` keeps C89/C++98 discipline separate from platform support and toolchain status.

## Content And Packs

Content and packs are data. They may declare capabilities, manifests, profiles, rules, and assets through contracts and pack metadata, but untrusted pack code must not mutate authoritative truth directly.

Future compiled or sandboxed extension systems require a separate reviewed capability and trust contract.
