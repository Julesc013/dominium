# Archive Manifest

Status: PROVISIONAL
Phase: CONVERGE-05
Date: 2026-05-12

CONVERGE-05 completed the archive-family root convergence. Root-level `attic/`, `legacy/`, and `quarantine/` material was retained and moved under the canonical `archive/` root. No non-archive source roots were moved.

| Previous Root | New Location | Action | Notes |
| --- | --- | --- | --- |
| `attic/` | `archive/historical/attic/` | moved | Historical quarantine material retained with its original substructure. |
| `legacy/` | `archive/legacy/` | moved | Legacy material retained with its original substructure. |
| `quarantine/` | `archive/quarantine/` | moved | Quarantined material retained and kept visibly quarantined. |

Current archive class directories:

- `archive/historical/`
- `archive/legacy/`
- `archive/quarantine/`
- `archive/superseded/`
- `archive/generated/`

Conflicts encountered: none.

Files intentionally not moved:

- Existing `archive/__init__.py` and `archive/deterministic_bundle.py` were preserved in place.

References updated:

- `contracts/repo/layout.contract.toml`
- `contracts/repo/root_allowlist.toml`
- `tools/validators/check_repo_layout.py`
- `tools/validators/check_root_allowlist.py`
- `tools/migration/root_inventory.json`
- `tools/migration/root_move_map.json`
- `docs/repo/ROOT_INVENTORY.md`
- `docs/repo/MOVE_MAP.md`
- `docs/repo/REPO_LAYOUT_TARGET.md`
- `docs/repo/OWNERSHIP_RULES.md`
- `docs/repo/ROOT_FILE_POLICY.md`
- `docs/repo/audits/CONVERGE_00_BASELINE.md`

This manifest records the root convergence only. It does not claim every archived file has been semantically audited.
