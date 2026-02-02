import argparse
import os
import shutil
import subprocess
import sys

BUILD_INFO_KEYS = [
    "product=",
    "product_version=",
    "sku=",
    "engine_version=",
    "game_version=",
    "build_number=",
    "build_id=",
    "build_kind=",
    "build_bii=",
    "build_gbn=",
    "build_timestamp=",
    "git_hash=",
    "git_commit=",
    "toolchain_id=",
    "toolchain_family=",
    "toolchain_version=",
    "toolchain_stdlib=",
    "toolchain_runtime=",
    "toolchain_link=",
    "toolchain_target=",
    "toolchain_os=",
    "toolchain_arch=",
    "toolchain_os_floor=",
    "toolchain_config=",
    "protocol_law_targets=",
    "protocol_control_caps=",
    "protocol_authority_tokens=",
    "abi_dom_build_info=",
    "abi_dom_caps=",
    "api_dsys=",
    "platform_ext_window_ex_api=",
    "platform_ext_error_api=",
    "platform_ext_cliptext_api=",
    "platform_ext_cursor_api=",
    "platform_ext_dragdrop_api=",
    "platform_ext_gamepad_api=",
    "platform_ext_power_api=",
    "platform_ext_text_input_api=",
    "platform_ext_window_mode_api=",
    "platform_ext_dpi_api=",
    "api_dgfx=",
]


def run_cmd(cmd, expect_code=0, expect_nonzero=False, expect_contains=None):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    output = result.stdout
    if expect_nonzero:
        if result.returncode == 0:
            sys.stderr.write("FAIL: expected non-zero exit for {}\n".format(cmd))
            sys.stderr.write(output)
            return False
    elif expect_code is not None and result.returncode != expect_code:
        sys.stderr.write("FAIL: expected exit {} for {}\n".format(expect_code, cmd))
        sys.stderr.write(output)
        return False
    if expect_contains:
        for token in expect_contains:
            if token not in output:
                sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, cmd))
                sys.stderr.write(output)
                return False
    return True


