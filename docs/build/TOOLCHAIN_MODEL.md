# Toolchain Model

Dominium emits a toolchain descriptor for every build. It is a stable, app-layer view of the compiler/runtime environment without forcing a single vendor.

## Descriptor Fields

The toolchain descriptor includes:

- `id`: legacy compact string (`DOM_TOOLCHAIN_ID`).
- `family`: compiler family label (e.g., `msvc`, `clang`, `clang-cl`, `gcc`, `mingw-w64`).
- `version`: compiler version string (C compiler).
- `stdlib`: standard library label (`msvc-stl`, `libstdc++`, `libc++`).
- `runtime`: runtime/CRT/libc label (e.g., `static:msvc`, `dynamic:glibc`).
- `link`: `static` or `dynamic`.
- `os`, `arch`, `target`: target tokens (`target` is `<os>-<arch>`).
- `os_floor`: declared OS floor string.
- `config`: build configuration label.

## Output Location

The descriptor is emitted as JSON during configure:

```
<build>/generated/toolchain_descriptor.json
```

The same fields are printed in `--build-info` as `toolchain_*` keys.

## Overrides

These CMake cache variables override derived values:

- `DOM_TOOLCHAIN_STDLIB`
- `DOM_TOOLCHAIN_RUNTIME`
- `DOM_TOOLCHAIN_LINK`
- `DOM_TARGET_OS_FAMILY` / `DOM_TARGET_OS_MIN` (for `os_floor`)
- `DOM_BUILD_MODE` (for `config`)

If not overridden, defaults are best-effort and may report `unknown` or `unspecified`.

## Toolchain Gate

`DOM_TOOLCHAIN_STRICT` controls whether non-canonical toolchains or generators fail configuration.

- `OFF` (default): configure continues with warnings.
- `ON`: configure fails on non-canonical toolchains/generators.
