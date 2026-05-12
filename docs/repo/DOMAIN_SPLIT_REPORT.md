# Domain Split Report

Status: PROVISIONAL
Phase: CONVERGE-09

This report explains the CONVERGE-09 root-level domain split. The machine-readable planning artifacts remain `tools/migration/root_inventory.json`, `tools/migration/root_move_map.json`, and `contracts/repo/layout.contract.toml`.

CONVERGE-09 inspected root-level domain packages and moved only clearly classified implementation source into `game/domains/<domain>/`. The inspected moved roots contained Python domain implementation only; no schema, registry, capability, protocol, content, docs, or tests subsets were found inside those roots during the safe split. No new simulation features were added.

| Root | Classification | Contract Target | Implementation Target | Content Target | Docs Target | Tests Target | Status | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `astro/` | implementation_code | `contracts/*/astronomy/` | `game/domains/astronomy/` | `content/domain-data/astronomy/` | `docs/domains/astronomy/` | `tests/*/astronomy/` | completed | medium | Root implementation moved. |
| `chem/` | implementation_code | `contracts/*/chemistry/` | `game/domains/chemistry/` | `content/domain-data/chemistry/` | `docs/domains/chemistry/` | `tests/*/chemistry/` | completed | medium | Root implementation moved. |
| `electric/` | implementation_code | `contracts/*/electricity/` | `game/domains/electricity/` | `content/domain-data/electricity/` | `docs/domains/electricity/` | `tests/*/electricity/` | completed | medium | Root implementation moved. |
| `field/` | implementation_code | `contracts/*/fields/` | `game/domains/fields/from_root_field/` | `content/domain-data/fields/` | `docs/domains/fields/` | `tests/*/fields/` | completed | high | Facade preserved separately under fields. |
| `fields/` | implementation_code | `contracts/*/fields/` | `game/domains/fields/` | `content/domain-data/fields/` | `docs/domains/fields/` | `tests/*/fields/` | completed | high | Canonical field implementation moved without collapsing facade semantics. |
| `fluid/` | implementation_code | `contracts/*/fluids/` | `game/domains/fluids/` | `content/domain-data/fluids/` | `docs/domains/fluids/` | `tests/*/fluids/` | completed | medium | Root implementation moved. |
| `geo/` | implementation_code | `contracts/*/geology/` | `game/domains/geology/` | `content/domain-data/geology/` | `docs/domains/geology/` | `tests/*/geology/` | completed | medium | Root implementation moved; view/projection code remains reviewable domain source. |
| `logic/` | implementation_code | `contracts/*/logic/` | `game/domains/logic/` | `content/domain-data/logic/` | `docs/domains/logic/` | `tests/*/logic/` | completed | medium | Root implementation moved. |
| `materials/` | implementation_code | `contracts/*/materials/` | `game/domains/materials/` | `content/domain-data/materials/` | `docs/domains/materials/` | `tests/*/materials/` | completed | medium | Root implementation moved. |
| `mechanics/` | implementation_code | `contracts/*/mechanics/` | `game/domains/mechanics/` | `content/domain-data/mechanics/` | `docs/domains/mechanics/` | `tests/*/mechanics/` | completed | medium | Root implementation moved. |
| `physics/` | implementation_code | `contracts/*/physics/` | `game/domains/physics/` | `content/domain-data/physics/` | `docs/domains/physics/` | `tests/*/physics/` | completed | medium | Root implementation moved. |
| `pollution/` | implementation_code | `contracts/*/pollution/` | `game/domains/pollution/` | `content/domain-data/pollution/` | `docs/domains/pollution/` | `tests/*/pollution/` | completed | medium | Root implementation moved. |
| `process/` | implementation_code | `contracts/*/processes/` | `game/domains/processes/` | `content/domain-data/processes/` | `docs/domains/processes/` | `tests/*/processes/` | completed | high | Domain process package moved; process-only mutation meaning unchanged. |
| `signals/` | implementation_code | `contracts/*/signals/` | `game/domains/signals/` | `content/domain-data/signals/` | `docs/domains/signals/` | `tests/*/signals/` | completed | medium | Root implementation moved. |
| `system/` | implementation_code | `contracts/*/systems/` | `game/domains/systems/` | `content/domain-data/systems/` | `docs/domains/systems/` | `tests/*/systems/` | completed | high | Simulation system package moved; runtime OS system roots remain separate. |
| `thermal/` | implementation_code | `contracts/*/thermal/` | `game/domains/thermal/` | `content/domain-data/thermal/` | `docs/domains/thermal/` | `tests/*/thermal/` | completed | medium | Root implementation moved. |
| `universe/` | implementation_code | `contracts/*/universe/` | `game/domains/universe/` | `content/domain-data/universe/` | `docs/domains/universe/` | `tests/*/universe/` | completed | medium | Root implementation moved. |
| `worldgen/` | implementation_code | `contracts/*/worldgen/` | `game/domains/worldgen/` | `content/domain-data/worldgen/` | `docs/domains/worldgen/` | `tests/*/worldgen/` | completed | high | Root implementation moved; no generation features added. |
| `mobility/` | implementation_code | `contracts/*/mobility/` | `game/domains/mobility/` | `content/domain-data/mobility/` | `docs/domains/mobility/` | `tests/*/mobility/` | completed | medium | Root implementation moved. |
| `logistics/` | implementation_code | `contracts/*/logistics/` | `game/domains/logistics/` | `content/domain-data/logistics/` | `docs/domains/logistics/` | `tests/*/logistics/` | completed | medium | Root implementation moved. |
| `diegetics/` | implementation_code | `contracts/*/diegetics/` | `game/domains/diegetics/` | `content/domain-data/diegetics/` | `docs/domains/diegetics/` | `tests/*/diegetics/` | completed | medium | Additional domain root moved. |
| `embodiment/` | implementation_code | `contracts/*/embodiment/` | `game/domains/embodiment/` | `content/domain-data/embodiment/` | `docs/domains/embodiment/` | `tests/*/embodiment/` | completed | medium | Additional domain root moved. |
| `epistemics/` | implementation_code | `contracts/*/epistemics/` | `game/domains/epistemics/` | `content/domain-data/epistemics/` | `docs/domains/epistemics/` | `tests/*/epistemics/` | completed | medium | Additional domain root moved. |
| `infrastructure/` | implementation_code | `contracts/*/infrastructure/` | `game/domains/infrastructure/` | `content/domain-data/infrastructure/` | `docs/domains/infrastructure/` | `tests/*/infrastructure/` | completed | medium | Additional domain root moved. |
| `inspection/` | implementation_code | `contracts/*/inspection/` | `game/domains/inspection/` | `content/domain-data/inspection/` | `docs/domains/inspection/` | `tests/*/inspection/` | completed | medium | Additional domain root moved. |
| `interaction/` | implementation_code | `contracts/*/interaction/` | `game/domains/interaction/` | `content/domain-data/interaction/` | `docs/domains/interaction/` | `tests/*/interaction/` | completed | medium | Additional domain root moved. |
| `interior/` | implementation_code | `contracts/*/interior/` | `game/domains/interior/` | `content/domain-data/interior/` | `docs/domains/interior/` | `tests/*/interior/` | completed | medium | Additional domain root moved. |
| `machines/` | implementation_code | `contracts/*/machines/` | `game/domains/machines/` | `content/domain-data/machines/` | `docs/domains/machines/` | `tests/*/machines/` | completed | medium | Additional domain root moved. |
| `reality/` | implementation_code | `contracts/*/reality/` | `game/domains/reality/` | `content/domain-data/reality/` | `docs/domains/reality/` | `tests/*/reality/` | completed | high | Root implementation moved; `specs/reality/` authority unchanged. |
| `economy/` | absent | `contracts/*/economy/` | `game/domains/economy/` | `content/domain-data/economy/` | `docs/domains/economy/` | `tests/*/economy/` | absent | low | No root-level folder existed. |
| `civilization/` | absent | `contracts/*/civilization/` | `game/domains/civilization/` | `content/domain-data/civilization/` | `docs/domains/civilization/` | `tests/*/civilization/` | absent | low | No root-level folder existed. |
| `ecology/` | absent | `contracts/*/ecology/` | `game/domains/ecology/` | `content/domain-data/ecology/` | `docs/domains/ecology/` | `tests/*/ecology/` | absent | low | No root-level folder existed. |
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

Active Python imports and active tool/script path references to moved domain source paths were updated to `game.domains.<domain>` or `game/domains/<domain>/`. Historical docs may still mention old paths and are left for CONVERGE-12 unless they were required for validation.

## Compatibility

No root-level compatibility redirects were retained. The moved implementation has a single authoritative source location under `game/domains/`.
