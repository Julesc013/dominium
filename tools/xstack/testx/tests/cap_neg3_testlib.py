"""Shared CAP-NEG-3 degrade-ladder test helpers."""

from __future__ import annotations


def compiled_fallback_negotiation(repo_root: str) -> dict:
    from tools.xstack.testx.tests.cap_neg_testlib import ensure_repo_on_path

    ensure_repo_on_path(repo_root)
    from compat import build_default_endpoint_descriptor, negotiate_endpoint_descriptors

    server = build_default_endpoint_descriptor(
        repo_root,
        product_id="server",
        product_version="0.0.0+test.server.compiled",
    )
    engine = build_default_endpoint_descriptor(
        repo_root,
        product_id="engine",
        product_version="0.0.0+test.engine.l1",
    )
    server["feature_capabilities"] = sorted(
        set(list(server.get("feature_capabilities") or []) + ["cap.logic.compiled_automaton", "cap.logic.l1_eval"])
    )
    server["optional_capabilities"] = sorted(
        set(list(server.get("optional_capabilities") or []) + ["cap.logic.compiled_automaton"])
    )
    engine["feature_capabilities"] = sorted(
        set(
            [token for token in list(engine.get("feature_capabilities") or []) if str(token).strip() != "cap.logic.compiled_automaton"]
            + ["cap.logic.l1_eval"]
        )
    )
    engine["optional_capabilities"] = sorted(
        set([token for token in list(engine.get("optional_capabilities") or []) if str(token).strip() != "cap.logic.compiled_automaton"])
    )
    return negotiate_endpoint_descriptors(
        repo_root,
        server,
        engine,
        allow_read_only=False,
        chosen_contract_bundle_hash="hash.contract.bundle.test",
    )
