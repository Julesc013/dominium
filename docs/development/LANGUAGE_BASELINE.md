Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: `docs/reference/specs/SPEC_LANGUAGE_BASELINES.md` C89/C++98 wording before 2026-05-21
Superseded By: none
Stability: provisional
Binding Sources: `contracts/build/language_baseline.contract.toml`, `contracts/abi/c_api.contract.toml`, `contracts/abi/language_boundary.contract.toml`

# Language Baseline

Dominium mainline now builds as C17 and C++17.

The active floor is Windows 7 SP1, macOS 10.9.5, and Linux. C89/C++98 remains a
historical or future research lane, not the active mainline build law.

## Build Contract

- C translation units compile as C17 with extensions off.
- C++ translation units compile as C++17 with extensions off.
- Public ABI remains C-compatible.
- C++ ABI, STL containers, exceptions, RTTI, allocator objects, and class
  layouts do not cross stable public ABI boundaries.
- Deterministic replay, save, packet, and wire formats use explicit schemas or
  encodings, not raw compiler object layout.

## Mainline Placement

- `engine/`: C17 for public ABI-adjacent and deterministic substrate code;
  C++17 may be used for private implementation where ownership allows it.
- `game/`: C++17 primary, with C17 for deterministic packet/math/hash/save bits
  that need C-compatible reuse.
- `runtime/`: C++17 for resource, platform, renderer, shell, and service
  implementation; C17 for C-callable facades.
- `apps/`: C++17 primary.
- `tools/`: Python or C++17/C17 according to tool ownership.
- `contracts/` and `content/`: data and machine-readable law, not executable
  language authority.

## macOS 10.9.5 Subset

C++17 language mode is allowed, but the standard-library subset is restricted.
Do not require `std::filesystem`, `std::pmr`, `std::to_chars`,
`std::from_chars`, `std::any`, or throwing `std::optional`/`std::variant`
access paths for mainline macOS 10.9.5 compatibility.

Prefer project path/file abstractions, explicit result values, `has_value`,
`operator bool`, `operator*`, and no-exception low-level paths.

## Validation

Run:

```text
python tools/validators/build/check_language_baseline.py --repo-root . --strict
python tools/validators/build/check_cpp17_forbidden_library_use.py --repo-root . --strict
```

These checks are part of the normal fast strict gate.
