import argparse
import json
import os
import re
import uuid
from datetime import datetime


BUGREPORT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]+$")


def now_timestamp(deterministic):
    if deterministic or os.environ.get("OPS_DETERMINISTIC") == "1":
        return "2000-01-01T00:00:00Z"
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_list(values):
    return [value.strip() for value in (values or []) if value and value.strip()]


def parse_args():
    parser = argparse.ArgumentParser(description="Ingest clip/voice bug observations into data/logs/bugreports.")
    parser.add_argument("--bugreport-id", default="")
    parser.add_argument("--clip-path", default="")
    parser.add_argument("--voice-note-path", default="")
    parser.add_argument("--timestamp", action="append", default=[])
    parser.add_argument("--expected", required=True)
    parser.add_argument("--observed", required=True)
    parser.add_argument("--build-identity", required=True)
    parser.add_argument("--capability", action="append", default=[])
    parser.add_argument("--pack", action="append", default=[])
    parser.add_argument("--repro-step", action="append", default=[])
    parser.add_argument("--status", default="open")
    parser.add_argument("--regression-test", default="")
    parser.add_argument("--deferred-reason", default="")
    parser.add_argument("--out-root", default=os.path.join("data", "logs", "bugreports"))
    parser.add_argument("--deterministic", action="store_true")
    return parser.parse_args()


def parse_build_identity(raw):
    try:
        payload = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def main():
    args = parse_args()

    bugreport_id = args.bugreport_id.strip()
    if not bugreport_id:
        bugreport_id = "bugreport.{}".format(uuid.uuid4().hex)
    if BUGREPORT_ID_RE.match(bugreport_id) is None:
        raise SystemExit("invalid bugreport id: {}".format(bugreport_id))

    clip_path = args.clip_path.strip()
    voice_path = args.voice_note_path.strip()
    if not clip_path and not voice_path:
        raise SystemExit("clip-path or voice-note-path is required")

    build_identity = parse_build_identity(args.build_identity)
    if build_identity is None:
        raise SystemExit("build-identity must be a JSON object")

    payload = {
        "schema_id": "dominium.schema.bugreport_observation",
        "schema_version": "1.0.0",
        "record": {
            "bugreport_id": bugreport_id,
            "observed_behavior": args.observed.strip(),
            "expected_behavior": args.expected.strip(),
            "build_identity": build_identity,
            "capability_set": normalize_list(args.capability),
            "packs_enabled": normalize_list(args.pack),
            "created_at": now_timestamp(args.deterministic),
            "status": args.status.strip() or "open",
            "extensions": {},
        },
    }
    if clip_path:
        payload["record"]["clip_path"] = clip_path
    if voice_path:
        payload["record"]["voice_note_path"] = voice_path

    timestamps = normalize_list(args.timestamp)
    repro_steps = normalize_list(args.repro_step)
    if timestamps:
        payload["record"]["timestamps"] = timestamps
    if repro_steps:
        payload["record"]["reproduction_steps"] = repro_steps
    if args.regression_test.strip():
        payload["record"]["regression_test"] = args.regression_test.strip()
    if args.deferred_reason.strip():
        payload["record"]["deferred_reason"] = args.deferred_reason.strip()

    out_root = os.path.abspath(args.out_root)
    os.makedirs(out_root, exist_ok=True)
    out_path = os.path.join(out_root, "{}.json".format(bugreport_id))
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")

    print(json.dumps({
        "result": "ok",
        "bugreport_id": bugreport_id,
        "path": out_path.replace("\\", "/"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
