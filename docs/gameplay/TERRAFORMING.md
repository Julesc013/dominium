# Terraforming

This document defines field-based planetary modification. It MUST be read
alongside `docs/gameplay/ON_PLANET_ACTIONS.md`.

## Field-Based Modification

Terraforming MUST be expressed as processes that modify atmosphere, climate,
hydrology, and biomass fields at declared LODs. No instant transformations are
permitted.

## Time and Energy

Terraforming processes MUST declare explicit time and energy cost descriptors.
They MUST be long-horizon and causal.

## Conservation

Mass and energy conservation MUST be explicit in process inputs, outputs, and
waste descriptors. No hidden sources or sinks are permitted.

## Required Schemas

Terraforming content MUST use:
- `schema/process.schema`
- `schema/field.schema`
- `schema/domain.schema`
- `schema/material.schema`

## UPS Rules

Terraforming libraries MUST be delivered via UPS packs and resolved by
capability. No pack is required for engine or game boot.
