# Reader Brief — Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture

## What this chat was about

This chat established a future-proofing doctrine for Dominium: stable repository ownership, AIDE-driven refactorability, portable modular code, reusable engine/runtime/contracts, and mechanically enforced compatibility boundaries.

## Top 20 things to know

1. The user wants Dominium built like a serious long-lived game/engine platform.
2. The goal is not just cleaner folders; it is long-term portability and refactorability.
3. A stable root constitution is needed.
4. New top-level roots should be refused by default.
5. AIDE should become the refactor control plane.
6. Old XStack/AuditX/RepoX/TestX-style tools should be recycled, not deleted.
7. Temporary workflow names should not become product architecture.
8. Paths are not identity.
9. Contracts and manifests define identity.
10. Apps should be thin.
11. Runtime owns host adaptation.
12. Engine owns deterministic reusable substrate.
13. Game owns Dominium-specific rules.
14. Content is authored data, not runtime cache.
15. Public APIs need stability levels.
16. Stable C ABI seams should use opaque handles, allocators, versioned structs, error codes.
17. Schemas/protocols need versioning and negotiation.
18. Generated artifacts need quarantine.
19. Future refactors should use AIDE move maps and salvage maps.
20. Live repo status must be verified before implementation.

## Decisions

See DECISION-01 through DECISION-10 in the registers. The clearest user-accepted decisions are AIDE adoption and recycling existing material.

## Pending tasks

Highest priority: verify repo state; implement AIDE-STRUCTURE-00; inventory old tooling; implement AIDE-ARCH-00.

## Open questions

Main questions: current live repo state; useful old tooling; stable API boundaries; reuse-level classification; generated artifact policy; which recommendations become formal requirements.

## Artifacts

The uploaded `Pasted text.txt` prompt requested this preservation package. This package generated Markdown, YAML, and ZIP outputs.

## Verification items

Verify live repo head, CTest/validator status, referenced docs, old tool paths, component matrix names, and prior generated file availability.

## Best next step

Run live repo baseline verification, then implement AIDE-STRUCTURE-00 as a non-invasive control-plane task.
