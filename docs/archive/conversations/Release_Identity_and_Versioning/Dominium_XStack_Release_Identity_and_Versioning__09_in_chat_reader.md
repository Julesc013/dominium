# In-Chat Reader — Dominium XStack Release Identity and Versioning

## Package overview

This package preserves the chat's versioning/release-identity design work for later human reading and aggregation. It includes a full report, context transfer packet, YAML-style spec sheet, structured registers, aggregator packet, reader brief, verification/audit file, bootstrap prompt, and this in-chat reader.

## File index

| File | Purpose |
|---|---|
| 00_manifest | Package inventory and caveats. |
| 01_human_readable_report | Main narrative report, sections 0-16. |
| 02_context_transfer_packet | Future-chat handoff. |
| 03_spec_sheet | YAML-style aggregation/spec data. |
| 04_registers | Workstream/decision/task/constraint/open-question/artifact/risk registers. |
| 05_aggregator_packet | Compact merge packet for a master aggregator chat. |
| 06_reader_brief | Short human overview. |
| 07_verification_and_audit | Self-audit and verification queue. |
| 08_future_chat_bootstrap_prompt | Prompt for continuing in a new chat. |
| 09_in_chat_reader | Guide to this package. |

## Plain-English explanation

This chat decided that Dominium/XStack should use a layered identity architecture: strict SemVer for public API components, SemVer-shaped release IDs for products/suites, GBN/BII/hash for exact provenance, manifests for canonical truth, and capabilities/contracts for internal compatibility. The exact suite semantics, BII schema, target taxonomy, manifest schema, and capability registry still need formal work.

## Question menu

- What is the Release Constitution implied by this chat?
- Which entities should be strict SemVer components?
- What should suite X.Y.Z mean?
- How should GBN and BII appear in metadata and filenames?
- What should the manifest schema be?
- What target families and baselines should exist?
- How should capabilities/contracts be named and negotiated?

## Top things to preserve

Preserve layered identity, strict SemVer scoping, product/suite separation, GBN/BII provenance, lifecycle/prerelease split, manifest authority, and capability-based internal compatibility.

## Safest next actions

Start with Release Constitution and SemVer Component Inventory. Then define suite policy, build identity, channel/lifecycle, artifact names, manifest schema, target taxonomy, and capabilities.
