Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# org.dominium.core.interaction.baseline

Purpose: Provide baseline interaction primitives (inspect/place/remove/measure/signal) with zero external assets.

Maturity: BOUNDED

Capabilities:
- org.dominium.core.interaction

Dependencies (capability-level):
- org.dominium.core.materials
- org.dominium.core.interfaces
- org.dominium.core.units
- org.dominium.core.standards
- org.dominium.core.signals

Contents:
- `data/fab_pack.json` (marker, beacon, indicator, and baseline measurement instrument)

Primitives:
- org.dominium.core.interaction.marker (Maturity: BOUNDED)
- org.dominium.core.interaction.beacon (Maturity: STRUCTURAL)
- org.dominium.core.interaction.indicator (Maturity: STRUCTURAL)
- org.dominium.core.instrument.measure.baseline (Maturity: BOUNDED)

Notes:
- Data-only and optional.
- Signal roles are declarative; behavior is enforced by law/meta-law and client tooling.
