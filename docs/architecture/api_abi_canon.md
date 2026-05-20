Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: API-ABI-CANON, DEPENDENCY-DIRECTION, COMMAND-SURFACE, PROVIDER-MODEL, REPLACEMENT-PROTOCOL
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `contracts/public_surface/public_surface.contract.toml`, `contracts/abi/c_api.contract.toml`, `contracts/abi/language_boundary.contract.toml`

# API / ABI Canon

## Purpose

Dominium public ABI is the narrow surface downstream products, Domino-based games,
native shells, providers, modules, tools, and long-lived artifacts may rely on.
Implementation files, directory names, generated outputs, and UI behavior are not
public contract authority by themselves.

Stable public ABI must be boring, explicit, and C-compatible. Private
implementation may change behind the registered surface.

## Public ABI

Stable reusable public ABI is C17 C-compatible unless the public surface registry
declares a different language floor. Public C++17 implementation can exist behind a C
ABI, but C++ classes, templates, STL types, exceptions, and overload-only symbols
must not cross the public C boundary.

Public reusable symbols use `domino_`. Public Dominium product symbols use
`dominium_`. Public macros use `DOMINO_` or `DOMINIUM_`. Stable semantic identity
uses dotted IDs in contracts and registries, not file paths.

Existing `dom_` and `d_` names are treated as provisional existing debt. They are
not frozen by this task; stable promotion requires explicit exception or a
registered replacement.

## Opaque Handles

Owned objects that cross a public ABI use opaque handles:

```c
typedef struct domino_engine domino_engine_t;
```

Creation functions must state ownership and lifetime. Destroy/free functions or
explicit allocators are required when memory crosses a boundary.

## ABI Structs

ABI-visible option, config, descriptor, vtable, and argument structs include
`struct_size`. Public config structs should include `api_version` when the callee
must support forward or backward compatibility. Callers initialize
`struct_size = sizeof(struct_type)`, and callees validate size and version before
using the struct.

Raw public struct layout is not a save, replay, network, or file format.
Serialization uses explicit schemas, protocols, or encodings.

## Results And Refusals

Public APIs return explicit result or refusal codes. Null or zero may be a valid
result only when documented as such. Stable result, diagnostic, and refusal IDs
will be bound to later diagnostic/refusal registries.

## Header Hygiene

Public headers must be guarded, self-contained where practical, and consumable by
C++ through `extern "C"` when they expose C functions. Public headers must avoid
private implementation includes, generated-output includes, broad generic
macros, and short unprefixed global names.

Engine public headers must remain portable. They must not include Windows,
POSIX, Cocoa, OpenGL, Direct3D, Vulkan, Metal, SDL, or equivalent platform
headers. Platform-specific provider headers require explicit platform scope and
registry classification.

## Provider And Module Implications

Provider ABI and module APIs are public only when registered. Workbench modules
and provider surfaces call registered commands, services, or ABI entrypoints;
they must not bind to private internals as a compatibility promise. Stable module
or provider APIs require conformance tests, compatibility policy, and replacement
protocol coverage.

## Proof

The current validator is:

```powershell
python tools/validators/abi/check_public_headers.py --repo-root . --strict
```

The validator catches high-confidence header violations and records provisional
promotion blockers as warnings. Full frozen ABI proof still requires later
consumer compile coverage, compatibility corpus, replacement protocol, and
release/full-gate validation.
