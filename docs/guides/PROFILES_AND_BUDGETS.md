# Profiles and Budgets (HWCAPS0)

Status: draft.
Scope: selecting execution profiles and safe budget overrides.

## Selecting a Profile
Profiles are data-defined under `data/defaults/profiles/*.tlv`. Server and
client launch configuration should point to one profile ID or file path:
- retro_1990s
- baseline_2010
- modern_2020
- server_mmo

Selection affects backends and budgets only; it never changes gameplay meaning.

## Safe Budget Overrides
Override budgets by editing the profile file or supplying a profile variant:
- Adjust base budgets (cpu/io/net) in abstract units.
- Keep deterministic scaling rules (no wall-clock inputs).
- Preserve scalar + exec2 fallbacks.
- Update degradation_policy_id to match intended behavior.

## Disabling SIMD/GPU/Threads via Server Settings
Use law constraint flags (evaluated by governance) to gate execution:
- allow_multithread = 0 disables exec3_parallel.
- allow_simd = 0 disables SIMD kernels.
- allow_gpu_derived = 0 disables GPU-derived kernels.

These flags override profile preferences and are always audited.

## Examples
Spectate-only museum server:
- Profile: server_mmo
- allow_debug_tools = 0
- allow_modified_clients = 0
- allow_unauthenticated = 0

Anarchy server:
- Profile: modern_2020
- allow_debug_tools = 1
- allow_modified_clients = 1
- allow_unauthenticated = 1

Retro client mode:
- Profile: retro_1990s
- allow_simd = 0
- allow_gpu_derived = 0
- allow_multithread = 0
