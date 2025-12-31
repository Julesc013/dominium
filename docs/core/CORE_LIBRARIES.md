# Core Libraries (Shared)

This document lists the shared core libraries under `source/dominium/common` that
are used by both launcher and setup kernels.

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

- No OS/UI headers in core libraries.
- Deterministic output: stable ordering and canonical encoding.
- C89-compatible ABIs at module boundaries; launcher/setup code uses C++98 only.
- Skip-unknown TLV semantics for forward compatibility.

## Extending Safely

- Add new core headers under `include/dominium/` and sources under
  `source/dominium/common/`.
- Register new schemas through `core_tlv_schema` with deterministic validators.
- Update `source/dominium/common/CMakeLists.txt` and link the new core lib into
  `launcher_kernel` and `setup_kernel`.
- Keep error IDs append-only; never renumber msg_id or schema IDs.
