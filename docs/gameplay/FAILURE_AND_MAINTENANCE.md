Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Failure and Maintenance

This document defines failure as a first-class, process-driven outcome. It MUST
be read alongside `docs/gameplay/ON_PLANET_ACTIONS.md`.

## Failure Is Normal

Failure MUST be modeled as a process output, not an exception. All wear,
degradation, and failure MUST be expressed through processes with explicit
provenance.

## Maintenance Processes

Maintenance MUST be represented by processes such as:
- wear_accumulate
- inspect_condition
- degrade_performance
- fail_component
- repair
- replace_part

Each process MUST declare inputs, outputs, time/energy cost descriptors, and
failure modes.

## Partial Simulation

Maintenance MUST support explicit degradation and partial simulation. Missing
capabilities MUST result in explicit downgrade, not silent success.

## Required Schemas

Maintenance content MUST use:
- `schema/process.schema`
- `schema/field.schema`
- `schema/part_and_interface.schema`
- `schema/assembly.schema`
- `schema/knowledge.schema`

## UPS Rules

Maintenance libraries MUST be delivered via UPS packs and resolved by
capability.