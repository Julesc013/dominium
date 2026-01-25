import copy
import json

from _common import compute_hash


SCHEMA_ID = "dominium.schema.world_definition"
SCHEMA_VERSION = 1

REFUSAL_INVALID = "WD-REFUSAL-INVALID"
REFUSAL_SCHEMA = "WD-REFUSAL-SCHEMA"
REFUSAL_CAPABILITY = "WD-REFUSAL-CAPABILITY"
REFUSAL_TEMPLATE = "WD-REFUSAL-TEMPLATE"


def _seed_from_params(params):
    seed = 0
    if params and isinstance(params, dict):
        seed = params.get("seed.primary", params.get("seed", 0))
    return seed


def _validate_seed(seed):
    if not isinstance(seed, int):
        return False
    if seed < 0 or seed > 0xFFFFFFFFFFFFFFFF:
        return False
    return True


def _make_refusal(code, message, details=None):
    payload = {
        "code": code,
        "message": message,
        "details": details or {}
    }
    return payload


def _make_topology_node(node_id, parent_id=None, trait_tags=None, frame_id=None):
    node = {"node_id": node_id}
    if parent_id:
        node["parent_refs"] = [{"node_id": parent_id}]
    if trait_tags:
        node["trait_tags"] = list(trait_tags)
    if frame_id:
        node["coord_frame_ref"] = {"frame_id": frame_id}
    return node


def _make_edge(parent_id, child_id):
    return {
        "parent_ref": {"node_id": parent_id},
        "child_ref": {"node_id": child_id}
    }


def _base_worlddef(template_id, template_version, seed, generator_source):
    worlddef_id = f"{template_id}.seed.{seed}"
    return {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "worlddef_id": worlddef_id,
        "topology": {
            "root_node_ref": {"node_id": "universe.root"},
            "nodes": [],
            "edges": []
        },
        "initial_fields": [],
        "policy_sets": {
            "movement_policies": [],
            "authority_policies": [],
            "mode_policies": [],
            "debug_policies": []
        },
        "spawn_spec": {
            "spawn_node_ref": {"node_id": "universe.root"},
            "coordinate_frame_ref": {"frame_id": "frame.universe.root"},
            "position": {"value": {"x": 0, "y": 0, "z": 0}},
            "orientation": {"value": {"yaw": 0, "pitch": 0, "roll": 0}}
        },
        "provenance": {
            "template_id": template_id,
            "template_version": template_version,
            "generator_source": generator_source,
            "seed": {"primary": seed},
            "template_params": {"seed.primary": seed}
        },
        "extensions": {}
    }


def generate_empty_universe(params):
    seed = _seed_from_params(params)
    if not _validate_seed(seed):
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_TEMPLATE,
                                         "invalid seed for template",
                                         {"template_id": "builtin.empty_universe"})}
    worlddef = _base_worlddef("builtin.empty_universe", "1.0.0", seed, "built_in")
    worlddef["topology"]["nodes"].append(
        _make_topology_node("universe.root", None, ["topology.universe"], "frame.universe.root")
    )
    return {"ok": True, "world_definition": worlddef}


def generate_minimal_system(params):
    seed = _seed_from_params(params)
    if not _validate_seed(seed):
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_TEMPLATE,
                                         "invalid seed for template",
                                         {"template_id": "builtin.minimal_system"})}
    worlddef = _base_worlddef("builtin.minimal_system", "1.0.0", seed, "built_in")
    nodes = worlddef["topology"]["nodes"]
    edges = worlddef["topology"]["edges"]
    nodes.append(_make_topology_node("universe.root", None, ["topology.universe"], "frame.universe.root"))
    nodes.append(_make_topology_node("system.minimal", "universe.root", ["topology.system"], "frame.system.minimal"))
    nodes.append(_make_topology_node("body.minimal.primary", "system.minimal",
                                     ["topology.body", "body.sphere"], "frame.body.minimal.primary"))
    edges.append(_make_edge("universe.root", "system.minimal"))
    edges.append(_make_edge("system.minimal", "body.minimal.primary"))
    worlddef["spawn_spec"]["spawn_node_ref"] = {"node_id": "body.minimal.primary"}
    worlddef["spawn_spec"]["coordinate_frame_ref"] = {"frame_id": "frame.body.minimal.primary"}
    return {"ok": True, "world_definition": worlddef}


def generate_realistic_test_universe(params):
    seed = _seed_from_params(params)
    if not _validate_seed(seed):
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_TEMPLATE,
                                         "invalid seed for template",
                                         {"template_id": "builtin.realistic_test_universe"})}
    worlddef = _base_worlddef("builtin.realistic_test_universe", "1.0.0", seed, "built_in")
    nodes = worlddef["topology"]["nodes"]
    edges = worlddef["topology"]["edges"]
    nodes.append(_make_topology_node("universe.root", None, ["topology.universe"], "frame.universe.root"))
    nodes.append(_make_topology_node("galaxy.test", "universe.root", ["topology.galaxy"], "frame.galaxy.test"))
    nodes.append(_make_topology_node("system.test", "galaxy.test", ["topology.system"], "frame.system.test"))
    edges.append(_make_edge("universe.root", "galaxy.test"))
    edges.append(_make_edge("galaxy.test", "system.test"))

    bodies = [
        ("body.sun", ["body.sphere", "body.star"]),
        ("body.mercury", ["body.sphere", "body.rocky"]),
        ("body.venus", ["body.sphere", "body.rocky"]),
        ("body.earth", ["body.sphere", "body.rocky", "body.spawn"]),
        ("body.mars", ["body.sphere", "body.rocky"]),
        ("body.jupiter", ["body.sphere", "body.gas_giant"]),
        ("body.saturn", ["body.sphere", "body.gas_giant"]),
        ("body.uranus", ["body.sphere", "body.gas_giant"]),
        ("body.neptune", ["body.sphere", "body.gas_giant"])
    ]
    for body_id, tags in bodies:
        frame_id = f"frame.{body_id}"
        nodes.append(_make_topology_node(body_id, "system.test", ["topology.body"] + tags, frame_id))
        edges.append(_make_edge("system.test", body_id))
    worlddef["spawn_spec"]["spawn_node_ref"] = {"node_id": "body.earth"}
    worlddef["spawn_spec"]["coordinate_frame_ref"] = {"frame_id": "frame.body.earth"}
    return {"ok": True, "world_definition": worlddef}


