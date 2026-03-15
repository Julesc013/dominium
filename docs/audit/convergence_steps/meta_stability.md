Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for meta_stability

# Convergence Step - META-STABILITY validator

- step_no: `2`
- step_id: `meta_stability`
- result: `complete`
- rule_id: `INV-ALL-REGISTRIES-TAGGED`
- source_fingerprint: `36a38a33c72fd25be2643e8078959a0f139f43a1fc2e902346a66ff8164c18f8`
- observed_refusal_count: `0`
- observed_degrade_count: `0`

## Key Hashes

- stability_report_fingerprint: `36a38a33c72fd25be2643e8078959a0f139f43a1fc2e902346a66ff8164c18f8`

## Notes

- registry_report_count=408
- violations=0

## Source Paths

- `data/registries`

## Remediation

- module=`src/meta/stability/stability_validator.py` rule=`INV-ALL-REGISTRIES-TAGGED` refusal=`none` command=`@'
from src.meta.stability.stability_validator import validate_all_registries
import json
print(json.dumps(validate_all_registries('.'), indent=2, sort_keys=True))
'@ | python -`
