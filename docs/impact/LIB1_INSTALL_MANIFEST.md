Change:
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

LIB-1 deterministic install manifests, build selection, and multi-install registration

Touched Paths:
- src/appshell/bootstrap.py
- src/appshell/config_loader.py
- src/lib/install/install_validator.py
- tools/launcher/launcher_cli.py
- tools/ops/ops_cli.py
- tools/setup/setup_cli.py

Demand IDs:
- cyber.firmware_flashing_pipeline_integration

Notes:
- Install manifests make product build selection, protocol support, and contract registry checks explicit so setup, launcher, and tool entrypoints can verify binaries without path-dependent assumptions.
- The AppShell fallback and repo-root resolution changes keep portable and linked installs deterministic across direct tool invocation paths instead of depending on caller working-directory state.
