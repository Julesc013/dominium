Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Setup Handoff Snapshot

Branch: main (formerly setup-kernel-refactor)
Commit range: 03fc3eb22a0e9979e7e46ee344588749055979d0 .. 4ba4d8d697f52156ce6d36e9dea66717e98dc432

Kernel version: Setup Kernel v1 (dsk_* modules, TLV v1 schemas)

Schema versions (all v1):
- install_manifest.tlv
- install_request.tlv
- install_plan.tlv
- installed_state.tlv
- setup_audit.tlv
- job_journal.tlv
- txn_journal.tlv

Adapters considered complete:
- CLI (dominium-setup)
- TUI (dominium-setup-tui)
- Windows EXE adapter
- Windows MSI wrapper
- macOS PKG wrapper
- Linux deb wrapper
- Linux rpm wrapper
- Steam provider adapter

Known limitations (documented):
- Job DAG parallelism deferred (docs/setup/FUTURE_BACKLOG.md)
- Signed manifest verification deferred (docs/setup/FUTURE_BACKLOG.md)
- Stronger cryptographic digests deferred (docs/setup/FUTURE_BACKLOG.md)
- MSIX/Flatpak/AppImage wrappers deferred (docs/setup/FUTURE_BACKLOG.md)
- Advanced Steam verify/repair mapping deferred (docs/setup/FUTURE_BACKLOG.md)

Gold master artifacts:
- artifacts/setup/gold_master/

How to reproduce:
- Build: scripts/ci/setup_build.bat or scripts/ci/setup_build.sh
- Conformance: scripts/setup/run_conformance.bat or scripts/setup/run_conformance.sh
- Release gate: scripts/release/run_setup_release_gate.bat or scripts/release/run_setup_release_gate.sh