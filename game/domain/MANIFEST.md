# Game Domains Manifest

Status: PROVISIONAL
Phase: CONVERGE-09

CONVERGE-09 moved root-level domain implementation packages that were inspected as Python-only domain source. No schema, registry, content, docs, or test subsets were identified inside the moved roots during this safe split. Review-heavy mixed roots were left in place.

| Previous Root | Domain Name | New Implementation Location | Other Targets | Action | Notes |
| --- | --- | --- | --- | --- | --- |
| `astro/` | astronomy | `game/domain/astronomy/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `chem/` | chemistry | `game/domain/chemistry/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `electric/` | electricity | `game/domain/electricity/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `field/` | fields facade | `game/domain/fields/from_root_field/` | contracts/content/docs/tests by split rule | completed | Compatibility facade preserved under the fields domain. |
| `fields/` | fields | `game/domain/fields/` | contracts/content/docs/tests by split rule | completed | Field implementation moved without merging facade files. |
| `fluid/` | fluids | `game/domain/fluids/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `geo/` | geology | `game/domain/geology/` | contracts/content/docs/tests by split rule | completed | Python implementation moved; presentation-adjacent modules remain domain source for now. |
| `logic/` | logic | `game/domain/logic/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `materials/` | materials | `game/domain/materials/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `mechanics/` | mechanics | `game/domain/mechanics/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `physics/` | physics | `game/domain/physics/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `pollution/` | pollution | `game/domain/pollution/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `process/` | processes | `game/domain/processes/` | contracts/content/docs/tests by split rule | completed | Domain process implementation moved; process-only mutation semantics unchanged. |
| `signals/` | signals | `game/domain/signals/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `system/` | systems | `game/domain/systems/` | contracts/content/docs/tests by split rule | completed | Simulation systems implementation moved; OS/runtime system ownership remains excluded. |
| `thermal/` | thermal | `game/domain/thermal/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `universe/` | universe | `game/domain/universe/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `worldgen/` | worldgen | `game/domain/worldgen/` | contracts/content/docs/tests by split rule | completed | Python implementation moved; no new generation features added. |
| `mobility/` | mobility | `game/domain/mobility/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `logistics/` | logistics | `game/domain/logistics/` | contracts/content/docs/tests by split rule | completed | Python implementation moved. |
| `economy/` | economy | none | contracts/content/docs/tests by split rule | absent | No root-level `economy/` was present. |
| `civilization/` | civilization | none | contracts/content/docs/tests by split rule | absent | No root-level `civilization/` was present. |
| `ecology/` | ecology | none | contracts/content/docs/tests by split rule | absent | No root-level `ecology/` was present. |
| `diegetics/` | diegetics | `game/domain/diegetics/` | contracts/content/docs/tests by split rule | completed | Additional domain root inspected and moved. |
| `embodiment/` | embodiment | `game/domain/embodiment/` | contracts/content/docs/tests by split rule | completed | Additional domain root inspected and moved. |
| `epistemics/` | epistemics | `game/domain/epistemics/` | contracts/content/docs/tests by split rule | completed | Additional domain root inspected and moved. |
| `infrastructure/` | infrastructure | `game/domain/infrastructure/` | contracts/content/docs/tests by split rule | completed | Additional domain root inspected and moved. |
| `inspection/` | inspection | `game/domain/inspection/` | contracts/content/docs/tests by split rule | completed | Additional domain root inspected and moved. |
| `interaction/` | interaction | `game/domain/interaction/` | contracts/content/docs/tests by split rule | completed | Additional domain root inspected and moved. |
| `interior/` | interior | `game/domain/interior/` | contracts/content/docs/tests by split rule | completed | Additional domain root inspected and moved. |
| `machines/` | machines | `game/domain/machines/` | contracts/content/docs/tests by split rule | completed | Additional domain root inspected and moved. |
| `reality/` | reality | `game/domain/reality/` | contracts/content/docs/tests by split rule | completed | Additional domain root inspected and moved; `specs/reality/` authority is unchanged. |
| `control/` | control | none | review | review | Left in place because it is process-control sensitive and mixed with runtime/contract concerns. |
| `core/` | core | none | review | review | Left in place because it may contain universal substrate, not only domain implementation. |
| `meta/` | meta | none | review | review | Left in place because it mixes meta, provenance, tooling, and contract-adjacent surfaces. |

No product, runtime, archive, generated-output, schema-root, or content-root migrations were performed in this phase.
