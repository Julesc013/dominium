# SPEC_SYS_CAPS_FIELDS (HWCAPS0)

Schema ID: SYS_CAPS_FIELDS
Schema Version: 1.0.0
Status: binding.
Scope: field list and semantics for SysCaps v1.

## Field Encoding Rules
- All integers are explicit; no implicit defaults.
- `0` means unknown for numeric estimates unless otherwise stated.
- `bool/unknown` uses a tri-state: unknown | false | true.
- Enums include an explicit `unknown` value.
- Unknown values must be treated conservatively by policy.

## Top-Level
- version_major: u32
- version_minor: u32
- cpu: struct
- gpu: struct
- storage: struct
- network: struct
- platform: struct

## CPU
- logical_cores: u32 (0 = unknown)
- physical_cores_estimate: u32 (0 = unknown)
- smt_present: bool/unknown
- core_classes: unknown | homogeneous | heterogeneous
- perf_cores_estimate: u32 (0 = unknown)
- eff_cores_estimate: u32 (0 = unknown)
- numa_nodes_estimate: u32 (0 = unknown; otherwise >= 1)
- cache_class:
  - l3_size_class: tiny | small | medium | large | huge | unknown
  - vcache_present: bool/unknown
- simd_caps:
  - sse2: bool/unknown
  - sse4: bool/unknown
  - avx2: bool/unknown
  - avx512: bool/unknown
  - neon: bool/unknown
  - sve: bool/unknown

## GPU
- has_gpu: bool
- gpu_memory_model: unified | discrete | unknown
- has_compute_queue: bool/unknown
- gpu_class: none | low | mid | high | unknown

## Storage
- storage_class: hdd | ssd | nvme | unknown
- direct_storage_available: bool/unknown

## Network
- net_class: offline | lan | wan | unknown

## Platform
- os_family: windows | linux | macos | unknown
- arch_family: x86 | x64 | arm64 | unknown

## Deterministic Hashing
Canonical hashing must serialize fields in the order listed above using
explicit little-endian encoding for integers and enum values.
