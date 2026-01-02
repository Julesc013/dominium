# Linux DEB Wrapper (SR-7)

The DEB wrapper is minimal. It does not run install logic in maintainer scripts.

## Scripts
- `postinst.sh`: calls `dominium-setup2 status` and `verify` against pkg-owned state.
- `prerm.sh`: removes setup2 state artifacts on uninstall.

## Default Paths
- `installed_state.tlv`: `/var/lib/dominium/installed_state.tlv`
- `job_journal.tlv`: `/var/lib/dominium/job_journal.tlv`

## Ownership
- Core runtime files are pkg-owned.
- Packs/mods or user data remain kernel-owned under explicit roots.

## Example (mock)
```
dominium-setup2 status --journal /var/lib/dominium/job_journal.tlv
dominium-setup2 verify --state /var/lib/dominium/installed_state.tlv --format txt
```
