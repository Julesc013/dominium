Status: DERIVED
Last Reviewed: 2026-03-30
Stability: stable
Future Series: XI-8
Replacement Target: later shim removal execution once REPO-LAYOUT-1 bridges are provably unused

# Shim Sunset Plan

Xi-8 does not remove shims automatically. The REPO-LAYOUT-1 shims remain in place until removal is proven safe.

- shim count: `11`
- shared sunset target: `remove after v0.0.1 or after directory restructure convergence`

Removal requires all of the following:

- no references in build graph
- no references in symbol index
- all docs updated
- Ω suite passes without shims

| Category | Shim ID | Legacy Surface | Forwards To | Milestone | Build Graph Ref | Symbol Index Ref |
| --- | --- | --- | --- | --- | --- | --- |
| `flag` | `shim.flag.legacy_client_ui` | `--ui gui|cli` | `--mode rendered|cli rendered|cli` | `v0.1.0` | `not proven` | `yes` |
| `flag` | `shim.flag.legacy_no_gui` | `--no-gui` | `--mode tui|cli` | `v0.1.0` | `not proven` | `yes` |
| `flag` | `shim.flag.legacy_portable` | `--portable` | `--install-root <portable adjacency root>` | `v0.1.0` | `not proven` | `yes` |
| `flag` | `shim.flag.legacy_server_ui` | `--ui headless|cli` | `--mode headless|cli headless|cli` | `v0.1.0` | `not proven` | `yes` |
| `path` | `shim.path.legacy_data_root` | `./data | data` | `VROOT_STORE/data` | `v0.1.0` | `not proven` | `yes` |
| `path` | `shim.path.legacy_packs_root` | `../packs | ./packs | packs | data/packs | ./data/packs` | `VROOT_PACKS` | `v0.1.0` | `not proven` | `yes` |
| `path` | `shim.path.legacy_profiles_root` | `./profiles | profiles | data/profiles | ./data/profiles` | `VROOT_PROFILES` | `v0.1.0` | `not proven` | `yes` |
| `path` | `shim.path.legacy_store_children` | `./locks | ./instances | ./saves | ./exports | ./logs | ./runtime` | `governed store vroots` | `v0.1.0` | `not proven` | `yes` |
| `tool` | `shim.tool.pack_migrate_capability_gating` | `tools/pack/migrate_capability_gating.py` | `dom pack migrate-capability-gating` | `v0.1.0` | `not proven` | `yes` |
| `tool` | `shim.tool.pack_validate` | `tools/pack/pack_validate.py` | `dom pack validate-manifest` | `v0.1.0` | `not proven` | `yes` |
| `validation` | `shim.validation.validate_all_py` | `tools/ci/validate_all.py` | `validate --all --profile FAST|STRICT|FULL` | `v0.1.0` | `not proven` | `yes` |

Current Xi-8 action: retain all shims. No shim was removed in this freeze pass.
