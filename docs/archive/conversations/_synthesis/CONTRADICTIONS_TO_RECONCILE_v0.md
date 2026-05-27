Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: contradictions_to_reconcile_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_synthesis
Promotion Status: not_promoted
Source Class: conversation_corpus_synthesis


# Contradictions To Reconcile v0

This document summarizes contradiction classes that should feed the reconciliation crosswalk. It does not resolve them.

## Counts By Class

- `conversation_vs_conversation`: `2`
- `conversation_vs_current_queue`: `102`
- `conversation_vs_docs`: `2`
- `stale_external_claim`: `121`

## Highest-Priority Classes

- `conversation_vs_current_queue`: old work suggestions that touch currently blocked scope.
- `conversation_vs_docs`: old baseline or architecture statements that may drift from current README/canon.
- `stale_external_claim`: external platform, SDK, language, renderer, or runtime claims needing current verification.
- `conversation_vs_conversation`: disagreements among old conversations that need review before promotion.

## Sample Findings

- `CONTRA-0001` `conversation_vs_current_queue` `advanced_simulation_infrastructure`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0002` `stale_external_claim` `advanced_simulation_infrastructure`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0003` `stale_external_claim` `advanced_simulation_infrastructure`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0004` `stale_external_claim` `advanced_simulation_infrastructure`: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- `CONTRA-0005` `conversation_vs_current_queue` `app_runtime_platform_renderers`: Archived conversation discusses work related to blocked scope `runtime_module_loader`.
- `CONTRA-0006` `conversation_vs_current_queue` `app_runtime_platform_renderers`: Archived conversation discusses work related to blocked scope `provider_runtime`.
- `CONTRA-0007` `conversation_vs_current_queue` `app_runtime_platform_renderers`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0008` `conversation_vs_current_queue` `app_runtime_platform_renderers`: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- `CONTRA-0009` `stale_external_claim` `app_runtime_platform_renderers`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0010` `conversation_vs_current_queue` `app_testx_codehygiene`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0011` `conversation_vs_current_queue` `app_testx_codehygiene`: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- `CONTRA-0012` `stale_external_claim` `app_testx_codehygiene`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0013` `stale_external_claim` `app_testx_codehygiene`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0014` `stale_external_claim` `app_testx_codehygiene`: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- `CONTRA-0015` `stale_external_claim` `app_testx_codehygiene`: Archived conversation contains potentially stale external or baseline claim: `iOS`.
- `CONTRA-0016` `conversation_vs_current_queue` `architecture_codex_prompts`: Archived conversation discusses work related to blocked scope `provider_runtime`.
- `CONTRA-0017` `conversation_vs_current_queue` `architecture_codex_prompts`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0018` `stale_external_claim` `architecture_codex_prompts`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0019` `stale_external_claim` `architecture_codex_prompts`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0020` `stale_external_claim` `architecture_codex_prompts`: Archived conversation contains potentially stale external or baseline claim: `ISO C89`.
- `CONTRA-0021` `conversation_vs_current_queue` `architecture_ui_providers`: Archived conversation discusses work related to blocked scope `broad_workbench_ui`.
- `CONTRA-0022` `conversation_vs_current_queue` `architecture_ui_providers`: Archived conversation discusses work related to blocked scope `provider_runtime`.
- `CONTRA-0023` `conversation_vs_current_queue` `architecture_ui_providers`: Archived conversation discusses work related to blocked scope `gameplay`.
- `CONTRA-0024` `conversation_vs_current_queue` `architecture_ui_providers`: Archived conversation discusses work related to blocked scope `renderer_implementation`.
- `CONTRA-0025` `conversation_vs_current_queue` `architecture_ui_providers`: Archived conversation discusses work related to blocked scope `native_gui`.
- `CONTRA-0026` `stale_external_claim` `architecture_ui_providers`: Archived conversation contains potentially stale external or baseline claim: `C89`.
- `CONTRA-0027` `stale_external_claim` `architecture_ui_providers`: Archived conversation contains potentially stale external or baseline claim: `C++98`.
- `CONTRA-0028` `stale_external_claim` `architecture_ui_providers`: Archived conversation contains potentially stale external or baseline claim: `DX12`.
- `CONTRA-0029` `stale_external_claim` `architecture_ui_providers`: Archived conversation contains potentially stale external or baseline claim: `SDK`.
- `CONTRA-0030` `stale_external_claim` `Build_and_Future_Proofing`: Archived conversation contains potentially stale external or baseline claim: `C89`.

## Reconciliation Rule

Resolve nothing by convenience. Check canon, glossary, AGENTS, authority order, current queue, contracts/schema law, and targeted current docs before promoting any claim.
