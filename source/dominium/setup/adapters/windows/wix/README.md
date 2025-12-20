# Windows MSI (WiX) Template (Plan S-6)

This directory contains a **design-only** WiX template showing how to invoke Setup Core through `dominium-setup-win`.

Key mapping:

- `CA_DSU_INSTALL`: `dominium-setup-win install --plan <plan>`
- `CA_DSU_REGISTER`: `dominium-setup-win platform-register --state <state>`
- `CA_DSU_UNREGISTER`: `dominium-setup-win platform-unregister --state <state>`
- `CA_DSU_UNINSTALL`: `dominium-setup-win uninstall --state <state>`

The packaging pipeline is responsible for:

- generating the `.dsuplan` file (via Setup Core resolve/plan build)
- embedding the adapter executable and payloads
- choosing per-user vs per-machine and handling elevation