BUILTIN_TEMPLATES = {
    "builtin.empty_universe": generate_empty_universe,
    "builtin.minimal_system": generate_minimal_system,
    "builtin.realistic_test_universe": generate_realistic_test_universe
}


def list_templates():
    templates = []
    for template_id in sorted(BUILTIN_TEMPLATES.keys()):
        if template_id == "builtin.empty_universe":
            desc = "Topology root only; valid but inert."
            guarantees = [
                "one topology root node",
                "no bodies, surfaces, or patches",
                "spawn resolves to root node"
            ]
        elif template_id == "builtin.minimal_system":
            desc = "One system and one body; spawn possible."
            guarantees = [
                "universe to system to body topology",
                "one body tagged as sphere",
                "spawn resolves to body node"
            ]
        else:
            desc = "Labeled test universe with spheres; spawn at Earth label."
            guarantees = [
                "universe to galaxy to system topology",
                "labeled star, rocky bodies, gas giants (spheres)",
                "spawn resolves to Earth-labeled body"
            ]
        templates.append({
            "template_id": template_id,
            "version": "1.0.0",
            "description": desc,
            "parameter_schema": {
                "seed.primary": "u64"
            },
            "required_capabilities": [],
            "output_guarantees": guarantees,
            "refusal_conditions": ["seed outside [0, 2^64-1]"]
        })
    return templates


def run_template(template_id, params=None):
    fn = BUILTIN_TEMPLATES.get(template_id)
    if not fn:
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_TEMPLATE,
                                         "template not found",
                                         {"template_id": template_id})}
    return fn(params or {})


def round_trip_json(payload):
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return json.loads(encoded)


def normalize_worlddef(payload, strip_extensions=False):
    data = copy.deepcopy(payload)
    if strip_extensions:
        _strip_extensions(data)
    return round_trip_json(data)


def _strip_extensions(value):
    if isinstance(value, dict):
        if "extensions" in value:
            value.pop("extensions", None)
        for key in list(value.keys()):
            _strip_extensions(value[key])
    elif isinstance(value, list):
        for item in value:
            _strip_extensions(item)


def worlddef_hash(payload, strip_extensions=False):
    normalized = normalize_worlddef(payload, strip_extensions=strip_extensions)
    return compute_hash(normalized)


def diff_worlddefs(left, right, strip_extensions=False):
    left_norm = normalize_worlddef(left, strip_extensions=strip_extensions)
    right_norm = normalize_worlddef(right, strip_extensions=strip_extensions)
    if left_norm == right_norm:
        return []
    return ["world_definition_mismatch"]


def validate_world_definition(payload, available_capabilities=None):
    if not isinstance(payload, dict):
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_INVALID,
                                         "world definition must be an object",
                                         {})}
    schema_version = payload.get("schema_version")
    if schema_version is None:
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_INVALID,
                                         "schema_version missing",
                                         {})}
    if not isinstance(schema_version, int):
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_SCHEMA,
                                         "schema_version must be integer",
                                         {"schema_version": schema_version})}
    if schema_version != SCHEMA_VERSION:
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_SCHEMA,
                                         "unsupported schema_version",
                                         {"schema_version": schema_version})}
    topology = payload.get("topology")
    if not isinstance(topology, dict):
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_INVALID,
                                         "missing topology",
                                         {})}
    nodes = topology.get("nodes", [])
    if not isinstance(nodes, list) or not nodes:
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_INVALID,
                                         "topology nodes missing",
                                         {})}
    root_ref = topology.get("root_node_ref", {})
    root_id = root_ref.get("node_id")
    node_ids = set()
    for node in nodes:
        if isinstance(node, dict) and "node_id" in node:
            node_ids.add(node["node_id"])
    if root_id not in node_ids:
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_INVALID,
                                         "root node missing",
                                         {"root_node_id": root_id})}
    spawn = payload.get("spawn_spec", {})
    spawn_node = spawn.get("spawn_node_ref", {}).get("node_id")
    if spawn_node not in node_ids:
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_INVALID,
                                         "spawn node missing",
                                         {"spawn_node_id": spawn_node})}
    if "policy_sets" not in payload:
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_INVALID,
                                         "policy_sets missing",
                                         {})}
    if "provenance" not in payload:
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_INVALID,
                                         "provenance missing",
                                         {})}
    if "extensions" not in payload:
        return {"ok": False,
                "refusal": _make_refusal(REFUSAL_INVALID,
                                         "extensions missing",
                                         {})}
    required_caps = payload.get("capability_expectations", [])
    if required_caps:
        available = set(available_capabilities or [])
        for cap in required_caps:
            if isinstance(cap, dict):
                cap_id = cap.get("capability_id")
            else:
                cap_id = cap
            if cap_id and cap_id not in available:
                return {"ok": False,
                        "refusal": _make_refusal(REFUSAL_CAPABILITY,
                                                 "missing required capability",
                                                 {"capability_id": cap_id})}
    return {"ok": True}
