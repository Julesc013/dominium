Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Domain Documentation Root

Status: PROVISIONAL
Phase: CONVERGE-09

`docs/domains/` is the target human-readable documentation surface for domain explanations, models, design notes, and migration reports.

Machine-readable domain contracts belong under `contracts/`. Domain implementation belongs under `game/domain/`. Domain content and datasets belong under `content/domains/` or `content/packs/`. Test fixtures, determinism cases, regression inputs, and golden cases belong under `tests/`.

Existing domain docs may remain in older `docs/<domain>/` surfaces until CONVERGE-12 cross-reference cleanup. Those older locations do not authorize new root-level domain source folders.
