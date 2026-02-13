Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# Gate Remediation Record

- gate: `exitcheck`
- blocker_type: `OTHER`
- artifact_dir: `docs/audit/remediation/vs2026/20260213T054938Z_exitcheck_OTHER`

## Failure Output

```
MSBuild version 18.0.5+e22287bf1 for .NET Framework

  Run TestX fast suite (manifest-driven)
  {
    "required_test_tags": [
      "docs",
      "invariant"
    ],
    "result": "suite_complete",
    "returncode": 8,
    "selected_tests": [
      "inv_proof_manifest",
      "inv_repox_rules",
      "tools_auditx"
    ],
    "suite_id": "testx_fast",
    "summary_json": "docs/audit/testx/TESTX_SUMMARY.json"
  }
C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Microsoft\VC\v180\Microsoft.CppCommon.targets(254,5): error MSB8066: Custom build for 'C:\Inbox\Git Repos\dominium\out\build\vs2026\verify\CMakeFiles\e79bb7050942be89f695b7f4c5716a5d\testx_fast.rule' exited with code 8. [C:\Inbox\Git Repos\dominium\out\build\vs2026\verify\testx_fast.vcxproj]
```
