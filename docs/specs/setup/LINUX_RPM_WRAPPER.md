# Linux RPM Wrapper (SR-7)

The RPM wrapper is minimal. It does not run install logic in maintainer scripts.

## Scripts
- `postinst.sh`: calls `dominium-setup status` and `verify` against pkg-owned state.
- `prerm.sh`: removes setup state artifacts on uninstall.

## Default Paths
- `installed_state.tlv`: `/var/lib/dominium/installed_state.tlv`
- `job_journal.tlv`: `/var/lib/dominium/job_journal.tlv`

## Ownership
- Core runtime files are pkg-owned.
- Packs/mods or user data remain kernel-owned under explicit roots.

## Example (mock)
```
dominium-setup status --journal /var/lib/dominium/job_journal.tlv
dominium-setup verify --state /var/lib/dominium/installed_state.tlv --format txt
```
