# FAB Execution Flow (FAB-1)

Status: binding.
Scope: how FAB data flows into game execution.

## Overview
FAB execution is a data-first pipeline. Schemas define shape and constraints.
Code interprets those shapes without encoding domain meaning.

## Flow
1. FAB data packs are validated by tools (schema shape, units, and references).
2. Registries load records for materials, interfaces, parts, assemblies, and process families.
3. Assemblies are validated for node references and interface compatibility.
4. Aggregation computes mass, volume, capacities, hosted processes, and limits.
5. Process-family execution validates parameters, instruments, standards, and constraints.
6. Deterministic outcomes are selected and surfaced with refusal codes when needed.

## Extension safety
- Mods add new records and references; existing IDs are never reused.
- Unknown fields are preserved in validation and tooling paths.
- Assemblies and processes remain data-driven; no code edits required.

## Determinism and numeric policy
- All authoritative values are fixed-point integers.
- Unit compatibility is mandatory and overflow is a refusal.
- Output ordering is deterministic regardless of input ordering.

## Common failure modes
- Missing unit annotations for numeric map fields.
- Interface references that do not exist or mismatch.
- Process families missing required instruments or standards.
