import hashlib


SCENARIO_HEADER = "DOMINIUM_SCENARIO_V1"
VARIANT_HEADER = "DOMINIUM_VARIANT_V1"
REPLAY_HEADER = "DOMINIUM_REPLAY_V1"
SAVE_HEADER = "DOMINIUM_SAVE_V1"


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return [line.rstrip("\r\n") for line in handle]


def iter_content_lines(lines):
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith(";"):
            continue
        yield line


def parse_variant_line(line):
    if not isinstance(line, str) or not line.startswith("variant "):
        return None
    tokens = line[len("variant ") :].split()
    data = {"scope": "world", "system_id": "", "variant_id": ""}
    for token in tokens:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        if key == "scope":
            data["scope"] = value or "world"
        elif key == "system":
            data["system_id"] = value
        elif key == "id":
            data["variant_id"] = value
    if not data["system_id"] or not data["variant_id"]:
        return None
    return data


def parse_scenario(path):
    lines = read_lines(path)
    content = list(iter_content_lines(lines))
    if not content or content[0] != SCENARIO_HEADER:
        raise ValueError("scenario header mismatch")
    data = {
        "scenario_id": "",
        "scenario_version": "",
        "world_template": "",
        "world_seed": "",
        "policies": {},
        "lockfile_id": "",
        "lockfile_hash": "",
        "variants": [],
        "fields": [],
        "agents": [],
    }
    in_variants = False
    in_fields = False
    in_agents = False
    for line in content[1:]:
        if line == "variants_begin":
            in_variants = True
            continue
        if line == "variants_end":
            in_variants = False
            continue
        if line == "fields_begin":
            in_fields = True
            continue
        if line == "fields_end":
            in_fields = False
            continue
        if line == "agents_begin":
            in_agents = True
            continue
        if line == "agents_end":
            in_agents = False
            continue
        if in_variants:
            entry = parse_variant_line(line)
            if entry:
                data["variants"].append(entry)
            continue
        if in_fields:
            if not line.startswith("field "):
                continue
            field_tokens = line[len("field ") :].split()
            field = {"field_id": "", "value": "", "known": ""}
            for token in field_tokens:
                if "=" not in token:
                    continue
                key, value = token.split("=", 1)
                if key in ("id", "field_id"):
                    field["field_id"] = value
                elif key == "value":
                    field["value"] = value
                elif key == "known":
                    field["known"] = value
            data["fields"].append(field)
            continue
        if in_agents:
            if not line.startswith("agent "):
                continue
            agent_tokens = line[len("agent ") :].split()
            agent = {
                "agent_id": "",
                "caps": "",
                "auth": "",
                "know": "",
                "resource": "",
                "dest": "",
                "threat": "",
            }
            for token in agent_tokens:
                if "=" not in token:
                    continue
                key, value = token.split("=", 1)
                if key == "id":
                    agent["agent_id"] = value
                elif key == "caps":
                    agent["caps"] = value
                elif key in ("auth", "authority"):
                    agent["auth"] = value
                elif key in ("know", "knowledge"):
                    agent["know"] = value
                elif key == "resource":
                    agent["resource"] = value
                elif key in ("dest", "destination"):
                    agent["dest"] = value
                elif key == "threat":
                    agent["threat"] = value
            data["agents"].append(agent)
            continue
        if line.startswith("scenario_id="):
            data["scenario_id"] = line.split("=", 1)[1]
        elif line.startswith("scenario_version="):
            data["scenario_version"] = line.split("=", 1)[1]
        elif line.startswith("world_template="):
            data["world_template"] = line.split("=", 1)[1]
        elif line.startswith("world_seed="):
            data["world_seed"] = line.split("=", 1)[1]
        elif line.startswith("policy."):
            key, value = line.split("=", 1)
            data["policies"][key] = value
        elif line.startswith("lockfile_id="):
            data["lockfile_id"] = line.split("=", 1)[1]
        elif line.startswith("lockfile_hash="):
            data["lockfile_hash"] = line.split("=", 1)[1]
    return data


