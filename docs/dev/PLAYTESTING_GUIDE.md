# Playtesting Guide (Slice-4 Harness)

This guide explains how to run deterministic playtests using scenario and variant data, capture replays, and analyze results. It does not add gameplay rules.

**Purpose**
- Keep iteration data-only and deterministic.
- Ensure CLI, TUI, and GUI execute the same intent APIs.
- Make replays the primary artifact for analysis and regression.

**Scenario Files**
Scenario files are text, header-first, and declarative. A scenario defines the world template, seed, policies, and optional initial adjustments.

Format (minimal):
```text
DOMINIUM_SCENARIO_V1
scenario_id=org.example.playtest.minimal
scenario_version=1.0.0
world_template=builtin.minimal_system
world_seed=42
policy.authority=policy.authority.shell
policy.mode=policy.mode.nav.free
policy.playtest=policy.playtest.sandbox
lockfile_id=org.example.lockfile.playtest
lockfile_hash=hash.example
```

Optional sections:
```text
variants_begin
variant scope=world system=planning id=planning.v1
variants_end

fields_begin
field id=4 value=1.0 known=1
fields_end

agents_begin
agent id=100 caps=survey auth=infra know=infra
agents_end
```

Notes:
- Comments start with `#` or `;`.
- Fields use numeric field IDs and Q16 values (e.g., `1.0`).
- Agents use capability/authority/knowledge tokens (`survey`, `infra`, etc).

**Variant Files**
Variants override scenario parameters without changing semantics. They may adjust policies, seed, and variant selections.

Format:
```text
DOMINIUM_VARIANT_V1
variant_id=org.example.playtest.variant.swap
variant_version=1.0.0
policy.playtest=policy.playtest.regression
variants_begin
variant scope=world system=planning id=planning.v1_shadow
variants_end
```

**Running Sessions (CLI)**
Use `batch` to chain commands.
```text
client "batch scenario-load path=data/scenarios/default.scenario; replay-save"
client "batch scenario-load path=data/scenarios/default.scenario variant=data/variants/variant_swap.variant; replay-save"
```

**Running Sessions (TUI/GUI)**
UI scripts use action tokens. Scenario and variant actions use default paths.
```text
client --ui=tui --ui-script "scenario-load,save,exit" --ui-frames 5
client --ui=gui --headless --renderer null --ui-script "scenario-load,save,exit" --ui-frames 5
```

Defaults used by UI actions:
- Scenario: `data/scenarios/default.scenario`
- Variant: `data/variants/default.variant`

**Replays**
Replays are text files that include meta, variants, and events.
```text
DOMINIUM_REPLAY_V1
meta_begin
scenario_id=...
scenario_version=...
scenario_variants=...
lockfile_id=...
lockfile_hash=...
meta_end
variants_begin
variant scope=world system=planning id=planning.v1
variants_end
events_begin
event_seq=1 event=client.scenario.load path=... result=ok
events_end
```

**Tools**
Use the playtest tools for headless analysis:
- `tools/playtest/replay_run.py` computes deterministic event hashes.
- `tools/playtest/replay_diff.py` compares replays (meta, variants, or events).
- `tools/playtest/replay_metrics.py` summarizes event-derived metrics.
- `tools/playtest/replay_timeline.py` emits a macro/micro timeline.

Examples:
```text
python tools/playtest/replay_run.py --input data/saves/session.replay --format json
python tools/playtest/replay_diff.py --left a.replay --right b.replay --compare events --fail-on-diff
python tools/playtest/replay_metrics.py --input data/saves/session.replay --format text
python tools/playtest/replay_timeline.py --input data/saves/session.replay --format csv
```

**Refusals and Metrics**
- Use `refusal` to see the last refusal code and detail.
- Metrics are derived from event streams only. Use `replay_metrics.py` for reproducible analysis.
