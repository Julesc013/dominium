#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from _common import ensure_cache_path, load_json, repo_root, write_json
import world_definition_lib as wdlib


def _print_json(payload):
    print(json.dumps(payload, indent=2, sort_keys=True))


def cmd_list_templates(_args):
    _print_json({"templates": wdlib.list_templates()})
    return 0


def cmd_generate(args):
    params = {"seed.primary": args.seed}
    result = wdlib.run_template(args.template_id, params)
    if not result.get("ok"):
        _print_json({"ok": False, "refusal": result.get("refusal")})
        return 2
    worlddef = result["world_definition"]
    if args.output:
        root = repo_root()
        output = ensure_cache_path(Path(args.output), root)
        write_json(output, worlddef)
    else:
        _print_json(worlddef)
    return 0


def cmd_validate(args):
    payload = load_json(Path(args.input))
    result = wdlib.validate_world_definition(payload, available_capabilities=args.capability)
    _print_json(result)
    return 0 if result.get("ok") else 3


def cmd_diff(args):
    left = load_json(Path(args.left))
    right = load_json(Path(args.right))
    diffs = wdlib.diff_worlddefs(left, right, strip_extensions=args.strip_extensions)
    _print_json({"differences": diffs})
    return 0 if not diffs else 4


def cmd_equivalence(args):
    left = load_json(Path(args.left))
    right = load_json(Path(args.right))
    diffs = wdlib.diff_worlddefs(left, right, strip_extensions=True)
    _print_json({"equivalent": not diffs, "differences": diffs})
    return 0 if not diffs else 5


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list-templates")
    list_cmd.set_defaults(func=cmd_list_templates)

    gen_cmd = sub.add_parser("generate")
    gen_cmd.add_argument("--template-id", required=True)
    gen_cmd.add_argument("--seed", type=int, default=0)
    gen_cmd.add_argument("--output")
    gen_cmd.set_defaults(func=cmd_generate)

    val_cmd = sub.add_parser("validate")
    val_cmd.add_argument("--input", required=True)
    val_cmd.add_argument("--capability", action="append", default=[])
    val_cmd.set_defaults(func=cmd_validate)

    diff_cmd = sub.add_parser("diff")
    diff_cmd.add_argument("--left", required=True)
    diff_cmd.add_argument("--right", required=True)
    diff_cmd.add_argument("--strip-extensions", action="store_true")
    diff_cmd.set_defaults(func=cmd_diff)

    eq_cmd = sub.add_parser("equivalence")
    eq_cmd.add_argument("--left", required=True)
    eq_cmd.add_argument("--right", required=True)
    eq_cmd.set_defaults(func=cmd_equivalence)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
