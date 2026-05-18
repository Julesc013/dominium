Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Domain Split Report

Status: PROVISIONAL
Phase: CONVERGE-09

This report explains the CONVERGE-09 root-level domain split. The machine-readable planning artifacts remain `tools/migration/root_inventory.json`, `tools/migration/root_move_map.json`, and `contracts/repo/layout.contract.toml`.

CONVERGE-09 inspected root-level domain packages and moved only clearly classified implementation source into `game/domain/<domain>/`. The inspected moved roots contained Python domain implementation only; no schema, registry, capability, protocol, content, docs, or tests subsets were found inside those roots during the safe split. No new simulation features were added.

| Root | Classification | Contract Target | Implementation Target | Content Target | Docs Target | Tests Target | Status | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `astro/` | implementation_code | `contracts/*/astronomy/` | `game/domain/astronomy/` | `content/domains/astronomy/` | `docs/domains/astronomy/` | `tests/*/astronomy/` | completed | medium | Root implementation moved. |
| `chem/` | implementation_code | `contracts/*/chemistry/` | `game/domain/chemistry/` | `content/domains/chemistry/` | `docs/domains/chemistry/` | `tests/*/chemistry/` | completed | medium | Root implementation moved. |
| `electric/` | implementation_code | `contracts/*/electricity/` | `game/domain/electricity/` | `content/domains/electricity/` | `docs/domains/electricity/` | `tests/*/electricity/` | completed | medium | Root implementation moved. |
| `field/` | implementation_code | `contracts/*/fields/` | `game/domain/fields/from_root_field/` | `content/domains/fields/` | `docs/domains/fields/` | `tests/*/fields/` | completed | high | Facade preserved separately under fields. |
| `fields/` | implementation_code | `contracts/*/fields/` | `game/domain/fields/` | `content/domains/fields/` | `docs/domains/fields/` | `tests/*/fields/` | completed | high | Canonical field implementation moved without collapsing facade semantics. |
| `fluid/` | implementation_code | `contracts/*/fluids/` | `game/domain/fluids/` | `content/domains/fluids/` | `docs/domains/fluids/` | `tests/*/fluids/` | completed | medium | Root implementation moved. |
| `geo/` | implementation_code | `contracts/*/geology/` | `game/domain/geology/` | `content/domains/geology/` | `docs/domains/geology/` | `tests/*/geology/` | completed | medium | Root implementation moved; view/projection code remains reviewable domain source. |
| `logic/` | implementation_code | `contracts/*/logic/` | `game/domain/logic/` | `content/domains/logic/` | `docs/domains/logic/` | `tests/*/logic/` | completed | medium | Root implementation moved. |
| `materials/` | implementation_code | `contracts/*/materials/` | `game/domain/materials/` | `content/domains/materials/` | `docs/domains/materials/` | `tests/*/materials/` | completed | medium | Root implementation moved. |
| `mechanics/` | implementation_code | `contracts/*/mechanics/` | `game/domain/mechanics/` | `content/domains/mechanics/` | `docs/domains/mechanics/` | `tests/*/mechanics/` | completed | medium | Root implementation moved. |
| `physics/` | implementation_code | `contracts/*/physics/` | `game/domain/physics/` | `content/domains/physics/` | `docs/domains/physics/` | `tests/*/physics/` | completed | medium | Root implementation moved. |
| `pollution/` | implementation_code | `contracts/*/pollution/` | `game/domain/pollution/` | `content/domains/pollution/` | `docs/domains/pollution/` | `tests/*/pollution/` | completed | medium | Root implementation moved. |
| `process/` | implementation_code | `contracts/*/processes/` | `game/domain/processes/` | `content/domains/processes/` | `docs/domains/processes/` | `tests/*/processes/` | completed | high | Domain process package moved; process-only mutation meaning unchanged. |
| `signals/` | implementation_code | `contracts/*/signals/` | `game/domain/signals/` | `content/domains/signals/` | `docs/domains/signals/` | `tests/*/signals/` | completed | medium | Root implementation moved. |
| `system/` | implementation_code | `contracts/*/systems/` | `game/domain/systems/` | `content/domains/systems/` | `docs/domains/systems/` | `tests/*/systems/` | completed | high | Simulation system package moved; runtime OS system roots remain separate. |
| `thermal/` | implementation_code | `contracts/*/thermal/` | `game/domain/thermal/` | `content/domains/thermal/` | `docs/domains/thermal/` | `tests/*/thermal/` | completed | medium | Root implementation moved. |
| `universe/` | implementation_code | `contracts/*/universe/` | `game/domain/universe/` | `content/domains/universe/` | `docs/domains/universe/` | `tests/*/universe/` | completed | medium | Root implementation moved. |
| `worldgen/` | implementation_code | `contracts/*/worldgen/` | `game/domain/worldgen/` | `content/domains/worldgen/` | `docs/domains/worldgen/` | `tests/*/worldgen/` | completed | high | Root implementation moved; no generation features added. |
| `mobility/` | implementation_code | `contracts/*/mobility/` | `game/domain/mobility/` | `content/domains/mobility/` | `docs/domains/mobility/` | `tests/*/mobility/` | completed | medium | Root implementation moved. |
| `logistics/` | implementation_code | `contracts/*/logistics/` | `game/domain/logistics/` | `content/domains/logistics/` | `docs/domains/logistics/` | `tests/*/logistics/` | completed | medium | Root implementation moved. |
| `diegetics/` | implementation_code | `contracts/*/diegetics/` | `game/domain/diegetics/` | `content/domains/diegetics/` | `docs/domains/diegetics/` | `tests/*/diegetics/` | completed | medium | Additional domain root moved. |
| `embodiment/` | implementation_code | `contracts/*/embodiment/` | `game/domain/embodiment/` | `content/domains/embodiment/` | `docs/domains/embodiment/` | `tests/*/embodiment/` | completed | medium | Additional domain root moved. |
| `epistemics/` | implementation_code | `contracts/*/epistemics/` | `game/domain/epistemics/` | `content/domains/epistemics/` | `docs/domains/epistemics/` | `tests/*/epistemics/` | completed | medium | Additional domain root moved. |
| `infrastructure/` | implementation_code | `contracts/*/infrastructure/` | `game/domain/infrastructure/` | `content/domains/infrastructure/` | `docs/domains/infrastructure/` | `tests/*/infrastructure/` | completed | medium | Additional domain root moved. |
| `inspection/` | implementation_code | `contracts/*/inspection/` | `game/domain/inspection/` | `content/domains/inspection/` | `docs/domains/inspection/` | `tests/*/inspection/` | completed | medium | Additional domain root moved. |
| `interaction/` | implementation_code | `contracts/*/interaction/` | `game/domain/interaction/` | `content/domains/interaction/` | `docs/domains/interaction/` | `tests/*/interaction/` | completed | medium | Additional domain root moved. |
| `interior/` | implementation_code | `contracts/*/interior/` | `game/domain/interior/` | `content/domains/interior/` | `docs/domains/interior/` | `tests/*/interior/` | completed | medium | Additional domain root moved. |
| `machines/` | implementation_code | `contracts/*/machines/` | `game/domain/machines/` | `content/domains/machines/` | `docs/domains/machines/` | `tests/*/machines/` | completed | medium | Additional domain root moved. |
| `reality/` | implementation_code | `contracts/*/reality/` | `game/domain/reality/` | `content/domains/reality/` | `docs/domains/reality/` | `tests/*/reality/` | completed | high | Root implementation moved; `specs/reality/` authority unchanged. |
| `economy/` | absent | `contracts/*/economy/` | `game/domain/economy/` | `content/domains/economy/` | `docs/domains/economy/` | `tests/*/economy/` | absent | low | No root-level folder existed. |
| `civilization/` | absent | `contracts/*/civilization/` | `game/domain/civilization/` | `content/domains/civilization/` | `docs/domains/civilization/` | `tests/*/civilization/` | absent | low | No root-level folder existed. |
| `ecology/` | absent | `contracts/*/ecology/` | `game/domain/ecology/` | `content/domains/ecology/` | `docs/domains/ecology/` | `tests/*/ecology/` | absent | low | No root-level folder existed. |
| `control/` | mixed_review | review | review | review | review | review | review | high | Left in place because control surfaces are process-control sensitive and mixed. |
| `core/` | mixed_review | review | review | review | review | review | review | high | Left in place because it may contain universal substrate. |
| `meta/` | mixed_review | review | review | review | review | review | review | review | Left in place because it mixes meta/provenance/tooling/contract-adjacent surfaces. |

## Domain Naming Normalization

| Root | Normalized Domain |
| --- | --- |
| `astro` | `astronomy` |
| `chem` | `chemistry` |
| `electric` | `electricity` |
| `field`, `fields` | `fields` |
| `fluid` | `fluids` |
| `geo` | `geology` |
| `process` | `processes` |
| `system` | `systems` |
| all other moved roots | same stable name |

## Review Roots

`control/`, `core/`, and `meta/` remain root-level review surfaces. They were not moved because their ownership cannot be proven as pure domain implementation without deeper inspection.

## References Updated

Active Python imports and active tool/script path references to moved domain source paths were updated to `game.domain.<domain>` or `game/domain/<domain>/`. Historical docs may still mention old paths and are left for CONVERGE-12 unless they were required for validation.

## Compatibility

No root-level compatibility redirects were retained. The moved implementation has a single authoritative source location under `game/domain/`.
