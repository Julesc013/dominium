Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# STATUS_SR2

SR-2 adds:
- Layer 1 runtime services (real + fake) with stable vtable contracts.
- Kernel now accepts services and uses platform facts for SPLAT selection.
- dominium-setup uses services for IO and supports `--use-fake-services`.
- Build-time kernel purity checks (sentinel + script) and new service/kernel tests.

Still stubbed:
- No job engine or transactional execution.
- Process, perms, registry/pkgmgr/codesign remain placeholders.
- Archive validation/extraction is minimal and deterministic only.