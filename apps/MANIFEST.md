# Apps Manifest

Status: PROVISIONAL
Phase: CONVERGE-08

CONVERGE-08 moved product entrypoint roots under `apps/` and preserved product target names, executable output names, product IDs, install IDs, pack IDs, virtual-root IDs, and command behavior.

| Previous Root | New Location | Action | Notes |
| --- | --- | --- | --- |
| `client/` | `apps/client/` | moved | Client product entrypoint root moved intact. Mixed UI/render/runtime-local material remains product-local for now and is marked for later review rather than split in this phase. |
| `server/` | `apps/server/` | moved | Server product entrypoint root moved intact. Authority semantics and executable naming were not changed. |
| `setup/` | `apps/setup/` | moved | Setup product entrypoint root moved intact. Setup/install identity and package behavior were not changed. |
| `launcher/` | `apps/launcher/` | moved | Launcher product entrypoint root moved intact. Launcher identity, command behavior, and executable naming were not changed. |
| `tools/` | `tools/` | retained | Developer tools remain canonical under `tools/`; no wholesale move to `apps/tools/` occurred. |

Current app subdirectories:

- `apps/client/`
- `apps/server/`
- `apps/setup/`
- `apps/launcher/`

No conflicts required provenance subdirectories. No domain roots, runtime roots, contract roots, content roots, archive roots, or generated-output roots were moved. This manifest does not claim a semantic audit of all product behavior; it records the product-root convergence and path-reference repairs performed in CONVERGE-08.
