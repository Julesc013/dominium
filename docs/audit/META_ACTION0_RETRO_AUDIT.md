Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# META-ACTION-0 Retro Consistency Audit

Status: AUDIT
Last Updated: 2026-03-03
Scope: Canonical action categorization pre-audit before Action Grammar enforcement.

## 1) Inventory Snapshot

Observed registry-backed action surfaces:

- `data/registries/control_action_registry.json`
  - control actions: `23`
- `data/registries/interaction_action_registry.json`
  - interaction actions: `48`
- `data/registries/task_type_registry.json`
  - task types: `9`
- `data/registries/process_registry.json`
  - process records: `97`

Process family prefixes (top groups):

- `process.on_planet.terrain` (11)
- `process.on_planet.construction` (9)
- `process.epistemic` (8)
- `process.on_planet.network` (7)
- `process.on_planet.terraforming` (7)
- `process.on_planet.maintenance` (6)
- `process.on_planet.mining` (6)
- `process.on_planet.regulation` (6)
- `process.on_planet.trade` (6)
- `process.on_planet.manufacturing` (5)

## 2) Provisional Family Categorization

Using provisional canonical-family mapping over IDs:

- control actions:
  - `DECIDE/AUTHORIZE`: 11
  - `TRANSFORM`: 9
  - `SENSE/MEASURE`: 2
  - `MOVE`: 1
- interaction actions:
  - `SENSE/MEASURE`: 16
  - `TRANSFORM`: 18
  - `STORE/CONTAIN`: 3
  - `DECIDE/AUTHORIZE`: 3
  - `MAINTAIN`: 1
  - `MOVE`: 6
  - `COMMUNICATE`: 1
- process records:
  - `DECIDE/AUTHORIZE`: 57
  - `TRANSFORM`: 25
  - `SENSE/MEASURE`: 11
  - `COMMUNICATE`: 2
  - `STORE/CONTAIN`: 1
  - `MOVE`: 1
- task types:
  - `TRANSFORM`: 7
  - `MAINTAIN`: 1
  - `DECIDE/AUTHORIZE`: 1

## 3) Potential Drift / Edge Cases

The following are valid but semantically broad and require explicit template metadata to avoid drift:

- `action.interaction.execute_process` (generic adapter action)
- `process.meta_pose_override` (meta-authority path)
- `process.schema.migrate.*` (governance/migration actions)
- `org.dominium.base.rules.process.template.*` (template process placeholders)

These are not uncategorizable, but they need strong Action Template declarations so future domains do not bypass canonical families.

## 4) Bespoke Migration Risks

Potential bespoke logic surfaces for follow-up migration hardening:

- generic process adapter actions (`action.interaction.execute_process`)
- control aliases (`control.action.*`) vs canonical `action.*` naming
- mixed-use process families where one process can touch multiple substrates by input payload

## 5) Migration Plan

1. Introduce canonical `action_family` and `action_template` schemas.
2. Register all current control/interaction/task/process IDs into templates.
3. Map every control-plane-exposed action to exactly one family.
4. Enforce template lookup and requirement checks in control-plane resolution.
5. Add RepoX/AuditX/TestX enforcement to block unregistered/bespoke drift.
