Status: DERIVED
Last Reviewed: 2026-03-28
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: XI-5 bounded src-removal execution against approved mapping lock

# XI-5A Preflight Disaster Cleanup Diagnosis

## Root Cause Class

- primary: `import-generated .pyc cleanup on Windows`
- contributing: `insufficient bounded cleanup normalization for reused disaster work roots`

## Exact Diagnosis

The live STRICT blocker was:

- `PermissionError [WinError 5]`
- path:
  `build/tmp/omega4_disaster_arch_audit/cases/missing_components_missing_binary_referenced_by_install/fixture/dist/tools/xstack/packagingx/__init__.pyc`

The failure did not come from disaster scenario semantics or from missing fixture assembly. It came from teardown of a reused disaster-suite work root under Windows.

`tools/mvp/disaster_suite_common.py::_safe_rmtree()` previously delegated cleanup to a plain recursive delete. When the staged fixture tree contained generated Python bytecode and Windows preserved restrictive file attributes or transient file-handle state, teardown could abort before the case root was fully removed.

The bounded root cause is therefore:

1. generated `__pycache__` and `.pyc` artifacts could survive between case reruns
2. Windows permission normalization was not performed before recursive delete
3. the reused arch-audit disaster work root then failed on teardown before the next case setup completed

## Bounded Conclusion

The repair belongs in deterministic disaster fixture cleanup only. No disaster assertion, refusal policy, arch-audit rule, or runtime behavior needed to change.
