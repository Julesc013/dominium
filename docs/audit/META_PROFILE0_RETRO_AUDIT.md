# META-PROFILE-0 Retro-Consistency Audit

Status: DERIVED  
Date: 2026-03-07  
Series: META-PROFILE-0

## Scope
This audit covers runtime/profile override touchpoints and mode-flag risks before implementing unified profile overrides.

Binding references:
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`

## Existing Mode-Flag / Bypass Findings

1. Existing hard gate present:
- `tools/xstack/repox/check.py` already enforces `INV-NO-MODE-FLAGS`.

2. Legacy runtime-style toggle found:
- `src/system/system_collapse_engine.py` used `state["debug_profile"]` via `_statevec_debug_guard_enabled(...)`.
- This is a profile-fragment toggle that must migrate to unified profile resolution.

3. Existing exception pathways are present but fragmented:
- Physics/session runtime already emits `exception.meta_law_override` style events.
- No unified profile-specific exception schema/engine existed.

## Override Points Cataloged

### PHYS invariants
- `src/reality/ledger/ledger_engine.py`
- Existing behavior supports exception guidance but did not route through unified profile binding.

### Process capsules
- `src/process/capsules/capsule_executor.py`
- Validity-domain and invalidation behavior exists; no unified profile resolution layer yet.

### Collapse/expand
- `src/system/system_collapse_engine.py`
- Direct debug-profile guard found (migrate to resolved profile rule).

### Logic compilation
- `src/meta/compile/compile_engine.py`
- Compilation contracts exist; no dedicated profile override surface.

### Coupling scheduler
- No `src/meta/coupling/*` runtime engine currently present; coupling discipline enforced primarily via registries/rules/reference checks.

### Instrumentation access
- `src/meta/instrumentation/instrumentation_engine.py`
- Access control policy exists; no unified cross-profile resolver yet.

## Proposed Migration Actions

1. Introduce unified profile artifacts:
- `profile`
- `profile_binding`
- `profile exception event`

2. Introduce deterministic runtime resolver:
- Universe -> Session -> Authority -> System overlay order.

3. Replace direct mode-like state toggles with resolved rule checks.

4. Require canonical exception event emission when effective behavior is overridden beyond baseline.

5. Extend SessionSpec/AuthorityContext contracts to carry explicit profile bindings/effective snapshots.

## Risks

- Existing runtime callsites may still use local override variables (`*_override`, `debug_profile`) and require progressive migration.
- Profile registry overlap with existing fragmented registries must remain backward-compatible.

## Audit Conclusion
The repository is ready for META-PROFILE-0 with incremental migration:
- Existing profile primitives are sufficient.
- Mode-flag enforcement exists and can be extended.
- Missing piece is unified resolver + canonical exception ledger contract.
