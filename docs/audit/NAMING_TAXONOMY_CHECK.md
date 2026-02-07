Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Naming & Taxonomy Check

## Scope

- Pack identifiers under `data/packs/`
- Schema identifiers under `schema/`
- Major registry namespaces

## Pack ID inventory (prefixes observed)

- `org.dominium.base.*`
- `org.dominium.core.*`
- `org.dominium.epistemics.*`
- `org.dominium.examples.*`
- `org.dominium.lib.*`
- `org.dominium.realities.*`
- `org.dominium.worldgen.*`

All observed pack IDs are lowercase, dot-separated, and namespaced. No illegal
`OTHER/UNKNOWN` sentinel names were detected in pack IDs.

## Schema naming

Schemas are stored as flat `schema/*.schema` files with `schema_id` and
semantic `schema_version`. No conflicting naming patterns detected in file
names. See `docs/schema/SCHEMA_INDEX.md` for authoritative naming rules.

All checked schema files include an explicit `stability:` field; no missing
stability annotations were detected in this pass.

## Registries / namespaces

No new registry naming collisions detected in this pass.

## Fix list

None in this audit. Any future naming normalization requires a scoped prompt
and explicit migration plan.
