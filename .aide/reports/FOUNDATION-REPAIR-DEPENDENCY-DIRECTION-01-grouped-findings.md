Status: DERIVED
Last Reviewed: 2026-05-21
Task: FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01

# Grouped Findings

Baseline from `FOUNDATION-CLOSEOUT-01`: `358` dependency-direction violations and `38` warnings.

Tracked-helper rescan during this repair exposed `9` additional real violations after newly added helper files became tracked. Those were repaired before final validation.

Final strict result: `PASS`, `0` violations, `68` warnings, `16579` files scanned.

## Groups

| Group | Classification | Result |
| --- | --- | --- |
| Original active product/runtime imports into tools | `fixed_import_include_direction` | Fixed or narrowed to exact transitional exceptions |
| Engine helper imports into game | `fixed_real_violation` | Fixed by removing game-specific reference helpers from engine and making compile state-vector support substrate-owned |
| Runtime compatibility imports into tools | `fixed_real_violation` | Fixed by runtime-owned build-id helper, inline stability marker helper, and removing the runtime validation shim copy |
| Transitional app/runtime tool adapter edges | `accepted_transitional_exception` | `12` exact exception entries, `28` applied edges, retire by `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-02` |
| Remaining unlisted active dependencies | `followup_required_explicit` | Warning-only review debt; not a strict blocker |
