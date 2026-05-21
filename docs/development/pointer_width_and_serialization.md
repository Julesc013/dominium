Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Pointer Width And Serialization

Dominium persisted formats are independent of native pointer width. Saves, replays, network packets, package manifests, renderer IR, domain data, commands, diagnostics, and artifact identity must use fixed-width fields with explicit encodings.

The governing policy lives in `contracts/platform/architecture_policy.contract.toml` and `contracts/platform/pointer_width_policy.schema.json`.

## Allowed Native Use

`size_t` is allowed for in-process memory sizes and container interaction. `ptrdiff_t` is allowed for in-process pointer arithmetic when it does not cross a stable boundary. `uintptr_t` and `intptr_t` are allowed only for local diagnostics and must never be persisted.

Use `u64` for file offsets, replay ticks, canonical hashes, and global IDs where needed. Use `u32` for local dense indices or handles where the domain range is sufficient. Use fixed-width signed and unsigned integer types for stable data.

## Forbidden Stable Use

Stable and persisted formats must not use:

```text
size_t
ptrdiff_t
long
unsigned long
intptr_t
uintptr_t
raw pointer values
compiler object layout
native padding
pointer-order sorting
address hashing
```

These constructs are host facts, not contract facts.

## Encoding

Persisted and protocol fields must declare fixed width and explicit little-endian encoding. Native object layout serialization is forbidden. A stable artifact may not depend on compiler padding, pointer alignment, `sizeof(void*)`, address order, or `long` width.

## Review Rule

If implementation code must touch native-size values near a stable boundary, isolate the conversion at the boundary and name the stable field type explicitly. Do not let the native type appear in schemas, packet definitions, save/replay layouts, renderer IR, package data, or artifact identity.

Run the architecture inventory for descriptive risk review:

```text
python tools/validators/platform/check_architecture_policy.py --repo-root . --inventory
```
