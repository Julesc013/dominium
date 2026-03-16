Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Change:
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

LIB-2 deterministic instance manifests, instance kinds, save associations, and portable/linked import-export flows

Touched Paths:
- src/lib/instance/instance_validator.py
- tools/ops/ops_cli.py
- tools/launcher/launcher_cli.py
- tools/share/share_cli.py
- tools/setup/setup_cli.py

Demand IDs:
- cyber.firmware_flashing_pipeline_integration

Notes:
- Instance manifests now bind pack locks, profile bundles, instance kinds, and save associations explicitly so launcher/setup/share flows can validate runtime selection without path-based assumptions.
- Saves are no longer treated as instance-owned payloads; clone/export/import preserve `save_refs` only.
- Portable instance export/import can round-trip embedded artifacts and optional embedded builds while linked import re-materializes reusable artifacts into the shared store.
