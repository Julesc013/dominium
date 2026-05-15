# Remaining Risks

- Full 130-task eval is too slow or hangs in this target state; use representative task runs until Q51/Q52 investigates eval runtime.
- Source bundle direct import remains blocked by an inner checksum entry for missing `.aide.local.example/secrets/README.md`.
- Source pack omits `.aide/providers/README.md`; Q50 treats this as a warning rather than synthesizing source content.
- `verify` WARN remains because diff-scope policy does not recognize all Q50 generated portable paths under the active packet.
- Repo intelligence reports 1635 unknown classifications; Q51 should classify/wrap existing systems rather than delete or migrate them.
- Gateway/provider status is report-only fallback because Q50 did not touch product-root `core/**`.

