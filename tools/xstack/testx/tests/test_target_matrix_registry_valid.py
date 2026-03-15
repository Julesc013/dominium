"""FAST test: ARCH-MATRIX target registry and baseline report are valid."""

from __future__ import annotations


TEST_ID = "test_target_matrix_registry_valid"
TEST_TAGS = ["fast", "release", "platform", "arch-matrix"]


def run(repo_root: str):
    from tools.xstack.testx.tests.arch_matrix_testlib import build_report, current_violations, load_registry

    registry = load_registry(repo_root)
    rows = list(dict(registry.get("record") or {}).get("targets") or [])
    ids = [str(dict(row).get("target_id", "")).strip() for row in rows]
    expected = [
        "target.os_bsd.abi_null.arch_x86_64",
        "target.os_linux.abi_glibc.arch_arm64",
        "target.os_linux.abi_glibc.arch_x86_64",
        "target.os_macos_classic.abi_carbon.arch_ppc32",
        "target.os_macosx.abi_cocoa.arch_arm64",
        "target.os_msdos.abi_freestanding.arch_x86_32",
        "target.os_posix.abi_null.arch_riscv64",
        "target.os_posix.abi_null.arch_x86_64",
        "target.os_posix.abi_sdl.arch_x86_64",
        "target.os_web.abi_wasm.arch_wasm32",
        "target.os_win9x.abi_mingw.arch_x86_32",
        "target.os_winnt.abi_msvc.arch_x86_32",
        "target.os_winnt.abi_msvc.arch_x86_64",
    ]
    if ids != expected:
        return {"status": "fail", "message": "target matrix registry ids drifted from governed order"}
    report = build_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "ARCH-MATRIX report did not complete successfully"}
    violations = current_violations(repo_root)
    if violations:
        return {"status": "fail", "message": "ARCH-MATRIX governance violations remain: {}".format(len(violations))}
    return {"status": "pass", "message": "target matrix registry and baseline report are valid"}
