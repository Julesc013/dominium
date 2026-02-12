"""AuditX analyzer registry."""

from analyzers import a1_reachability_orphaned
from analyzers import a2_ownership_boundary
from analyzers import a3_canon_drift
from analyzers import a4_schema_usage
from analyzers import a5_capability_misuse
from analyzers import a6_ui_parity_bypass
from analyzers import a7_legacy_contamination
from analyzers import a8_derived_freshness_smell
from analyzers import b1_duplicate_concept
from analyzers import b2_schema_shadowing
from analyzers import b3_capability_drift
from analyzers import b4_derived_artifact_contract
from analyzers import b5_cross_pack_entropy
from analyzers import b6_prompt_drift
from analyzers import b7_workspace_contamination
from analyzers import b8_blocker_recurrence
from analyzers import c1_security_boundary
from analyzers import c2_mode_flag_smell
from analyzers import c3_capability_bypass_smell
from analyzers import c4_terminology_misuse


ANALYZERS = (
    a1_reachability_orphaned,
    a2_ownership_boundary,
    a3_canon_drift,
    a4_schema_usage,
    a5_capability_misuse,
    a6_ui_parity_bypass,
    a7_legacy_contamination,
    a8_derived_freshness_smell,
    b1_duplicate_concept,
    b2_schema_shadowing,
    b3_capability_drift,
    b4_derived_artifact_contract,
    b5_cross_pack_entropy,
    b6_prompt_drift,
    b7_workspace_contamination,
    b8_blocker_recurrence,
    c1_security_boundary,
    c2_mode_flag_smell,
    c3_capability_bypass_smell,
    c4_terminology_misuse,
)


def run_analyzers(graph, repo_root, changed_files=None):
    findings = []
    for analyzer in ANALYZERS:
        findings.extend(analyzer.run(graph, repo_root, changed_files=changed_files))
    return findings
