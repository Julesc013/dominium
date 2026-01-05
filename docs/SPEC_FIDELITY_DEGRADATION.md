# SPEC_FIDELITY_DEGRADATION — Derived Fidelity Ladder

## Scope
This spec defines how UI/render fidelity degrades when derived data is missing
or late. It applies to display-only behavior and MUST NOT affect simulation.

## Rules (mandatory)
- Fidelity changes MUST NOT mutate authoritative state.
- Missing derived data MUST lower fidelity rather than stall execution.
- The UI MUST render something at every fidelity level.
- Fidelity increases opportunistically when required derived data is ready.
- Fidelity changes MUST be independent of determinism hashes.

## Level guidance
Implementations SHOULD provide at least:
- **Low:** minimal UI and safe placeholders; no dependence on derived caches.
- **Medium:** partial overlays or debug layers that tolerate missing data.
- **High:** full visual overlays and derived cache usage.

These levels are derived-only and may vary per renderer, but MUST obey the
rules above.

## Related specs
- `docs/SPEC_NO_MODAL_LOADING.md`
- `docs/SPEC_STREAMING_BUDGETS.md`
