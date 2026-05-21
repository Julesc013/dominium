Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Pack Mount Model

Pack mounting is governed by explicit plan, order, trust, compatibility,
overlay, conflict, and evidence law. COMPOSITION-RESOLVER-LAW-01 defines the
contract surface only; it does not mount packages or load pack payloads.

## Pack Classes

Composition plans and locks must be able to distinguish:

- base packs
- official packs
- mod packs
- theme packs
- user profile packs
- workspace packs

Those classes may have different trust and compatibility requirements. A mount
decision records the selected class and evidence; it does not infer authority
from a directory.

## Order

Packs sort by declared mount order, then `pack_id`, then version where policy
declares version as a tie-breaker. If two packs produce ambiguous ordering, the
composition decision must refuse, degrade, or cite an explicit conflict policy.

Existing pack verification and mod trust law remain authoritative for stronger
pack-specific requirements. This document records the product-level composition
result without replacing those laws.

## Overlays

Overlays are ordered contributions. Every overlapping contribution must declare
conflict behavior. Silent overwrite, implicit last-wins, ignored conflict, and
best-effort conflict behavior are forbidden.

User profile overrides and workspace overrides are allowed only when explicit
and evidenced. The decision must show which input contributed the override and
which policy allowed it.

## Conflicts

A conflict exists when two or more mounted inputs claim the same payload,
capability, provider, module contribution, schema binding, command binding, or
other governed composition slot. Conflicts require a report with stable
identifiers, participating sources, selected behavior, diagnostics, and
evidence.

No pack conflict may be resolved by path order, filesystem order, or hidden
last-writer behavior.

## Evidence

`pack_mount.lock.json` records selected packs, mount order, overlays, conflict
reports, diagnostics, evidence, limitations, and status. It is derived evidence,
not a source manifest.

Fixture locks are acceptable for contract proof. They do not prove package
runtime mounting, package loader behavior, or product launch behavior.
