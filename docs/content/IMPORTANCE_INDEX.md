# Importance Index

The importance index is a content-level field used to prioritize inspection,
navigation, and tooling. It MUST NOT change simulation truth.

## Field Definition

- Field type: `navigation.importance.index`
- Units: `unitless`
- Representation: typically procedural at macro LOD

## Usage

- Tools MAY use the index to rank regions or nodes for inspection.
- Clients MAY use it to focus rendering or reporting.
- The simulation MUST ignore the index for authoritative behavior.

## Tags

Importance fields MAY include tags such as:
- `navigation`
- `research`
- `hazards`

Tags are descriptive only. Unknown tags MUST be preserved.
