Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-26
Scope: RS-2/5 conservation contracts + deterministic exception ledger.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Conservation Ledger Baseline

## Quantities Tracked

1. `quantity.mass_energy_total`
2. `quantity.mass`
3. `quantity.energy`
4. `quantity.charge_total`
5. `quantity.ledger_balance`
6. `quantity.entropy_metric`

All quantity accounting is per-tick, per-shard, deterministic, and fixed-point.

## Contract Sets Available

1. `contracts.null`
2. `contracts.default.realistic`
3. `contracts.magic_relaxed`

Contract modes supported:

1. `enforce_strict`
2. `enforce_local`
3. `allow_with_ledger`
4. `track_only`
5. `ignore`

## Exception Types

1. `exception.boundary_flux`
2. `exception.field_exchange`
3. `exception.creation_annihilation`
4. `exception.coordinate_gauge`
5. `exception.numeric_error_budget`
6. `exception.meta_law_override`

Exception entry attribution fields are deterministic and include: tick, shard, domain, process, quantity, delta, reason, and fingerprint.

## Enforcement Behavior

1. Default realistic profile:
   - uses `contracts.default.realistic`
   - strict mass-energy and charge enforcement
   - refuses unaccounted deltas with `refusal.conservation_violation.<quantity_id>`
2. Null profile:
   - uses `contracts.null`
   - no strict refusal for ignored channels
   - still supports deterministic ledger finalization and hash chaining
3. Relaxed/magic profile:
   - uses `allow_with_ledger` for `quantity.mass_energy_total`
   - allows violations only when explicitly logged
   - unlogged deltas refuse with `refusal.conservation_unaccounted`

## Multiplayer and Proof Integration

1. `ledger_hash` is included in SRZ per-tick hash inputs.
2. Authoritative and hybrid runtimes persist per-tick conservation ledgers.
3. Hash-anchor frames carry `ledger_hash`.
4. Ranked anti-cheat proof export includes `conservation_ledgers`.
5. Handshake compatibility includes conservation contract set matching via `refusal.conservation_contract_set_mismatch`.

## Guardrails and Smell Detection

1. RepoX invariants:
   - `INV-CONSERVATION-CONTRACT-SET-REQUIRED`
   - `INV-NO-SILENT-VIOLATIONS`
2. AuditX analyzers:
   - `E42_UNACCOUNTED_VIOLATION_SMELL`
   - `E43_EXCESSIVE_NUMERIC_LOSS_SMELL`

## Test Coverage

1. `test_null_contract_set_allows_anything`
2. `test_realistic_strict_refuses_unaccounted_creation`
3. `test_allow_with_ledger_allows_violation_but_logs`
4. `test_ledger_hash_deterministic`
5. `test_mp_hash_includes_ledger`

## Gate Execution (2026-02-26)

1. RepoX:
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: PASS (`findings=0`)
2. AuditX:
   - command: `py -3 tools/auditx/auditx.py scan --repo-root . --format json`
   - result: COMPLETE (`findings_count=959`, scan-only, non-gating)
3. TestX (RS-2 suite):
   - command: `py -3 tools/xstack/testx_all.py --repo-root . --profile STRICT --cache off --subset testx.reality.test_null_contract_set_allows_anything,testx.reality.test_realistic_strict_refuses_unaccounted_creation,testx.reality.test_allow_with_ledger_allows_violation_but_logs,testx.reality.test_ledger_hash_deterministic,testx.reality.test_mp_hash_includes_ledger`
   - result: PASS (`selected_tests=5`)
4. strict build:
   - configure: `C:\Program Files\CMake\bin\cmake.exe -S . -B out/build/vs2026/verify -G "Visual Studio 17 2022" -A x64`
   - build: `C:\Program Files\CMake\bin\cmake.exe --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
   - result: PASS
5. ui bind:
   - pre-step: `py -3 tools/xstack/registry_compile/registry_compile.py --repo-root . --out-dir build/registries --lockfile-out build/lockfile.json`
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: PASS (`checked_windows=21`)

## Extension Points

1. Thermodynamics channels and budgets can be layered as additional quantities and contract sets.
2. Chemistry/reaction accounting can emit deterministic exception entries without replacing core ledger semantics.
3. RS-4 collapse/expand accounting can reuse the same per-shard chain and proof export path.
