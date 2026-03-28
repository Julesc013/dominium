Status: DERIVED
Last Reviewed: 2026-03-28
Stability: provisional
Future Series: XI
Replacement Target: XI-5a-v3 dangerous shadow-root execution logs

# XI-4z Shadow-Root Resolution Report

## Scope Decision

- Xi-5a-v3 is narrowed to dangerous shadow roots only: `src/` and `app/src/`.
- Legacy `source/` pockets, component-local `src/`, and content-source roots are deferred to later Xi-5 phases.
- Reserved package collisions inherited from Xi-4z-fix2 remain protected: `platform, time`.

## Counts

- approved_for_xi5 v3: `769`
- approved_for_xi5 v4: `542`
- approved_to_attic v3: `23`
- approved_to_attic v4: `0`
- deferred_to_xi5b v3: `3`
- deferred_to_xi5b v4: `253`

## Promoted Package Initializers

- `src/client/interaction/__init__.py`
- `src/lib/store/__init__.py`

## Deferred Follow-On Phase Counts

- `component_local_src`: `48`
- `content_source_root`: `13`
- `dangerous_shadow_root`: `1`
- `later_phase`: `5`
- `legacy_source_pocket`: `186`

## Conclusion

- Xi-5a-v3 can now execute the dangerous shadow-root slice mechanically from the v4 lock without re-deciding target paths.
- Xi-5b/Xi-5c remain responsible for the deferred legacy, content-source, and component-local source pockets.
