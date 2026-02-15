"""STRICT test: SRZ hybrid perceived transport filters deterministic fields without truth leakage."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.net.srz_hybrid.client_interest_filter_no_leak"
TEST_TAGS = ["strict", "net", "session", "srz"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.net.policies.policy_srz_hybrid import join_client_hybrid, prepare_hybrid_baseline
    from tools.xstack.testx.tests.net_hybrid_testlib import clone_runtime, prepare_hybrid_runtime_fixture

    fixture = prepare_hybrid_runtime_fixture(
        repo_root=repo_root,
        save_id="save.testx.net.srz_hybrid.no_leak",
        client_peer_id="peer.client.hybrid.alpha",
    )
    runtime = clone_runtime(fixture)
    baseline = prepare_hybrid_baseline(repo_root=repo_root, runtime=runtime)
    if str(baseline.get("result", "")) != "complete":
        return {"status": "fail", "message": "hybrid baseline preparation failed before no-leak check"}

    restricted_authority = copy.deepcopy(dict(fixture.get("authority_context") or {}))
    restricted_authority["entitlements"] = sorted(
        set(
            token
            for token in (restricted_authority.get("entitlements") or [])
            if str(token).strip() and str(token).strip() != "entitlement.inspect"
        )
    )
    restricted_law = copy.deepcopy(dict(fixture.get("law_profile") or {}))
    epistemic_limits = dict(restricted_law.get("epistemic_limits") or {})
    epistemic_limits["allow_hidden_state_access"] = False
    restricted_law["epistemic_limits"] = epistemic_limits

    joined = join_client_hybrid(
        repo_root=repo_root,
        runtime=runtime,
        peer_id="peer.client.hybrid.restricted",
        authority_context=restricted_authority,
        law_profile=restricted_law,
        lens_profile=dict(fixture.get("lens_profile") or {}),
        negotiated_policy_id="policy.net.srz_hybrid",
        snapshot_id=str((baseline.get("snapshot") or {}).get("snapshot_id", "")),
    )
    if str(joined.get("result", "")) != "complete":
        reason = str(((joined.get("refusal") or {}).get("reason_code", "")) if isinstance(joined, dict) else "")
        return {"status": "fail", "message": "restricted peer join refused ({})".format(reason)}

    clients = dict(runtime.get("clients") or {})
    restricted = dict(clients.get("peer.client.hybrid.restricted") or {})
    perceived_model = dict(restricted.get("last_perceived_model") or {})
    observed_fields = list(perceived_model.get("observed_fields") or [])
    observed_field_ids = sorted(
        str(row.get("field_id", "")).strip()
        for row in observed_fields
        if isinstance(row, dict) and str(row.get("field_id", "")).strip()
    )

    hidden_tokens = [field_id for field_id in observed_field_ids if field_id.startswith("time_control.")]
    if hidden_tokens:
        return {"status": "fail", "message": "restricted peer observed hidden time_control fields over net path"}
    if "simulation_time.tick" not in observed_field_ids:
        return {"status": "fail", "message": "restricted peer missing required simulation_time.tick observed field"}

    forbidden_top_level = ("truth_model", "universe_state", "registry_payloads")
    leaked = [token for token in forbidden_top_level if token in perceived_model]
    if leaked:
        return {"status": "fail", "message": "perceived payload leaked forbidden truth keys: {}".format(",".join(leaked))}
    return {"status": "pass", "message": "srz hybrid perceived no-leak filter check passed"}

