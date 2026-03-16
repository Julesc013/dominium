Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: LIB/APPSHELL
Replacement Target: release-pinned install discovery and installation governance contract

# Install Discovery Baseline

Fingerprint: `4afc477d3fbc0075b54b944e98a34c12956327d2876630476e14baa544e4d489`

## Discovery Order

- 1. explicit CLI: --install-root or --install-id
- 2. portable adjacency: <exe_dir>/install.manifest.json
- 3. environment override: DOMINIUM_INSTALL_ROOT or DOMINIUM_INSTALL_ID
- 4. installed registry: install_registry.json from user config or platform default location
- 5. refusal: refusal.install.not_found

## Refusal Codes

- `refusal.install.not_found`

## Sample Outcomes

| Case | Result | Mode | Resolution Source | Install Id | Refusal Code |
| --- | --- | --- | --- | --- | --- |
| `explicit` | `complete` | `explicit` | `cli_install_root` | `install.explicit` | `` |
| `installed` | `complete` | `installed` | `installed_registry_single` | `install.registered` | `` |
| `portable` | `complete` | `portable` | `portable_manifest` | `install.portable` | `` |
| `refused` | `refused` | `` | `` | `` | `refusal.install.not_found` |

## Integration Coverage

| Surface | File | Status | Markers |
| --- | --- | --- | --- |
| `install_discovery_engine` | `src/lib/install/install_discovery_engine.py` | `integrated` | `3/3` |
| `virtual_paths` | `src/appshell/paths/virtual_paths.py` | `integrated` | `3/3` |
| `appshell_bootstrap` | `src/appshell/bootstrap.py` | `integrated` | `3/3` |
| `compat_status` | `src/appshell/commands/command_engine.py` | `integrated` | `1/1` |
| `setup_install_commands` | `tools/setup/setup_cli.py` | `integrated` | `3/3` |
| `launcher_install_commands` | `tools/launcher/launch.py` | `integrated` | `3/3` |

## Manifest Discipline

- manifest absolute-path violations: `0`
- integration remaining count: `0`

## Integration Coverage Report

- AppShell boot now resolves install selection through the LIB discovery engine before virtual roots are derived.
- `compat-status`, `setup install status`, and `launcher install status` expose the resolved install decision or refusal details.
- Repo wrapper fallback remains outside the authoritative discovery order and is tracked in the virtual-path shim surface, not the runtime install discovery contract.
