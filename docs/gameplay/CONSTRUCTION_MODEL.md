Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Construction Model

This document defines construction as a process pipeline. It MUST be read
alongside `docs/gameplay/ON_PLANET_ACTIONS.md`.

## Construction Is a Process Pipeline

Construction MUST be expressed as a chain of processes, not prefabs or build
modes. The canonical pipeline includes:
- survey_site (epistemic)
- clear_and_prepare (transformative)
- establish_foundation (transformative)
- claim_volume (transactional)
- place_part (transformative)
- connect_interface (transformative)
- verify_integrity (epistemic)
- certify_structure (transactional)

Each step MUST declare inputs, outputs, time/energy costs, and failure modes.

## Structures

A structure MUST be defined as:
- Claimed domain volumes
- An assembly graph of parts
- Network attachments (optional)
- A host for processes

No structure type is hardcoded. All structure meaning is content-defined.

## Vehicles

Vehicles MUST be treated as mobile assemblies with constraints and capabilities.
Movement and operation MUST be expressed as processes, not special-case systems.

## Required Schemas

Construction content MUST use:
- `schema/process.schema`
- `schema/part_and_interface.schema`
- `schema/assembly.schema`
- `schema/domain.schema`
- `schema/knowledge.schema`

## UPS Rules

Construction libraries MUST be delivered via UPS packs and resolved by
capability. No construction step may assume a specific asset or pack.