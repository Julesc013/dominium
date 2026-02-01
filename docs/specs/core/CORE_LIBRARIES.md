Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Core Libraries (Shared)

This document lists the shared contract modules under
`libs/contracts/include/dom_contracts` that are used by launcher and setup.

## Modules

- `core_tlv`: framed TLV reader/writer + canonical encoding helpers.
- `core_tlv_schema`: schema registry, version gates, and migration hooks.
- `core_err`: stable `err_t` model, flags, and msg_id catalog.
- `core_log`: structured event logging with deterministic TLV sink.
- `core_job`: resumable job model + TLV journaling.
- `core_caps`: typed capability entries + deterministic merge/compare helpers.
- `core_solver`: deterministic constraint solver + explainable selection output.
- `core_audit`: deterministic audit helpers (err detail encoding).
- `core_installed_state`: installed_state.tlv parse/write helpers (setup -> launcher).
- `provider_api`: C ABI provider vtables (content/trust/keychain/net/os integration).

## Invariants

- No OS/UI headers in core contract headers.
- Deterministic output: stable ordering and canonical encoding.
- C89-compatible ABIs at module boundaries; launcher/setup code uses C++98 only.
- Skip-unknown TLV semantics for forward compatibility.

## Extending Safely

- Add new core headers under `libs/contracts/include/dom_contracts/`.
- Register new schemas through `core_tlv_schema` with deterministic validators.
- Update `libs/contracts/CMakeLists.txt` and link the new contract header into
  launcher/setup/tool targets as needed.
- Keep error IDs append-only; never renumber msg_id or schema IDs.