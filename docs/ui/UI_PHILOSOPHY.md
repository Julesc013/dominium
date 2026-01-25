# UI Philosophy

The UI is a deterministic, non-authoritative projection of the simulation. It
exists to request snapshots, display history, and submit intent requests. It is
not gameplay and it never mutates authoritative state.

## Principles
- Non-authoritative: no state mutation, no authority bypass, no epistemic leaks.
- Parity-first: CLI is the contract; TUI and GUI mirror it exactly.
- Zero-asset baseline: GUI operates fully with zero packs or assets.
- Transparency: refusals and errors surface verbatim.
- Determinism: same inputs produce the same event stream.

## Allowed data sources
UI may consume only:
- Subjective snapshots.
- Event streams.
- History artifacts.
- Capability lists.
- Pack manifests.

UI must not request objective snapshots by default or access debug-only
interfaces unless explicitly enabled.

## State machines
Every screen is an explicit state machine with documented transitions. UI logic
may change presentation, but not simulation state.

## References
- docs/ui/CLI_TUI_GUI_PARITY.md
- docs/ui/ZERO_ASSET_GUI.md
- docs/ui/UI_FORBIDDEN_BEHAVIORS.md
- docs/arch/GUI_BASELINE.md
