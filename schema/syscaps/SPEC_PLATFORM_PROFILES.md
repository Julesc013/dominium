# SPEC_PLATFORM_PROFILES (HWCAPS0)

Schema ID: PLATFORM_PROFILES
Schema Version: 1.0.0
Status: binding.
Scope: execution-policy profile containers and default profiles.

## Purpose
Define data-driven profiles that pair with SysCaps to select deterministic
execution backends and budgets. Profiles are data-only and must not encode
gameplay semantics.

## Container Format (DTLV v1)
Profiles are stored as DTLV containers with a single chunk:
- Chunk type: `EPRF` (`tag('E','P','R','F')`)
- Chunk version: 1

TLV records inside the chunk use these tags:
- `PID0`: profile_id (string bytes)
- `SCHD`: scheduler_order (array of u32 backend ids)
- `KORD`: kernel_order (array of u32 backend ids)
- `ALOW`: allow_mask (u32 bitmask)
  - bit 0: allow_exec3
  - bit 1: allow_simd
  - bit 2: allow_gpu_derived
- `MINC`: min_cores_for_exec3 (u32)
- `BID0`: budget_profile_id (string bytes)
- `BCAU`: base_cpu_authoritative (u32)
- `BCDR`: base_cpu_derived (u32)
- `BIOD`: base_io_derived (u32)
- `BNET`: base_net (u32)
- `MEMC`: memory_budget_class (u32 enum)
- `DEGR`: degradation_policy_id (string bytes)
- `CSMN`: cpu_scale_min (u32)
- `CSMX`: cpu_scale_max (u32)
- `IOSX`: io_scale_max (u32)
- `NSMX`: net_scale_max (u32)
- `RNDL`: render_allowlist entry (string bytes, repeated)

Required tags: `PID0`, `SCHD`, `KORD`, `ALOW`, `BID0`, `BCAU`, `BCDR`,
`BIOD`, `BNET`, `MEMC`, `DEGR`, `CSMN`, `CSMX`, `IOSX`, `NSMX`.

Unknown tags must be skipped.

## Default Profiles (data/defaults/profiles)
- retro_1990s: exec2 + scalar only, tiny budgets, aggressive degradation.
- baseline_2010: exec3 allowed if cores >= 4, simd allowed when present,
  conservative budgets.
- modern_2020: exec3 preferred, simd preferred, gpu-derived allowed,
  larger derived budgets.
- server_mmo: exec3 preferred, high derived budgets, conservative net budgets,
  gpu-derived off by default.

## Rules
- Profiles may change performance only; never gameplay meaning.
- Deny-by-law overrides allow-by-profile.
- GPU-derived backends are never selected for authoritative tasks.
