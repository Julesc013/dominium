# Offline Install (SHIP-1)

Status: binding.
Scope: offline-first setup behavior.

## Rules

- Setup works fully offline.
- Network is optional and additive.
- Missing network produces an explicit notice and continues offline.
- Pack references that are unavailable do not block install.

## Network mode

Setup accepts:

- `--network-mode offline` — force offline behavior.
- `--network-mode online` — request network; if unavailable, continue offline.
- `--network-mode auto` — default behavior (attempt network if available).

Setup never hides network failures; they are reported in structured output.

## References

- `docs/distribution/SETUP_GUARANTEES.md`
- `docs/architecture/SETUP_TRANSACTION_MODEL.md`
