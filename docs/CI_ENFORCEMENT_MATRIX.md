# CI Enforcement Matrix (ENF0)

This matrix defines mandatory, mechanical CI enforcement for architectural law.
All failures are merge-blocking.

## Enforcement Table

| ID | Description | Enforcement Mechanism | Stage | Failure Mode | Remediation | Rationale |
| --- | --- | --- | --- | --- | --- | --- |
| ARCH-TOP-001 | Top-level `source/`, `src/`, `common_source/` are FORBIDDEN. | Repo layout lint (tools/ci/arch_checks.py) | Configure | CI fail: ARCH-TOP-001 | Remove or relocate the directory into a canonical top-level domain. | Prevents ambiguous ownership and drift. |
| ARCH-OWN-002 | `engine/` and `game/` responsibilities MUST NOT be merged. | Repo layout + target graph check | Configure | CI fail: ARCH-OWN-002 | Split responsibilities and restore separation between engine and game targets. | Preserves core layering and portability. |
| ARCH-DEP-001 | `engine/` MUST NOT reference or link `game/`, `launcher/`, `setup/`, or `tools/`. | Target graph rule + static scan (tools/ci/arch_checks.py) | Configure | CI fail: ARCH-DEP-001 | Remove forbidden references and use engine public APIs only. | Keeps engine as the dependency root. |
| ARCH-DEP-002 | `game/` MAY depend only on `engine/`. | Target graph rule in CMake | Configure | CI fail: ARCH-DEP-002 | Remove illegal dependencies and rewire through engine public APIs. | Maintains clear ownership of rules. |
| ARCH-DEP-003 | `client/` MAY depend only on `engine/` and `game/`. | Target graph rule in CMake | Configure | CI fail: ARCH-DEP-003 | Remove illegal dependencies and use engine/game public APIs. | Prevents client coupling to tools or setup. |
| ARCH-DEP-004 | `server/` MAY depend only on `engine/` and `game/`. | Target graph rule in CMake | Configure | CI fail: ARCH-DEP-004 | Remove illegal dependencies and use engine/game public APIs. | Keeps server authoritative and focused. |
| ARCH-DEP-005 | `tools/` MAY depend only on `engine/` and `game/`. | Target graph rule in CMake | Configure | CI fail: ARCH-DEP-005 | Remove illegal dependencies and use engine/game public APIs. | Avoids tool-to-runtime coupling. |
| ARCH-DEP-006 | `launcher/` and `setup/` MAY depend only on `libs/` and `schema/`. | Target graph rule in CMake | Configure | CI fail: ARCH-DEP-006 | Remove engine/game dependencies and use schema contracts only. | Keeps operational tools separate from runtime. |
| ARCH-INC-001 | `game/` includes from `engine/modules/**` or platform headers are FORBIDDEN. | Compile-time include guard + static scan (tools/ci/arch_checks.py) | Build | CI fail: ARCH-INC-001 | Replace with `engine/include/**` public headers; remove platform headers from game. | Enforces API boundaries. |
| ARCH-INC-002 | `client/`, `server/`, `tools/` include from `engine/modules/**` are FORBIDDEN. | Compile-time include guard + static scan (tools/ci/arch_checks.py) | Build | CI fail: ARCH-INC-002 | Replace with `engine/include/**` public headers. | Protects internal engine modules. |
| ARCH-INC-003 | Public headers MUST live in `engine/include/**` only. | Include path allowlist scan | Build | CI fail: ARCH-INC-003 | Move or re-export headers via `engine/include/**`. | Prevents accidental API exposure. |
| ARCH-RENDER-001 | Renderer-specific code outside `engine/render/**` is FORBIDDEN. | Path-based static scan (tools/ci/arch_checks.py) | Configure | CI fail: ARCH-RENDER-001 | Move code into `engine/render/**` and expose public API. | Centralizes renderer ownership. |
| ARCH-REN-002 | `game/` MUST NOT branch on graphics APIs. | Static scan for backend tokens | Configure | CI fail: ARCH-REN-002 | Move backend choice to engine render layer. | Keeps game logic renderer-agnostic. |
| ARCH-REN-003 | `client/` MUST NOT own renderer backends. | Target graph + path scan | Configure | CI fail: ARCH-REN-003 | Relocate backend code to `engine/render/**`. | Prevents client-only renderer forks. |
| ARCH-SETUP-001 | `launcher/` or `setup/` depending on engine internals is FORBIDDEN. | Target graph rule in CMake | Configure | CI fail: ARCH-SETUP-001 | Remove the dependency and use `libs/` or `schema/`. | Avoids coupling operational tools to runtime. |
| DET-FLOAT-001 | Floating point usage in authoritative zones is FORBIDDEN (prelude). | Static scan (tools/ci/arch_checks.py, warn-only unless strict) | Configure | CI warn: DET-FLOAT-001 | Replace with deterministic fixed-point or approved math. | Prevents nondeterministic math. |
| DET-FLOAT-003 | Floating point usage in authoritative zones is FORBIDDEN (strict). | Static scan | Configure | CI fail: DET-FLOAT-003 | Replace with deterministic fixed-point or approved math. | Prevents nondeterministic math. |
| DET-TIME-001 | OS time APIs in authoritative zones are FORBIDDEN. | Static scan | Configure | CI fail: DET-TIME-001 | Use deterministic time sources from engine core. | Eliminates wall-clock variance. |
| DET-RNG-002 | Non-deterministic RNG in authoritative zones is FORBIDDEN. | Static scan | Configure | CI fail: DET-RNG-002 | Use engine deterministic RNG only. | Ensures replayable randomness. |
| DET-ORD-004 | Unordered container iteration without normalization is FORBIDDEN. | Lint + static scan | Configure | CI fail: DET-ORD-004 | Normalize ordering or use ordered containers. | Removes hash-order variance. |
| DET-THREAD-005 | Nondeterministic shared mutable state is FORBIDDEN. | Threading lint + race-focused tests | Test | CI fail: DET-THREAD-005 | Add deterministic scheduling or remove shared writes. | Prevents race-driven divergence. |
| DET-GATE-STEP-001 | Step vs batch equivalence MUST hold. | Determinism test suite | Test | CI fail: DET-GATE-STEP-001 | Fix update order or accumulation errors. | Ensures execution-mode equivalence. |
| DET-GATE-REPLAY-002 | Replay equivalence MUST hold. | Replay determinism suite | Test | CI fail: DET-GATE-REPLAY-002 | Remove nondeterministic inputs or ordering. | Protects replay and auditability. |
| DET-GATE-LOCKSTEP-003 | Lockstep vs server-auth equivalence MUST hold. | Network determinism suite | Test | CI fail: DET-GATE-LOCKSTEP-003 | Align authoritative rules and client prediction. | Maintains network determinism. |
| DET-GATE-HASH-004 | Hash partition invariance MUST hold. | Shard invariance suite | Test | CI fail: DET-GATE-HASH-004 | Normalize partition ordering and hash inputs. | Preserves sharding correctness. |
| DET-EXC-006 | Determinism exceptions are FORBIDDEN. | Policy scan for exception tags | Configure | CI fail: DET-EXC-006 | Remove the exception and fix root determinism issue. | Prevents erosion of determinism law. |
| PERF-GLOBAL-002 | Global iteration in runtime update paths is FORBIDDEN. | Lint + fixture test | Test | CI fail: PERF-GLOBAL-002 | Convert to event-driven, interest-set bounded processing. | Avoids O(N) frame scaling. |
| PERF-MODAL-001 | Blocking IO on render/UI threads is FORBIDDEN. | Runtime trace + watchdog | Test | CI fail: PERF-MODAL-001 | Move IO to background jobs and stream results. | Prevents hitches and stalls. |
| PERF-SHADER-002 | Shader compilation on demand is FORBIDDEN. | Runtime trace + build audit | Test | CI fail: PERF-SHADER-002 | Precompile shaders or compile during preload. | Avoids runtime shader stalls. |
| PERF-ASSET-003 | Synchronous asset decode on render/UI threads is FORBIDDEN. | Runtime trace | Test | CI fail: PERF-ASSET-003 | Decode asynchronously and cache results. | Keeps UI smooth under load. |
| PERF-STALL-004 | Stall watchdog thresholds MUST NOT be exceeded. | Perf regression test | Test | CI fail: PERF-STALL-004 | Reduce stalls or move work off render/UI threads. | Enforces predictable frame budgets. |
| PERF-FID-005 | Forbidden fidelity degradation is FORBIDDEN. | Scenario tests + invariants | Test | CI fail: PERF-FID-005 | Use only approved degradation mechanisms. | Protects authoritative state integrity. |
| UI-BYPASS-001 | UI code reading authoritative world state is FORBIDDEN. | Static scan (tools/ci/arch_checks.py) + unit test | Test | CI fail: UI-BYPASS-001 | Route UI through authorized projection layers. | Preserves epistemic separation. |
| BUILD-GLOBAL-001 | `include_directories()` or `link_directories()` usage is FORBIDDEN. | CMake lint (tools/ci/arch_checks.py) | Configure | CI fail: BUILD-GLOBAL-001 | Use target-scoped include/link directories only. | Prevents global include leakage. |
