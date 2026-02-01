Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Reality Flow (REALITY0)





Status: binding.


Scope: canonical intent-to-audit flow for reality interactions.





This flow applies to all authoritative actions, including tool and admin


requests. Refusal, absence, and deferral are valid outcomes.





## Invariants


- All authoritative actions pass law/capability gates.


- Effects are scheduled on ACT and audited.


- Refusal, absence, and deferral are valid outcomes.





## Canonical flow


1) Intent


   - Declare actor, capability set, and law targets.


2) Law & Capability Gate


   - Evaluate law kernel; accept/refuse/transform.


   - Accepted intents become actions.


3) Reality Checks


   - Domain permissions and jurisdiction.


   - Existence state and archival status.


   - Visitability and refinement contract.


4) Scheduling (ACT)


   - Schedule on ACT; deterministic ordering and budgets.


5) Effect


   - Explicit effect emission; no direct mutation outside effects.


6) Audit


   - Record law decisions, effects, and rationale.





## Valid outcomes


- Accept: proceed with scheduling and effect emission.


- Refuse: emit refusal with explanation and audit.


- Defer: schedule later or degrade deterministically.


- Absent: no-op without error when a system is disabled.





## Forbidden assumptions


- Direct state mutation without effects is allowed.


- Law gates can be skipped for tools or admins.





## Dependencies


- Law enforcement points: `docs/architecture/LAW_ENFORCEMENT_POINTS.md`


- Reality layer: `docs/architecture/REALITY_LAYER.md`





## See also


- `docs/architecture/REALITY_LAYER.md`


- `docs/architecture/VISITABILITY_AND_REFINEMENT.md`


- `docs/architecture/LAW_ENFORCEMENT_POINTS.md`


- `docs/architecture/REFUSAL_AND_EXPLANATION_MODEL.md`


- `schema/law/SPEC_LAW_KERNEL.md`
