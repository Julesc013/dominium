# Crafting Baseline (T10)

Status: baseline, deterministic, process-only.

This document defines the minimal crafting layer that transforms explicit
inputs into explicit outputs without progression, economy, or automation.

## What crafting is (and is not)

Crafting is an **atomic process** that consumes specific inputs and produces
specific outputs under tool and condition constraints. It is **not** a tech
tree, progression system, or batch production pipeline.

Included:
- Process-only crafting (`process.craft.execute`).
- Deterministic input consumption and output creation.
- Tool and environmental condition checks.
- Disassembly/recycling via inverse recipes (with losses).

Excluded (explicitly):
- Tech trees, unlocks, or skill checks.
- Economy, pricing, or trade.
- Factories, batch queues, or automation.

## Process model

Crafting is implemented as a single deterministic process:

- `process.craft.execute`
  - Validates inputs, tools, conditions, and law/meta-law.
  - Consumes inputs, produces outputs and optional byproducts.
  - Emits deterministic events for replay.

Failure is explicit:
- Refusal explains the violated condition or missing tool.
- If a failure mode allows waste, inputs are consumed and byproducts are produced.

## Tools & conditions

Tools are assemblies with integrity:
- Required tools must exist and meet minimum integrity.
- Tools can wear and break over time.

Conditions are field-derived:
- Temperature and humidity ranges are checked deterministically.
- Environment tags are matched when required.

## Disassembly & recycling

Disassembly is defined by explicit inverse recipes:
- Outputs are scaled by a configured loss factor.
- Optional waste/byproducts can be produced.
- No perfect reversibility is assumed by default.

## Determinism & budgets

All crafting operations:
- Are deterministic and replayable.
- Consume explicit budgets.
- Remain constant-cost with respect to world size.

## Maturity

This baseline is **BOUNDED**:
- It is intentionally simple and data-driven.
- It is extensible for later automation or economy layers without changing
  the core process model.
