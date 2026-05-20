Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Task: NAME-00
Machine-Readable Source: `contracts/build/language_baseline.contract.toml`

# Language Ownership

Language placement follows ownership and determinism obligations.

## Active Rule

| Root | Allowed by default | Must not own |
| --- | --- | --- |
| `engine/` | C17 mainline; C++17 private implementation only where ownership allows; public ABI remains C-compatible | Python runtime behavior, shell runtime behavior, C++ ABI leakage |
| `game/` | C++17 primary; C17 for deterministic packet/math/hash/save bits | platform adapters, product shell behavior, C++ ABI leakage |
| `runtime/` | C++17 for services/platform/render/resource internals; C17 for C-callable facades | game truth, domain law, process authority |
| `apps/` | C++17 or product-specific thin shell language | simulation truth, domain law, runtime adapter ownership |
| `contracts/` | JSON, TOML, YAML, schema, manifest, registry, policy, matrix, lock | executable runtime behavior |
| `content/` | data, assets, packs, profiles, templates, themes, locale | executable code, truth mutation |
| `tools/` | Python, PowerShell, Bash, CMD, CMake helpers, C17/C++17 tooling, codegen | runtime dependency from product code |
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

Public engine headers must remain C17 C-compatible and C++17-consumable without leaking C++ ABI. This is checked by the ABI/header validators and build boundary guardrails.

## Toolchain Rule

The active OS floor is Windows 7 SP1, macOS 10.9.5, and Linux. C17/C++17 is the active build baseline; retro C89/C++98 lanes are historical or future research only.

## Content And Packs

Content and packs are data. They may declare capabilities, manifests, profiles, rules, and assets through contracts and pack metadata, but untrusted pack code must not mutate authoritative truth directly.

Future compiled or sandboxed extension systems require a separate reviewed capability and trust contract.
