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
    "legacy-win-vs2015",
    "dev-macos-xcode",
    "verify-macos-xcode",
    "release-macos-xcode",
    "dev-linux-gcc",
    "dev-linux-clang",
    "verify-linux-gcc",
    "release-linux-gcc",
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
    "verify-macos-xcode",
    "verify-linux-gcc",
]


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def find_preset(presets, name: str) -> dict:
    for preset in presets:
        if preset.get("name") == name:
            return preset
    raise AssertionError("missing preset: {}".format(name))


def assert_strict_cache(preset: dict, name: str) -> None:
    cache = preset.get("cacheVariables") or {}
    for key, expected in STRICT_KEYS.items():
        if cache.get(key) != expected:
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

    for name in REQUIRED_CONFIGURE:
        find_preset(configure_presets, name)

    for name in REQUIRED_BUILD:
        find_preset(build_presets, name)

    for name in VERIFY_PRESETS:
        preset = find_preset(configure_presets, name)
        assert_strict_cache(preset, name)

    print("Build matrix preset tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
