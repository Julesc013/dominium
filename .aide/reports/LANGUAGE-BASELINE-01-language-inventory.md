# LANGUAGE-BASELINE-01 Language Inventory

## Active Baseline

- C standard: C17.
- C++ standard: C++17.
- C extensions: OFF.
- C++ extensions: OFF.
- Active OS floor: Windows 7 SP1, macOS 10.9.5, Linux.

## Updated Build Surfaces

- Root `CMakeLists.txt` now sets `CMAKE_C_STANDARD 17` and `CMAKE_CXX_STANDARD 17`.
- Active target `CMakeLists.txt` files now request C17/C++17 where a standard is declared.
- Active verify/dev/release `CMakePresets.json` cache entries now use C17/C++17.
- `tools/build/generate_user_presets.py` now emits C17/C++17 user presets.
- `tests/ops/build_matrix_tests.py` now expects C17/C++17 strict keys.

## Preserved ABI Posture

Public ABI remains C-compatible. C++17 implementation is allowed behind public
ABI boundaries, but C++ ABI, STL types, exceptions, RTTI, and platform headers
must not leak into stable public ABI.

## macOS 10.9.5 Subset

The active C++17 subset forbids required use of library surfaces that are not
portable to the macOS 10.9.5 deployment target, including `std::filesystem`,
`std::pmr`, `std::to_chars`, `std::from_chars`, and throwing `std::any`,
`std::optional`, or `std::variant` access paths.

## Legacy Projection Warnings

The language baseline validator reports 7 warning-only legacy projection presets
that still declare `DOM_LANG_MODE=c89_cpp98`:

- `ide-win-vc6-win9x-client-gui`
- `ide-win-vc6-nt4-server-cli`
- `ide-win-vc71-xp-launcher-gui`
- `ide-win-vs2015-win10-1507-1607-setup-gui`
- `ide-mac-cw-classic-launcher-gui`
- `ide-mac-xcode3-universal-setup-gui`
- `ide-linux-gcc295-legacy-client-gui`

These are not active mainline presets.
