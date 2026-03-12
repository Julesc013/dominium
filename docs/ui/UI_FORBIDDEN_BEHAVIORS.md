Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# UI Forbidden Behaviors

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.






The UI MUST NOT:


- Mutate simulation state or bypass authority checks.


- Access objective snapshots by default.


- Infer or reveal hidden truth.


- Auto-correct player intent or inject actions directly.


- Provide GUI-only or TUI-only features not present in the CLI.


- Hide failures, refusal reasons, or error codes.


- Expose gameplay difficulty or simulation rule toggles in Settings.


- Use assets, textures, images, external fonts, or content packs in baseline UI.





Any UI implementation violating the above is non-canonical.





## References


- docs/ui/UI_PHILOSOPHY.md


- docs/architecture/INVARIANTS.md
