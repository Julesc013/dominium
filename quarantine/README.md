# Quarantine Directory

This directory holds migration-isolated legacy code/data that must not be linked into production runtime targets.

Rules:
- Production runtime modules must not import from `quarantine/`.
- Any temporary access must go through an adapter explicitly listed in `data/governance/deprecations.json`.
- Quarantine content is transitional and should be removed once migration is complete.

