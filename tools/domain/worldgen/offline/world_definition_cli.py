#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from _common import ensure_cache_path, load_json, repo_root, write_json
import world_definition_lib as wdlib


def _print_json(payload):
    print(json.dumps(payload, indent=2, sort_keys=True))


def _load_pack_paths(args):
    if not args.packs:
        return [repo_root() / "data" / "packs"]
    return [Path(p).expanduser().resolve() for p in args.packs]


def cmd_list_templates(args):
    templates = wdlib.list_all_templates(pack_paths=_load_pack_paths(args))
    if args.format == "text":
        lines = []
        for entry in templates:
            template_id = entry.get("template_id", "")
            version = entry.get("version", "")
            source = entry.get("source", "")
            desc = entry.get("description", "").replace("|", "/")
            lines.append(f"{template_id}|{version}|{source}|{desc}")
        output = "\n".join(lines) + ("\n" if lines else "")
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0
    _print_json({"templates": templates})
    return 0


def cmd_generate(args):
    params = {"seed.primary": args.seed}
    if args.policy_movement:
        params["policy.movement"] = args.policy_movement
    if args.policy_authority:
        params["policy.authority"] = args.policy_authority
    if args.policy_mode:
        params["policy.mode"] = args.policy_mode
    if args.policy_debug:
        params["policy.debug"] = args.policy_debug
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


def cmd_summarize(args):
    payload = load_json(Path(args.input))
    summary = wdlib.summarize_worlddef(payload)
    if args.format == "text":
        lines = [
            f"worlddef_id={summary.get('worlddef_id', '')}",
            f"template_id={summary.get('template_id', '')}",
            f"spawn_node_id={summary.get('spawn_node_id', '')}",
            f"spawn_frame_id={summary.get('spawn_frame_id', '')}",
        ]
        pos = summary.get("spawn_pos", {})
        ori = summary.get("spawn_orient", {})
        lines.append(f"spawn_pos={pos.get('x', 0)},{pos.get('y', 0)},{pos.get('z', 0)}")
        lines.append(f"spawn_orient={ori.get('yaw', 0)},{ori.get('pitch', 0)},{ori.get('roll', 0)}")
        policy_sets = summary.get("policy_sets", {})
        def fmt_list(values):
            return ",".join([str(v) for v in values]) if isinstance(values, list) else ""
        lines.append(f"policy_movement={fmt_list(policy_sets.get('movement_policies', []))}")
        lines.append(f"policy_authority={fmt_list(policy_sets.get('authority_policies', []))}")
        lines.append(f"policy_mode={fmt_list(policy_sets.get('mode_policies', []))}")
        lines.append(f"policy_debug={fmt_list(policy_sets.get('debug_policies', []))}")
        nodes = summary.get("topology_nodes", [])
        if nodes:
            for node_id in nodes:
                lines.append(f"topology_node={node_id}")
        output = "\n".join(lines) + "\n"
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0
    _print_json(summary)
    return 0


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list-templates")
    list_cmd.add_argument("--format", choices=["json", "text"], default="json")
    list_cmd.add_argument("--output")
    list_cmd.add_argument("--packs", action="append", default=[])
    list_cmd.set_defaults(func=cmd_list_templates)

    gen_cmd = sub.add_parser("generate")
    gen_cmd.add_argument("--template-id", required=True)
    gen_cmd.add_argument("--seed", type=int, default=0)
    gen_cmd.add_argument("--output")
    gen_cmd.add_argument("--policy-movement", action="append", default=[])
    gen_cmd.add_argument("--policy-authority", action="append", default=[])
    gen_cmd.add_argument("--policy-mode", action="append", default=[])
    gen_cmd.add_argument("--policy-debug", action="append", default=[])
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

    sum_cmd = sub.add_parser("summarize")
    sum_cmd.add_argument("--input", required=True)
    sum_cmd.add_argument("--format", choices=["json", "text"], default="json")
    sum_cmd.add_argument("--output")
    sum_cmd.set_defaults(func=cmd_summarize)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
