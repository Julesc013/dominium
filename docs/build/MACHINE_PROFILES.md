# Machine Profiles

Status: PROVISIONAL

Phase: POST-CONVERGE-10

## Purpose

Machine profiles describe what a host can actually build. They are detected by `tools/build/probe_toolchains.py` and written to ignored local evidence such as:

```text
.dominium.local/toolchains.detected.json
```

## Host Classes

| Host Class | Purpose | Notes |
| --- | --- | --- |
| current Windows MSVC host | canonical Windows verify proof | requires Visual Studio 2022 or another reviewed tuple |
| Windows compatibility host | winnt7/xp research and compatibility lanes | requires protected compatibility review |
| Linux host | GCC/Clang configure/build/test lanes | requires compiler plus build tool |
| macOS host | Xcode/Cocoa configure/build/test lanes | requires Xcode proof |
| research host | classic or retired platform investigations | no support claim |
| self-hosted CI host | repeatable build proof | CI YAML is not a separate matrix authority |

## Detected Fields

The probe records:

- host platform
- Python version
- CMake version
- CMake generator names
- Ninja/build-tool presence
- Visual Studio instances where discoverable
- GCC, Clang, and Xcode presence
- available and blocked toolchain IDs

## Local Policy

`.dominium.local/` is ignored. It may contain machine-local probe output, generated preset data, and temporary build evidence.

`CMakeUserPresets.json` is also ignored. It may be generated for a host, but it must not become committed source authority.
