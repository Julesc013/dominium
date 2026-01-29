import argparse
import os


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def assert_contains(text, needle, label):
    if needle not in text:
        raise AssertionError("missing {}: {}".format(label, needle))


def test_platform_doc(repo_root):
    doc_path = os.path.join(repo_root, "docs", "architecture", "PLATFORM_RESPONSIBILITY.md")
    if not os.path.isfile(doc_path):
        raise AssertionError("missing platform responsibility doc")
    text = read_text(doc_path)
    required_sections = [
        "Platform Responsibility",
        "Supported Platform Classes",
        "Filesystem & Path Rules",
        "Time & Clock Model",
        "Threading & Concurrency",
        "IPC & Multi-Process",
        "Environment & Config",
        "Error Handling & Exit Codes",
        "Freeze & Lock",
    ]
    for section in required_sections:
        assert_contains(text, section, "platform doc section")

    env_vars = [
        "DSYS_PATH_APP_ROOT",
        "DSYS_PATH_USER_DATA",
        "DSYS_PATH_USER_CONFIG",
        "DSYS_PATH_USER_CACHE",
        "DSYS_PATH_TEMP",
        "OPS_DETERMINISTIC",
        "USERNAME",
        "USER",
    ]
    for env in env_vars:
        assert_contains(text, env, "env var")


def test_locklist(repo_root):
    path = os.path.join(repo_root, "docs", "architecture", "LOCKLIST.md")
    text = read_text(path)
    assert_contains(text, "Platform runtime layer", "locklist platform entry")


def test_exit_codes(repo_root):
    header = os.path.join(repo_root, "engine", "include", "domino", "app", "runtime.h")
    text = read_text(header)
    for token in [
        "D_APP_EXIT_OK",
        "D_APP_EXIT_FAILURE",
        "D_APP_EXIT_USAGE",
        "D_APP_EXIT_UNAVAILABLE",
        "D_APP_EXIT_SIGNAL",
    ]:
        assert_contains(text, token, "exit code")


def test_null_platform_backend(repo_root):
    sys_impl = os.path.join(repo_root, "engine", "modules", "system", "sys.c")
    text = read_text(sys_impl)
    assert_contains(text, "DSYS_BACKEND_NULL", "null backend macro")
    assert_contains(text, "null_time_now_us", "null time source")


def test_sandbox_guard(repo_root):
    sys_impl = os.path.join(repo_root, "engine", "modules", "system", "sys.c")
    text = read_text(sys_impl)
    assert_contains(text, "dsys_guard_io_blocked", "sandbox guard")


def test_deterministic_dir_iteration(repo_root):
    dtlv = os.path.join(repo_root, "engine", "modules", "io", "dtlv.c")
    text = read_text(dtlv)
    assert_contains(text, "Deterministic directory order", "deterministic dir ordering")


def test_headless_flags(repo_root):
    launcher_cli = os.path.join(repo_root, "launcher", "cli", "launcher_cli_main.c")
    text = read_text(launcher_cli)
    assert_contains(text, "--headless", "headless flag")
    assert_contains(text, "--ui=none", "ui none flag")


def main():
    parser = argparse.ArgumentParser(description="Platform contract tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    test_platform_doc(repo_root)
    test_locklist(repo_root)
    test_exit_codes(repo_root)
    test_null_platform_backend(repo_root)
    test_sandbox_guard(repo_root)
    test_deterministic_dir_iteration(repo_root)
    test_headless_flags(repo_root)

    print("PLATFORM-PERFECT-0 contract tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
