import argparse
import json
import os
import re
import sys


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def require(condition, message):
    if not condition:
        sys.stderr.write("FAIL: {}\n".format(message))
        return False
    return True


def strip_comments_and_strings(text):
    text = re.sub(r"/\\*.*?\\*/", "", text, flags=re.S)
    text = re.sub(r"//.*", "", text)
    text = re.sub(r"\"(?:\\\\.|[^\"\\\\])*\"", "\"\"", text)
    return text


def extract_function(text, name):
    idx = text.find(name)
    if idx == -1:
        return None
    brace = text.find("{", idx)
    if brace == -1:
        return None
    depth = 0
    for i in range(brace, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[brace : i + 1]
    return None


def extract_array(text, key):
    idx = text.find(key)
    if idx == -1:
        return ""
    start = text.find("[", idx)
    if start == -1:
        return ""
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i]
    return ""


def check_move_cost(body):
    stripped = strip_comments_and_strings(body)
    if re.search(r"\bfor\s*\(", stripped) or re.search(r"\bwhile\s*\(", stripped):
        return False, "dom_client_shell_move contains loop (navigation cost scales)"
    forbidden = [
        "worlddef_json",
        "worlddef_len",
        "dom_shell_world_has_node",
        "dom_shell_json_",
    ]
    for token in forbidden:
        if token in stripped:
            return False, "dom_client_shell_move touches topology ({})".format(token)
    return True, ""


def check_renderer_no_worlddef(text):
    forbidden = ["worlddef_json", "worlddef_len"]
    for token in forbidden:
        if token in text:
            return False, "renderer references worlddef payload ({})".format(token)
    return True, ""


def check_template_tags(text):
    required_tags = [
        "topology.universe",
        "topology.galaxy",
        "topology.system",
        "topology.body",
    ]
    ok = True
    for tag in required_tags:
        ok = ok and require(tag in text, "template missing tag {}".format(tag))
    ok = ok and require("body.earth" in text, "template missing body.earth")
    nodes_block = extract_array(text, "\"nodes\"")
    edges_block = extract_array(text, "\"edges\"")
    node_count = 0
    edge_count = 0
    try:
        node_count = len(json.loads("[" + nodes_block + "]")) if nodes_block.strip() else 0
    except Exception as exc:
        ok = False
        sys.stderr.write("FAIL: nodes block not valid JSON ({})\n".format(exc))
    try:
        edge_count = len(json.loads("[" + edges_block + "]")) if edges_block.strip() else 0
    except Exception as exc:
        ok = False
        sys.stderr.write("FAIL: edges block not valid JSON ({})\n".format(exc))
    ok = ok and require(node_count >= 5, "template node count too small")
    ok = ok and require(node_count <= 6, "template node count too large")
    ok = ok and require(edge_count >= 4, "template edge count too small")
    return ok


def main():
    parser = argparse.ArgumentParser(description="Exploration baseline scaling guard tests.")
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    shell_path = os.path.join(repo_root, "client", "shell", "client_shell.c")
    ui_path = os.path.join(repo_root, "client", "app", "main_client.c")
    template_path = os.path.join(
        repo_root, "data", "world", "templates", "exploration_baseline.worlddef.json"
    )

    ok = True
    ok = ok and require(os.path.isfile(shell_path), "client_shell.c missing")
    ok = ok and require(os.path.isfile(ui_path), "main_client.c missing")
    ok = ok and require(os.path.isfile(template_path), "template missing")
    if not ok:
        return 1

    shell_text = read_text(shell_path)
    body = extract_function(shell_text, "dom_client_shell_move")
    ok = ok and require(body is not None, "dom_client_shell_move not found")
    if body:
        ok_move, msg = check_move_cost(body)
        ok = ok and require(ok_move, msg)

    ui_text = read_text(ui_path)
    ok_ui, msg = check_renderer_no_worlddef(ui_text)
    ok = ok and require(ok_ui, msg)

    template_text = read_text(template_path)
    ok = ok and check_template_tags(template_text)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