def check_build_info(exe, product_name):
    result = subprocess.run(
        [exe, "--build-info"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
    )
    output = result.stdout
    if result.returncode != 0:
        sys.stderr.write("FAIL: expected exit 0 for {}\n".format([exe, "--build-info"]))
        sys.stderr.write(output)
        return False
    for token in BUILD_INFO_KEYS + ["product=" + product_name]:
        if token not in output:
            sys.stderr.write("FAIL: missing '{}' in output for {}\n".format(token, exe))
            sys.stderr.write(output)
            return False
    info = {}
    for line in output.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            info[key.strip()] = value.strip()
    build_kind = info.get("build_kind", "")
    build_bii = info.get("build_bii", "")
    build_gbn = info.get("build_gbn", "")
    if build_kind not in ("dev", "ci"):
        sys.stderr.write("FAIL: unexpected build_kind '{}'\n".format(build_kind))
        return False
    if not build_bii:
        sys.stderr.write("FAIL: missing build_bii value\n")
        return False
    if build_kind in ("dev", "ci") and build_gbn != "none":
        sys.stderr.write("FAIL: build_gbn must be 'none' for {}\n".format(build_kind))
        return False
    if not info.get("build_timestamp"):
        sys.stderr.write("FAIL: missing build_timestamp value\n")
        return False
    if not info.get("git_commit"):
        sys.stderr.write("FAIL: missing git_commit value\n")
        return False
    return True


def check_basic_cli(exe, product_token):
    ok = True
    ok = ok and run_cmd([exe, "--help"], expect_contains=["usage"])
    ok = ok and run_cmd([exe, "--version"], expect_contains=[product_token])
    return ok


def ensure_clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--server", required=True)
    parser.add_argument("--launcher", required=True)
    parser.add_argument("--setup", required=True)
    parser.add_argument("--tools", required=True)
    parser.add_argument("--temp-root", required=True)
    args = parser.parse_args()

    ok = True

    ok = ok and check_basic_cli(args.client, "client ")
    ok = ok and check_basic_cli(args.server, "server ")
    ok = ok and check_basic_cli(args.launcher, "launcher ")
    ok = ok and check_basic_cli(args.setup, "setup ")
    ok = ok and check_basic_cli(args.tools, "tools ")

    ok = ok and check_build_info(args.client, "client")
    ok = ok and check_build_info(args.server, "server")
    ok = ok and check_build_info(args.launcher, "launcher")
    ok = ok and check_build_info(args.setup, "setup")
    ok = ok and check_build_info(args.tools, "tools")

    ok = ok and run_cmd([args.client, "--smoke"])
    ok = ok and run_cmd([args.server, "--smoke"])
    ok = ok and run_cmd([args.launcher, "--smoke"])
    ok = ok and run_cmd([args.setup, "--smoke"])
    ok = ok and run_cmd([args.tools, "--smoke"])

    ok = ok and run_cmd([args.client, "--ui=none", "--smoke"])
    ok = ok and run_cmd([args.server, "--ui=none", "--smoke"])
    ok = ok and run_cmd([args.launcher, "--ui=none", "--smoke"])
    ok = ok and run_cmd([args.setup, "--ui=none", "--smoke"])
    ok = ok and run_cmd([args.tools, "--ui=none", "--smoke"])

    ok = ok and run_cmd([args.client, "--deterministic", "--smoke"])
    ok = ok and run_cmd([args.server, "--deterministic", "--smoke"])
    ok = ok and run_cmd([args.launcher, "--deterministic", "--smoke"])
    ok = ok and run_cmd([args.setup, "--deterministic", "--smoke"])
    ok = ok and run_cmd([args.tools, "--deterministic", "--smoke"])

    ok = ok and run_cmd(
        [args.client, "--interactive", "--smoke"],
        expect_nonzero=True,
        expect_contains=["requires deterministic"],
    )
    ok = ok and run_cmd(
        [args.server, "--interactive", "--smoke"],
        expect_nonzero=True,
        expect_contains=["requires deterministic"],
    )
    ok = ok and run_cmd(
        [args.launcher, "--interactive", "--smoke"],
        expect_nonzero=True,
        expect_contains=["requires deterministic"],
    )
    ok = ok and run_cmd(
        [args.setup, "--interactive", "--smoke"],
        expect_nonzero=True,
        expect_contains=["requires deterministic"],
    )
    ok = ok and run_cmd(
        [args.tools, "--interactive", "--smoke"],
        expect_nonzero=True,
        expect_contains=["requires deterministic"],
    )

    ok = ok and run_cmd(
        [args.client, "--renderer=missing", "--smoke"],
        expect_nonzero=True,
        expect_contains=["unavailable"],
    )

    ok = ok and run_cmd(
        [args.launcher, "capabilities"],
        expect_contains=[
            "platform_backend=",
            "renderer_auto=",
            "renderer=",
            "platform_ext_dpi=",
            "platform_ext_window_mode=",
        ],
    )

    ok = ok and run_cmd(
        [args.server, "--ui=gui"],
        expect_nonzero=True,
        expect_contains=["gui not implemented"],
    )
    ok = ok and run_cmd(
        [args.launcher, "--ui=gui", "--headless", "--renderer", "null", "--ui-frames", "1"],
    )
    ok = ok and run_cmd(
        [args.setup, "--ui=gui"],
        expect_nonzero=True,
        expect_contains=["gui not implemented"],
    )
    ok = ok and run_cmd(
        [args.tools, "--ui=gui", "--headless", "--renderer", "null", "--ui-frames", "1"],
    )

    temp_root = os.path.abspath(args.temp_root)
    ensure_clean_dir(temp_root)
    setup_root = os.path.join(temp_root, "setup_root")
    ok = ok and run_cmd(
        [args.setup, "prepare", "--root", setup_root],
        expect_contains=["setup_prepare=ok"],
    )
    for name in ("program", "data", "user", "state", "temp"):
        if not os.path.isdir(os.path.join(setup_root, name)):
            sys.stderr.write("FAIL: missing directory {}\n".format(name))
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
