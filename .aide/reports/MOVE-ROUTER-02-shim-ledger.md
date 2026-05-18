Status: DERIVED
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-02

# MOVE-ROUTER-02 Shim Ledger

Three temporary runtime control shim packages were created:

- `runtime/control/__init__.py`
- `runtime/control/effects/__init__.py`
- `runtime/control/fidelity/__init__.py`

They are repair shims only. They re-export routed governance/control surfaces and
must be retired or narrowed by `MOVE-ROUTER-02R`; new code must not bind to the
old `control/` root.
