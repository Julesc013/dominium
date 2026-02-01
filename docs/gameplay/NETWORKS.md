Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Networks

This document defines the unified network abstraction for on-planet systems.
It MUST be read alongside `docs/gameplay/ON_PLANET_ACTIONS.md`.

## Unified Graph Model

All networks MUST use the graph model defined by `schema/network.schema`.
Networks are content-defined and MUST NOT introduce bespoke systems per type.

## Network Types

Network type is a tag, not a hardcoded system. Examples include:
- electrical
- fluid
- thermal
- logistics
- data

Unknown network types MUST be preserved.

## Capacity and Loss

Capacity and loss are descriptive metadata. They MUST NOT encode simulation
behavior. Processes MUST interpret them explicitly.

## Attachment and Flow

Network attachment, routing, and balancing MUST be expressed as processes with
declared authority scope and failure modes. No direct mutation is permitted.

## Required Schemas

Network content MUST use:
- `schema/network.schema`
- `schema/process.schema`
- `schema/assembly.schema`
- `schema/part_and_interface.schema`
- `schema/domain.schema`

## UPS Rules

Network libraries MUST be delivered via UPS packs and resolved by capability.