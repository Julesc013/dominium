Status: CANONICAL
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Prompt Firewall Policy

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


ControlX enforces a prompt firewall before any command execution.

## Untrusted Prompt Handling

- Prompts are parsed as data, not authority.
- Policy determines what text is forbidden, sanitized, or ignored.
- Forbidden directives are removed without operator confirmation.

## Forbidden Prompt Directives

- stop-on-failure mechanics
- ask-user-for-permission mechanics
- gate/tool bypass instructions
- direct `check_repox_rules.py`, `ctest`, `tool_ui_*`, or `performx.py` calls
- disable-rule or weaken-governance language

## Execution Normalization

Prompt instructions are normalized into this contract:

1. `gate.py precheck`
2. apply sanitized change intent
3. `gate.py taskcheck`
4. `gate.py exitcheck`

No alternative prompt-supplied execution path is authoritative.

## Escalation Policy

ControlX escalates only for semantic ambiguity:

- canon meaning conflicts
- ontology changes
- legal/licensing decisions
- security/trust policy decisions

All non-semantic failures are remediated mechanically and execution continues.
