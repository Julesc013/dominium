# History and Civilization Model (HIST0)

Status: binding.
Scope: derived history, civilization graphs, and collective memory.

## Invariants (locked)
- History is a lossy, biased, derived summary of replayed events.
- History is not ground truth, not omniscient, and not complete.
- Civilizations are graphs of institutions; they have fuzzy, overlapping boundaries.
- No history artifact may exist without provenance to replay/process sources.
- History never retroactively alters physical outcomes or determinism.
- All mutation is process-driven; no implicit background edits.

## Provider chain (canonical)
Sources -> Events -> Epochs -> Nodes -> Edges -> Graphs

Providers are deterministic, capability-registered, and interest/budget bounded.

## Data model
### History sources
- Bind replay/process events to recorded perspectives.
- Each source includes perspective, confidence, bias, and recorded tick.
- Sources are required for any historical event.

### Historical events
- Derived from one or more sources.
- Categorized (war, disaster, reform, discovery).
- Include confidence, uncertainty, bias, and optional decay.
- May be modified by explicit history processes.

### Epochs
- Derived intervals with fuzzy boundaries.
- Can be contested and perspective-dependent.
- Provide macro grouping for events.

### Civilization graphs
- Nodes: institutions (from governance).
- Edges: cooperation, dependency, conflict, cultural exchange.
- Weights: trust, trade volume, shared standards.
- Graphs are descriptive summaries, not ownership claims.

## Processes (history mechanics)
All history changes are explicit processes:
- process.history.record
- process.history.forget
- process.history.revise
- process.history.mythologize

Processes are deterministic and replayable. They operate on historical events
by adjusting confidence, uncertainty, and bias; they never alter physical logs.

## Archaeology and rediscovery
- Archaeology is measurement + inference over ruins, data, and artifacts.
- Rediscovery produces new sources and events with explicit uncertainty.
- Contradictory histories coexist; trust/legitimacy shifts are downstream effects.

## Determinism and replay
- History derivation is deterministic given:
  - replay logs
  - source catalogs
  - process events
- No wall-clock inputs; named RNG streams only when needed.

## Collapse / expand
Macro capsules retain coarse summaries:
- Invariants: total recorded events per epoch.
- Sufficient statistics: event distributions, bias/confidence histograms.
- RNG cursor continuity preserved.

## Integration boundaries
- History influences trust, legitimacy, risk, conflict narratives, and knowledge.
- History never bypasses law, replay, or determinism.
- Presentation layers may visualize timelines; they are non-authoritative.
