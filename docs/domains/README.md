# Domain Documentation Root

Status: PROVISIONAL
Phase: CONVERGE-09

`docs/domains/` is the target human-readable documentation surface for domain explanations, models, design notes, and migration reports.

Machine-readable domain contracts belong under `contracts/`. Domain implementation belongs under `game/domains/`. Domain content and datasets belong under `content/domain-data/` or `content/packs/`. Test fixtures, determinism cases, regression inputs, and golden cases belong under `tests/`.

Existing domain docs may remain in older `docs/<domain>/` surfaces until CONVERGE-12 cross-reference cleanup. Those older locations do not authorize new root-level domain source folders.
