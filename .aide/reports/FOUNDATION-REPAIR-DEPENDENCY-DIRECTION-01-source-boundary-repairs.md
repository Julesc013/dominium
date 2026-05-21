Status: DERIVED
Last Reviewed: 2026-05-21
Task: FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01

# Source Boundary Repairs

Implemented repairs:

- Removed `engine -> game` edges in `engine/foundation/meta/compile/compile_engine.py`.
- Removed game-domain reference evaluator files from `engine/foundation/meta/reference/**`.
- Replaced `runtime -> tools.release.build_id_engine` with `runtime/package/build_id_engine.py`.
- Removed `runtime -> tools.validators.stability` by keeping the shim stability marker helper runtime-owned.
- Removed `runtime/compatibility/shims/validation_shims.py`; validation shims remain tools-owned.

The final dependency-direction strict validator passes.
