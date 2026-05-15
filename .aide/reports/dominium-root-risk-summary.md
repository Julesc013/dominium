# Dominium Root Risk Summary

Status: needs_review

## Selected Root

- Root: `ide/`
- Risk: high / review_required
- Files: 4 tracked
- Fate: keep all

## Risk Drivers

- `ide/README.md`: authority-sensitive root behavior policy.
- `ide/manifests/projection_manifest.schema.json`: identity-sensitive schema.
- Projection examples: generated-sensitive fixtures.
- Baseline AIDE ownership remains unknown.

## Deferred Roots

- Product roots are deferred.
- Doctrine and contract roots are deferred.
- Tool-system roots are deferred.
- `governance/` is deferred for extra authority review.

## Safety Result

No file operation, reference rewrite, alias, shim, product edit, doctrine edit, tool edit, branch mutation, or provider/network call occurred.