def parse_variant_file(path):
    lines = read_lines(path)
    content = list(iter_content_lines(lines))
    if not content or content[0] != VARIANT_HEADER:
        raise ValueError("variant header mismatch")
    data = {
        "variant_id": "",
        "variant_version": "",
        "world_seed": "",
        "policies": {},
        "lockfile_id": "",
        "lockfile_hash": "",
        "variants": [],
    }
    in_variants = False
    for line in content[1:]:
        if line == "variants_begin":
            in_variants = True
            continue
        if line == "variants_end":
            in_variants = False
            continue
        if in_variants:
            entry = parse_variant_line(line)
            if entry:
                data["variants"].append(entry)
            continue
        if line.startswith("variant_id="):
            data["variant_id"] = line.split("=", 1)[1]
        elif line.startswith("variant_version="):
            data["variant_version"] = line.split("=", 1)[1]
        elif line.startswith("world_seed=") or line.startswith("seed="):
            data["world_seed"] = line.split("=", 1)[1]
        elif line.startswith("policy."):
            key, value = line.split("=", 1)
            data["policies"][key] = value
        elif line.startswith("lockfile_id="):
            data["lockfile_id"] = line.split("=", 1)[1]
        elif line.startswith("lockfile_hash="):
            data["lockfile_hash"] = line.split("=", 1)[1]
    return data


def parse_replay(path):
    lines = read_lines(path)
    if not lines:
        raise ValueError("replay empty")
    header = ""
    start_index = 0
    if lines[0] in (SAVE_HEADER, REPLAY_HEADER):
        header = lines[0]
        start_index = 1
    data = {
        "header": header,
        "format": "save" if header == SAVE_HEADER else "replay",
        "meta": {
            "scenario_id": "",
            "scenario_version": "",
            "scenario_variants": [],
            "lockfile_id": "",
            "lockfile_hash": "",
        },
        "variants": [],
        "events": [],
    }
    in_meta = False
    in_variants = False
    in_events = False
    saw_events_section = False
    for raw in lines[start_index:]:
        line = raw.strip()
        if line == "meta_begin":
            in_meta = True
            continue
        if line == "meta_end":
            in_meta = False
            continue
        if line == "variants_begin":
            in_variants = True
            continue
        if line == "variants_end":
            in_variants = False
            continue
        if line == "events_begin":
            in_events = True
            saw_events_section = True
            continue
        if line == "events_end":
            in_events = False
            continue
        if in_meta:
            if line.startswith("scenario_id="):
                data["meta"]["scenario_id"] = line.split("=", 1)[1]
            elif line.startswith("scenario_version="):
                data["meta"]["scenario_version"] = line.split("=", 1)[1]
            elif line.startswith("scenario_variants="):
                csv = line.split("=", 1)[1]
                data["meta"]["scenario_variants"] = [v for v in csv.split(",") if v]
            elif line.startswith("lockfile_id="):
                data["meta"]["lockfile_id"] = line.split("=", 1)[1]
            elif line.startswith("lockfile_hash="):
                data["meta"]["lockfile_hash"] = line.split("=", 1)[1]
            continue
        if in_variants:
            entry = parse_variant_line(line)
            if entry:
                data["variants"].append(entry)
            continue
        if not line:
            continue
        if saw_events_section:
            if in_events:
                data["events"].append(line)
        else:
            data["events"].append(line)
    if not data["events"]:
        raise ValueError("replay has no events")
    return data


def parse_event_line(line):
    tokens = line.split()
    seq = None
    name = ""
    details = {}
    raw_detail = ""
    for token in tokens:
        if token.startswith("event_seq="):
            seq = token.split("=", 1)[1]
        elif token.startswith("event="):
            name = token.split("=", 1)[1]
        else:
            raw_detail = raw_detail + (" " if raw_detail else "") + token
            if "=" in token:
                key, value = token.split("=", 1)
                details[key] = value
    return {"seq": seq, "name": name, "detail": raw_detail, "detail_map": details}


def event_domain(event_name, detail_map):
    domain = detail_map.get("domain", "")
    if domain in ("macro", "micro", "meso"):
        return domain
    lowered = event_name.lower()
    if ".macro" in lowered or lowered.startswith("macro."):
        return "macro"
    if ".micro" in lowered or lowered.startswith("micro."):
        return "micro"
    if ".meso" in lowered or lowered.startswith("meso."):
        return "meso"
    return "unknown"


def hash_events(events):
    digest = hashlib.sha256("\n".join(events).encode("utf-8")).hexdigest()
    return digest
