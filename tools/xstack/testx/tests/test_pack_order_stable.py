"""FAST test: GEO-9 same-precedence pack ordering is stable by canonical layer sort."""

from __future__ import annotations

import sys


TEST_ID = "test_pack_order_stable"
TEST_TAGS = ["fast", "geo", "overlay", "ordering"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from geo import explain_property_origin
    from tools.xstack.testx.tests.geo9_testlib import OBJECT_ID_EARTH, overlay_fixture_merge_result

    first = overlay_fixture_merge_result(include_mods=True, include_save=False)
    second = overlay_fixture_merge_result(
        include_mods=True,
        include_save=False,
        reverse_mod_order=True,
        reverse_patch_order=True,
        reverse_resolved_packs=True,
    )
    merge_a = dict(first.get("merge_result") or {})
    merge_b = dict(second.get("merge_result") or {})
    if str(merge_a.get("result", "")) != "complete" or str(merge_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "overlay merge did not complete in pack order fixture"}
    if merge_a.get("effective_object_views") != merge_b.get("effective_object_views"):
        return {"status": "fail", "message": "effective object views changed when pack input order changed"}
    if str(merge_a.get("overlay_merge_result_hash_chain", "")).strip() != str(
        merge_b.get("overlay_merge_result_hash_chain", "")
    ).strip():
        return {"status": "fail", "message": "overlay result hash changed when pack input order changed"}
    origin = explain_property_origin(merge_result=merge_a, object_id=OBJECT_ID_EARTH, property_path="display_name")
    if str(origin.get("current_layer_id", "")).strip() != "mod.beta":
        return {"status": "fail", "message": "stable same-precedence pack ordering did not resolve to the expected layer"}
    return {"status": "pass", "message": "GEO-9 pack ordering stable under reordered manifest/patch inputs"}
