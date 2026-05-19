#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
MAX_LIST = 256
REQUIRED_FILES = [
    "fields.json",
    "knowledge_artifacts.json",
    "measurement_artifacts.json",
    "provenance_records.json",
    "refinement_plans.json",
    "worldgen_models.json",
]


def load_json(path, errors):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        errors.append(f"{path}: failed to parse json: {exc}")
        return None


def collect_values(value, key):
    if isinstance(value, dict):
        for current_key, current_value in value.items():
            if current_key == key and isinstance(current_value, str):
                yield current_value
            yield from collect_values(current_value, key)
    elif isinstance(value, list):
        for item in value:
            yield from collect_values(item, key)


def require_keys(obj, keys, path, errors):
    for key in keys:
        if key not in obj:
            errors.append(f"{path}: missing required field '{key}'")


def check_version(doc, path, errors):
    schema_version = doc.get("schema_version")
    if not schema_version or not VERSION_RE.match(schema_version):
        errors.append(f"{path}: invalid schema_version '{schema_version}'")


def check_records(doc, path, errors):
    records = doc.get("records")
    if not isinstance(records, list) or not records:
        errors.append(f"{path}: records must be a non-empty list")
        return []
    if len(records) > MAX_LIST:
        errors.append(f"{path}: records exceeds max size {MAX_LIST}")
    return records


def validate_real_worldgen_domain(repo_root, domain_name, display_name, min_field_count):
    root = os.path.join(repo_root, "content", "domains", "worldgen", "real", domain_name)
    errors = []

    if not os.path.isdir(root):
        errors.append(f"{root}: missing canonical worldgen real domain directory")
    if os.path.isdir(os.path.join(root, "content")):
        errors.append(f"{os.path.join(root, 'content')}: nested content/ wrapper is not canonical")

    docs = {}
    for filename in REQUIRED_FILES:
        path = os.path.join(root, filename)
        if not os.path.exists(path):
            errors.append(f"{path}: missing required canonical worldgen file")
            continue
        doc = load_json(path, errors)
        if doc is not None:
            docs[filename] = doc

    if errors:
        for err in errors:
            print(err)
        return 1

    records_by_file = {}
    for filename, doc in docs.items():
        path = os.path.join(root, filename)
        check_version(doc, path, errors)
        records_by_file[filename] = check_records(doc, path, errors)

    token = f"worldgen.real.{domain_name}"
    id_prefix = f"org.dominium.worldgen.real.{domain_name}."
    provenance_prefix = f"prov.org.dominium.worldgen.realdata.{domain_name}."

    provenance_ids = set()
    for record in records_by_file["provenance_records.json"]:
        require_keys(record, ["knowledge_artifact_id", "knowledge_domain_tag"], "provenance_records.json", errors)
        provenance_id = record.get("knowledge_artifact_id")
        if provenance_id:
            provenance_ids.add(provenance_id)
            if not provenance_id.startswith(provenance_prefix):
                errors.append(f"provenance_records.json: unexpected provenance id '{provenance_id}'")
        if token not in record.get("knowledge_domain_tag", ""):
            errors.append("provenance_records.json: provenance domain tag does not match canonical domain")

    field_ids = set()
    for record in records_by_file["fields.json"]:
        require_keys(
            record,
            ["field_id", "field_type", "units", "resolution", "representation", "knowledge_state", "provenance_ref"],
            "fields.json",
            errors,
        )
        field_id = record.get("field_id")
        if field_id in field_ids:
            errors.append(f"fields.json: duplicate field_id '{field_id}'")
        if field_id:
            field_ids.add(field_id)
            if not field_id.startswith(f"{id_prefix}field."):
                errors.append(f"fields.json: field_id '{field_id}' does not use canonical domain prefix")
        if not isinstance(record.get("units"), list):
            errors.append(f"fields.json: field '{field_id}' units must be a list")
        if not isinstance(record.get("representation"), list) or not record.get("representation"):
            errors.append(f"fields.json: field '{field_id}' representation must be a non-empty list")

    if len(field_ids) < min_field_count:
        errors.append(f"fields.json: expected at least {min_field_count} {display_name} field records")

    model_ids = set()
    for record in records_by_file["worldgen_models.json"]:
        require_keys(record, ["model_id", "model_family", "supported_fields", "provenance_ref"], "worldgen_models.json", errors)
        model_id = record.get("model_id")
        if model_id in model_ids:
            errors.append(f"worldgen_models.json: duplicate model_id '{model_id}'")
        if model_id:
            model_ids.add(model_id)
            if not model_id.startswith(f"{id_prefix}model."):
                errors.append(f"worldgen_models.json: model_id '{model_id}' does not use canonical domain prefix")
        supported_fields = set(collect_values(record.get("supported_fields", []), "field_id"))
        missing_fields = sorted(supported_fields - field_ids)
        if missing_fields:
            errors.append(f"worldgen_models.json: model '{model_id}' references unknown fields {missing_fields}")

    for record in records_by_file["refinement_plans.json"]:
        require_keys(record, ["plan_id", "layers", "provenance_ref"], "refinement_plans.json", errors)
        plan_id = record.get("plan_id")
        if plan_id and not plan_id.startswith(f"{id_prefix}plan."):
            errors.append(f"refinement_plans.json: plan_id '{plan_id}' does not use canonical domain prefix")
        layers = record.get("layers", [])
        if not isinstance(layers, list) or not layers:
            errors.append(f"refinement_plans.json: plan '{plan_id}' layers must be a non-empty list")
            continue
        order_indices = []
        for layer in layers:
            layer_id = layer.get("layer_id")
            order_index = layer.get("order_index")
            if not isinstance(order_index, int):
                errors.append(f"refinement_plans.json: layer '{layer_id}' order_index must be an int")
            else:
                order_indices.append(order_index)
            missing_fields = sorted(set(collect_values(layer.get("field_refs", []), "field_id")) - field_ids)
            if missing_fields:
                errors.append(f"refinement_plans.json: layer '{layer_id}' references unknown fields {missing_fields}")
            missing_models = sorted(set(collect_values(layer.get("model_refs", []), "model_id")) - model_ids)
            if missing_models:
                errors.append(f"refinement_plans.json: layer '{layer_id}' references unknown models {missing_models}")
        if order_indices and order_indices != sorted(order_indices):
            errors.append(f"refinement_plans.json: plan '{plan_id}' layers must be ordered by order_index")

    for filename, id_key in [
        ("knowledge_artifacts.json", "knowledge_artifact_id"),
        ("measurement_artifacts.json", "measurement_artifact_id"),
    ]:
        for record in records_by_file[filename]:
            require_keys(record, [id_key, "provenance_ref"], filename, errors)
            record_id = record.get(id_key, "")
            if domain_name not in record_id:
                errors.append(f"{filename}: {id_key} '{record_id}' does not identify {display_name}")

    for filename, records in records_by_file.items():
        if filename == "provenance_records.json":
            continue
        for provenance_id in collect_values(records, "provenance_id"):
            if provenance_id not in provenance_ids:
                errors.append(f"{filename}: provenance_id '{provenance_id}' is not declared")

    if errors:
        for err in errors:
            print(err)
        return 1

    print(f"{display_name} canonical worldgen data validation passed")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    return validate_real_worldgen_domain(
        os.path.abspath(args.repo_root),
        domain_name="earth",
        display_name="Earth",
        min_field_count=13,
    )


if __name__ == "__main__":
    sys.exit(main())
