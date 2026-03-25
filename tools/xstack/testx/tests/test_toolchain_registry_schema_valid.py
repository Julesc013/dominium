"""FAST test: Ω-9 toolchain registries expose the expected schemas and baseline ids."""

from __future__ import annotations


TEST_ID = "test_toolchain_registry_schema_valid"
TEST_TAGS = ["fast", "omega", "toolchain", "release"]


def run(repo_root: str):
    from tools.mvp.toolchain_matrix_common import (
        TOOLCHAIN_MATRIX_REGISTRY_SCHEMA_ID,
        TOOLCHAIN_TEST_PROFILE_REGISTRY_SCHEMA_ID,
    )
    from tools.xstack.testx.tests.toolchain_matrix_testlib import (
        committed_matrix_registry,
        committed_profile_registry,
    )

    matrix_registry = committed_matrix_registry(repo_root)
    profile_registry = committed_profile_registry(repo_root)
    if str(matrix_registry.get("schema_id", "")).strip() != TOOLCHAIN_MATRIX_REGISTRY_SCHEMA_ID:
        return {"status": "fail", "message": "toolchain matrix registry schema_id drifted"}
    if str(profile_registry.get("schema_id", "")).strip() != TOOLCHAIN_TEST_PROFILE_REGISTRY_SCHEMA_ID:
        return {"status": "fail", "message": "toolchain test profile registry schema_id drifted"}
    env_ids = {
        str((row or {}).get("env_id", "")).strip()
        for row in list((dict(matrix_registry.get("record") or {}).get("environments") or []))
        if str((row or {}).get("env_id", "")).strip()
    }
    profile_ids = {
        str((row or {}).get("profile_id", "")).strip()
        for row in list((dict(profile_registry.get("record") or {}).get("profiles") or []))
        if str((row or {}).get("profile_id", "")).strip()
    }
    for required_id in ("winnt-msvc-x86_64-vs2026", "linux-gcc-x86_64-debian13", "macosx-clang-x86_64-10_14"):
        if required_id not in env_ids:
            return {"status": "fail", "message": "missing toolchain env {}".format(required_id)}
    for required_id in ("toolchain.smoke", "toolchain.determinism_core", "toolchain.ecosystem", "toolchain.full"):
        if required_id not in profile_ids:
            return {"status": "fail", "message": "missing toolchain profile {}".format(required_id)}
    return {"status": "pass", "message": "toolchain registries expose expected schemas and baseline ids"}
