# AGENT GOALS

Agents MUST treat goals as declarative data that describes desired world-state conditions.
Goals MUST be serializable, inspectable, and modifiable only via processes.
Goals MUST NOT encode actions, strategies, or assumed success.

Goals MUST include identifiers, priority/urgency, acceptable risk, time horizon,
epistemic confidence, and abandonment/deferral conditions.
Agents MAY hold multiple simultaneous and mutually incompatible goals.
Goal arbitration MUST be deterministic and capability/authority gated.

Goals MUST NOT assume human psychology, player intent, or human-centric defaults.
Goals MUST NOT rely on "AI magic" or hidden optimization heuristics.

References:
- docs/architecture/INVARIANTS.md
- docs/architecture/REALITY_LAYER.md
