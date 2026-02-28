# TOOLS_EFFECTS Baseline

Status: ACT-2 baseline complete
Version: 1.0.0

## Scope
ACT-2 introduces ToolEffect and instrument-capable tool assemblies. Tools are data-driven capabilities that filter ActionSurface affordances and pass deterministic effect parameters into process intents.

## Schemas
Source schemas:
- `schema/interaction/tool.schema`
- `schema/interaction/tool_type.schema`
- `schema/interaction/tool_effect_model.schema`
- `schema/interaction/tool_bind.schema`

Compiled schemas:
- `schemas/tool.schema.json`
- `schemas/tool_type.schema.json`
- `schemas/tool_effect_model.schema.json`
- `schemas/tool_bind.schema.json`
- `schemas/tool_type_registry.schema.json`
- `schemas/tool_effect_model_registry.schema.json`

## Registries
- `data/registries/tool_type_registry.json`
- `data/registries/tool_effect_model_registry.json`

Baseline tool types:
- `tool.axe.basic`
- `tool.saw.basic`
- `tool.wrench.basic`
- `tool.hammer.basic`
- `tool.welder.basic`
- `tool.caliper.basic`
- `tool.scanner.basic`

Baseline effect models:
- `effect.basic_hand_tool`
- `effect.basic_cutting`
- `effect.basic_fastening`
- `effect.basic_measurement`
- `effect.basic_welding_stub`

## Runtime Behavior
- Tool assemblies and binds are runtime state rows.
- Processes:
  - `process.tool_bind`
  - `process.tool_unbind`
  - `process.tool_use_prepare`
  - `process.tool_readout_tick`
- Tool bind is entitlement/law gated and deterministic.
- One active tool per subject default is enforced.

## ActionSurface Integration
- Active tool context filters:
  - allowed surface types
  - compatible tool tags
  - allowed process IDs
- Tool effect parameters are attached to affordances and intent payloads.
- No hidden gameplay semantics are added to UI; process runtime remains source of mutation semantics.

## Diegetic Channels
Added derived tool channels:
- `ch.diegetic.tool.torque`
- `ch.diegetic.tool.measurement`
- `ch.diegetic.tool.health`

Readouts are deterministic and derived from perceived-safe state.

## Multiplayer / Anti-Cheat
- Tool use requires active authoritative bind.
- Spoofed use returns deterministic refusal and anti-cheat evidence.
- Ranked/server profiles can restrict tool types via law/entitlements.

## Guardrails
RepoX invariants:
- `INV-TOOLS-DATA-DRIVEN`
- `INV-NO-HARDCODED-TOOL-LOGIC`
- `INV-TOOL_USE_REQUIRES_BIND`

AuditX analyzers:
- `ToolBypassSmell`
- `ToolTruthLeakSmell`

TestX:
- `test_tool_bind_deterministic`
- `test_surface_affordance_filtering_by_tool`
- `test_tool_parameter_pass_through`
- `test_tool_readout_deterministic`
- `test_multiplayer_tool_spoof_refusal`

## Gate Snapshot
- `RepoX` (`STRICT`): pass
- `AuditX` (`scan --format json`): run complete
- `TestX` (ACT-2 + ACT-1 interaction subset): pass
- `strict build` (`tools/xstack/run.py strict`): refusal due pre-existing `CompatX` findings + existing full-suite `TestX` failures outside ACT-2 scope
- `ui_bind --check`: pass

## Extension Points
- ACT-3 task orchestration can consume tool capability/effect metadata without changing process-only mutation.
- Later inventory/crafting systems can manage tool ownership while reusing ACT-2 bind/effect contracts.
