Status: DERIVED
Stability: stable
Future Series: OMEGA
Replacement Target: Frozen offline update simulation baseline for v0.0.0-mock distribution gating.

# Update Simulation Run

- result: `complete`
- platform_tag: `win64`
- deterministic_fingerprint: `9e1863aafb874bbdbadb028b556e6d4e809078518904ff0d3ff8ed0cee09d4ad`
- baseline_present: `True`
- baseline_matches: `True`

## Scenario Results

- baseline install: result=`complete`, plan=`ac4c7ce3b7a02b064fd3d0d0358fdeedb849c088386deeb6d2970882d66ac5b0`, component_set_hash=`dbed548b7f8de8e7e046783f78fef90c7c3e3da36f2ac837419f832d69e03223`
- latest-compatible upgrade: result=`complete`, plan=`3bbdd2dfbb2ceb8e4f996643453211061073702561182eb34bd7c62a6a73390a`, client=`0.0.1`
- yanked exclusion: result=`complete`, skipped_yanked_count=`1`, selected_yanked=`none`
- strict trust: result=`complete`, refusal_code=`refusal.trust.signature_missing`
- rollback: result=`complete`, restored_component_set_hash=`dbed548b7f8de8e7e046783f78fef90c7c3e3da36f2ac837419f832d69e03223`
