import argparse
import json
import os


REQUIRED_CONFIGURE = [
    "local",
    "verify",
    "release-check",
    "dev-win-vs2026",
    "verify-win-vs2026",
    "release-win-vs2026",
    "msvc-dev-debug",
    "msvc-dev-release",
    "msvc-verify",
    "msvc-verify-full",
    "release-winnt-x86_64",
    "win9x-x86_32-legacy",
    "win16-x86_16",
    "dos-x86_16",
    "legacy-win-vs2015",
    "dev-macos-xcode",
    "verify-macos-xcode",
    "release-macos-xcode",
    "macos-dev",
    "macos-verify",
    "macos-verify-full",
    "release-macos-arm64",
    "dev-linux-gcc",
    "dev-linux-clang",
    "verify-linux-gcc",
    "release-linux-gcc",
    "linux-gcc-dev",
    "linux-clang-dev",
    "linux-verify",
    "linux-verify-full",
    "release-linux-x86_64",
]

REQUIRED_BUILD = list(REQUIRED_CONFIGURE)

STRICT_KEYS = {
    "CMAKE_C_STANDARD": "90",
    "CMAKE_C_STANDARD_REQUIRED": "ON",
    "CMAKE_C_EXTENSIONS": "OFF",
    "CMAKE_CXX_STANDARD": "98",
    "CMAKE_CXX_STANDARD_REQUIRED": "ON",
    "CMAKE_CXX_EXTENSIONS": "OFF",
}

VERIFY_PRESETS = [
    "verify",
    "release-check",
    "verify-win-vs2026",
    "msvc-verify",
    "msvc-verify-full",
    "verify-macos-xcode",
    "macos-verify",
    "macos-verify-full",
    "verify-linux-gcc",
    "linux-verify",
    "linux-verify-full",
]

EXPECTED_BUILD_TARGETS = {
    "local": "all_runtime",
    "dev-win-vs2026": "all_runtime",
    "msvc-dev-debug": "all_runtime",
    "msvc-dev-release": "all_runtime",
    "verify": "verify_fast",
    "verify-win-vs2026": "verify_fast",
    "msvc-verify": "verify_fast",
    "release-check": "verify_full",
    "msvc-verify-full": "verify_full",
    "release-win-vs2026": "dist_all",
    "release-winnt-x86_64": "dist_all",
    "dev-macos-xcode": "all_runtime",
    "macos-dev": "all_runtime",
    "verify-macos-xcode": "verify_fast",
    "macos-verify": "verify_fast",
    "macos-verify-full": "verify_full",
    "release-macos-xcode": "dist_all",
    "release-macos-arm64": "dist_all",
    "dev-linux-gcc": "all_runtime",
    "dev-linux-clang": "all_runtime",
    "linux-gcc-dev": "all_runtime",
    "linux-clang-dev": "all_runtime",
    "verify-linux-gcc": "verify_fast",
    "linux-verify": "verify_fast",
    "linux-verify-full": "verify_full",
    "release-linux-gcc": "dist_all",
    "release-linux-x86_64": "dist_all",
    "win9x-x86_32-legacy": "all_runtime",
    "win16-x86_16": "all_runtime",
    "dos-x86_16": "all_runtime",
}


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def find_preset(presets, name: str) -> dict:
    for preset in presets:
        if preset.get("name") == name:
            return preset
    raise AssertionError("missing preset: {}".format(name))


def resolve_cache_value(configure_map: dict, name: str, key: str):
    seen = set()
    current = name
    while current and current not in seen:
        seen.add(current)
        preset = configure_map.get(current)
        if not isinstance(preset, dict):
            return None
        cache = preset.get("cacheVariables") or {}
        if key in cache:
            return cache.get(key)
        inherits = preset.get("inherits")
        if isinstance(inherits, list):
            current = inherits[0] if inherits else None
        elif isinstance(inherits, str):
            current = inherits
        else:
            current = None
    return None


def assert_strict_cache(configure_map: dict, name: str) -> None:
    for key, expected in STRICT_KEYS.items():
        actual = resolve_cache_value(configure_map, name, key)
        if actual != expected:
            raise AssertionError("preset {} missing strict {}={}".format(name, key, expected))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build matrix preset tests")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    presets_path = os.path.join(repo_root, "CMakePresets.json")
    data = load_json(presets_path)
    configure_presets = data.get("configurePresets") or []
    build_presets = data.get("buildPresets") or []
    configure_map = {}
    for preset in configure_presets:
        if isinstance(preset, dict):
            name = preset.get("name")
            if isinstance(name, str) and name:
                configure_map[name] = preset

    for name in REQUIRED_CONFIGURE:
        find_preset(configure_presets, name)

    for name in REQUIRED_BUILD:
        find_preset(build_presets, name)

    for name in VERIFY_PRESETS:
        find_preset(configure_presets, name)
        assert_strict_cache(configure_map, name)

    for name, expected_target in EXPECTED_BUILD_TARGETS.items():
        preset = find_preset(build_presets, name)
        targets = preset.get("targets") or []
        if expected_target not in targets:
            raise AssertionError(
                "build preset {} missing target {} (got {})".format(name, expected_target, targets)
            )

    print("Build matrix preset tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
