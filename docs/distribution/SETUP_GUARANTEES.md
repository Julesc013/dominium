# Setup Guarantees (SHIP-1)

Status: binding.
Scope: offline-first setup guarantees across install, repair, rollback, and uninstall.

## Core guarantees

- Setup NEVER assumes content packs exist.
- Setup NEVER mutates an existing install silently.
- Setup NEVER leaves partial state after failure.
- Setup ALWAYS explains outcomes clearly.
- Setup ALWAYS logs actions deterministically.

## Transactional guarantees

- All setup actions are PLAN → STAGE → COMMIT or ROLLBACK.
- Any failure triggers ROLLBACK.
- Logs are emitted for every stage.

## Offline-first guarantees

- Setup works fully offline.
- Network access is optional and additive.
- Missing network produces an explicit notice and continues offline.

## Distribution guarantees

- Minimal distribution: binaries only, zero packs, zero assets.
- Maximal distribution: binaries plus bundled packs.
- Setup treats bundled content as already present; no special code paths.

## References

- `docs/architecture/SETUP_TRANSACTION_MODEL.md`
- `docs/distribution/LAUNCHER_SETUP_CONTRACT.md`
- `docs/architecture/PRODUCT_SHELL_CONTRACT.md`
