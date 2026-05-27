# In-Chat Reader — Dominium Canon, Repository Alignment, and Portability Doctrine

## Package overview

This package preserves a chat about Dominium’s old v1 canon, current repository alignment, and future-proofing practices. It includes a human-readable report, registers, context packet, spec sheet, aggregator packet, audit, bootstrap prompt, and reader guide.

## File index

- `00_manifest`: package index and caveats.
- `01_human_readable_report`: main explanation.
- `02_context_transfer_packet`: handoff for future chat.
- `03_spec_sheet`: YAML-style structured summary.
- `04_registers`: workstreams, decisions, tasks, risks, verification queue.
- `05_aggregator_packet`: compact merge packet.
- `06_reader_brief`: shorter human brief.
- `07_verification_and_audit`: self-audit and verification queue.
- `08_future_chat_bootstrap_prompt`: prompt for new chat.
- `09_in_chat_reader`: this guide.

## Question menu

- What did the repo audit actually prove?
- What is only an inference?
- Which recommendations should become formal requirements?
- What should be verified before cleanup?
- How do we design the second Domino reuse proof?
- How should public API/ABI boundaries be written?
- What belongs in engine vs game vs runtime vs apps?
- How do we avoid overclaiming implementation maturity?

## Top things to preserve

- Old v1 canon and glossary.
- Repo-materialized canon authority.
- Ownership-root layout.
- Stable contracts/replaceable implementations doctrine.
- Docs/schema/code/test separation.
- Verification queue.

## Safest next actions

1. Verify current physical repo tree.
2. Run/check strict layout validators.
3. Inventory public APIs and schemas.
4. Audit survival process runtime.
5. Only then plan refactor/cleanup waves.
