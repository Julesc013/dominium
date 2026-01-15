import os
import struct


def tlv(tag, payload):
    return struct.pack("<II", tag, len(payload)) + payload


def kv_u32(tag, value):
    return (tag, struct.pack("<I", value))


def kv_u16(tag, value):
    return (tag, struct.pack("<H", value))


def kv_i32(tag, value):
    return (tag, struct.pack("<i", value))


def kv_q16(tag, value):
    raw = int(round(value * 65536.0))
    return (tag, struct.pack("<i", raw))


def kv_q32(tag, value):
    raw = int(round(value * float(1 << 32)))
    return (tag, struct.pack("<q", raw))


def kv_str(tag, text):
    data = text.encode("utf-8") + b"\0"
    return (tag, data)


def kv_blob(tag, blob):
    return (tag, blob)


def build_kv(fields):
    fields_sorted = sorted(fields, key=lambda f: (f[0], f[1]))
    return b"".join(tlv(tag, payload) for (tag, payload) in fields_sorted)


def extract_u32_field(kv_payload, wanted_tag=0x01):
    off = 0
    while off + 8 <= len(kv_payload):
        tag, ln = struct.unpack_from("<II", kv_payload, off)
        off += 8
        payload = kv_payload[off : off + ln]
        off += ln
        if tag == wanted_tag and ln == 4:
            return struct.unpack("<I", payload)[0]
    return 0


def build_stream(records):
    def sort_key(rec):
        schema_id, payload = rec
        return (schema_id, extract_u32_field(payload, 0x01), payload)

    records_sorted = sorted(records, key=sort_key)
    return b"".join(tlv(schema_id, payload) for (schema_id, payload) in records_sorted)


SCHEMA_MATERIAL = 0x0101
SCHEMA_ITEM = 0x0102
SCHEMA_PROCESS = 0x0104
SCHEMA_STRUCTURE = 0x0106
SCHEMA_SPLINE = 0x0108
SCHEMA_BLUEPRINT = 0x010B
SCHEMA_RESEARCH = 0x010C
SCHEMA_POLICY_RULE = 0x010E
SCHEMA_PACK = 0x0201
SCHEMA_MOD = 0x0202

F_ID = 0x01

F_MAT_NAME = 0x02
F_ITEM_NAME = 0x02
F_PROC_NAME = 0x02
F_STRUCT_NAME = 0x02
F_SPLINE_NAME = 0x02
F_BP_NAME = 0x02
F_RESEARCH_NAME = 0x02
F_POLICY_NAME = 0x02

F_ITEM_MATERIAL = 0x03
F_PROC_BASE_DURATION = 0x05

F_PROC_IO_TERM = 0x06
F_PROC_IO_KIND = 0x01
F_PROC_IO_ITEM_ID = 0x02
F_PROC_IO_RATE = 0x03
F_PROC_IO_FLAGS = 0x04

F_STRUCT_LAYOUT = 0x04
F_STRUCT_IO = 0x05

F_SPLINE_TYPE = 0x05
F_SPLINE_FLAGS = 0x06
F_SPLINE_BASE_SPEED = 0x07
F_SPLINE_MAX_GRADE = 0x08
F_SPLINE_CAPACITY = 0x09

F_BP_PAYLOAD = 0x04
BP_REC_STRUCT = 0x01

F_RESEARCH_PREREQ_ID = 0x04

F_POLICY_SCOPE = 0x04
F_POLICY_EFFECT = 0x05
F_POLICY_CONDITIONS = 0x06

POLICY_SCOPE_SUBJECT_KIND = 0x10
POLICY_EFFECT_ALLOWED = 0x30

F_PACK_ID = 0x01
F_PACK_VERSION = 0x02
F_PACK_NAME = 0x03
F_PACK_DESCRIPTION = 0x04
F_PACK_CONTENT = 0x05

F_MOD_ID = 0x01
F_MOD_VERSION = 0x02
F_MOD_NAME = 0x03
F_MOD_DESCRIPTION = 0x04
F_MOD_CONTENT = 0x06

STRUCT_LAYOUT_W = 0x01
STRUCT_LAYOUT_H = 0x02
STRUCT_LAYOUT_ANCHOR_Z = 0x03

STRUCT_IO_PORT = 0x10
STRUCT_PORT_KIND = 0x01
STRUCT_PORT_POS_X = 0x02
STRUCT_PORT_POS_Y = 0x03
STRUCT_PORT_DIR_Z = 0x04

STRUCT_PORT_ITEM_IN = 3
STRUCT_PORT_ITEM_OUT = 2

SPLINE_TYPE_ITEM = 1
PROC_IO_INPUT_ITEM = 1
PROC_IO_OUTPUT_ITEM = 2


def demo_blueprint_stream(struct_id_a, struct_id_b):
    payload = build_kv(
        [
            kv_u32(F_ID, 6001),
            kv_str(F_BP_NAME, "Demo Blueprint"),
            kv_blob(
                F_BP_PAYLOAD,
                tlv(BP_REC_STRUCT, struct.pack("<I", struct_id_a))
                + tlv(BP_REC_STRUCT, struct.pack("<I", struct_id_b)),
            ),
        ]
    )
    return build_stream([(SCHEMA_BLUEPRINT, payload)])


def demo_research_stream():
    logistics = build_kv([kv_u32(F_ID, 7001), kv_str(F_RESEARCH_NAME, "Logistics I")])
    automation = build_kv(
        [
            kv_u32(F_ID, 7002),
            kv_str(F_RESEARCH_NAME, "Automation I"),
            kv_u32(F_RESEARCH_PREREQ_ID, 7001),
        ]
    )
    return build_stream([(SCHEMA_RESEARCH, logistics), (SCHEMA_RESEARCH, automation)])


def demo_policy_stream():
    scope = build_kv([kv_u32(POLICY_SCOPE_SUBJECT_KIND, 0)])
    effect = build_kv([kv_u32(POLICY_EFFECT_ALLOWED, 1)])
    payload = build_kv(
        [
            kv_u32(F_ID, 8001),
            kv_str(F_POLICY_NAME, "Demo Policy (Allow)"),
            kv_blob(F_POLICY_SCOPE, scope),
            kv_blob(F_POLICY_EFFECT, effect),
            kv_blob(F_POLICY_CONDITIONS, b""),
        ]
    )
    return build_stream([(SCHEMA_POLICY_RULE, payload)])


def demo_material_item_stream():
    mat = build_kv([kv_u32(F_ID, 1001), kv_str(F_MAT_NAME, "Iron")])
    ore = build_kv([kv_u32(F_ID, 2001), kv_str(F_ITEM_NAME, "Ore"), kv_u32(F_ITEM_MATERIAL, 1001)])
    plate = build_kv([kv_u32(F_ID, 2002), kv_str(F_ITEM_NAME, "Plate"), kv_u32(F_ITEM_MATERIAL, 1001)])
    widget = build_kv([kv_u32(F_ID, 2003), kv_str(F_ITEM_NAME, "Widget"), kv_u32(F_ITEM_MATERIAL, 1001)])
    return build_stream([(SCHEMA_MATERIAL, mat), (SCHEMA_ITEM, ore), (SCHEMA_ITEM, plate), (SCHEMA_ITEM, widget)])


def demo_process_stream():
    def io_term(kind, item_id, rate):
        return tlv(
            F_PROC_IO_TERM,
            build_kv(
                [
                    kv_u16(F_PROC_IO_KIND, kind),
                    kv_u32(F_PROC_IO_ITEM_ID, item_id),
                    kv_q16(F_PROC_IO_RATE, rate),
                    kv_u16(F_PROC_IO_FLAGS, 0),
                ]
            ),
        )

    p1 = build_kv(
        [
            kv_u32(F_ID, 3001),
            kv_str(F_PROC_NAME, "Ore \u2192 Plate"),
            kv_q16(F_PROC_BASE_DURATION, 2.0),
        ]
    ) + io_term(PROC_IO_INPUT_ITEM, 2001, 1.0) + io_term(PROC_IO_OUTPUT_ITEM, 2002, 1.0)

    p2 = build_kv(
        [
            kv_u32(F_ID, 3002),
            kv_str(F_PROC_NAME, "Plate \u2192 Widget"),
            kv_q16(F_PROC_BASE_DURATION, 3.0),
        ]
    ) + io_term(PROC_IO_INPUT_ITEM, 2002, 1.0) + io_term(PROC_IO_OUTPUT_ITEM, 2003, 1.0)

    return build_stream([(SCHEMA_PROCESS, p1), (SCHEMA_PROCESS, p2)])


def demo_spline_stream():
    payload = build_kv(
        [
            kv_u32(F_ID, 4001),
            kv_str(F_SPLINE_NAME, "Belt Mk1"),
            kv_u16(F_SPLINE_TYPE, SPLINE_TYPE_ITEM),
            kv_u16(F_SPLINE_FLAGS, 0),
            kv_q16(F_SPLINE_BASE_SPEED, 2.0),
            kv_q16(F_SPLINE_MAX_GRADE, 1.0),
            kv_q16(F_SPLINE_CAPACITY, 8.0),
        ]
    )
    return build_stream([(SCHEMA_SPLINE, payload)])


def demo_structure_stream():
    layout = build_kv(
        [
            kv_u32(STRUCT_LAYOUT_W, 2),
            kv_u32(STRUCT_LAYOUT_H, 1),
            kv_q16(STRUCT_LAYOUT_ANCHOR_Z, 0.0),
        ]
    )

    port_in = build_kv(
        [
            kv_u32(STRUCT_PORT_KIND, STRUCT_PORT_ITEM_IN),
            kv_i32(STRUCT_PORT_POS_X, -1),
            kv_i32(STRUCT_PORT_POS_Y, 0),
            kv_i32(STRUCT_PORT_DIR_Z, 0),
        ]
    )
    port_out = build_kv(
        [
            kv_u32(STRUCT_PORT_KIND, STRUCT_PORT_ITEM_OUT),
            kv_i32(STRUCT_PORT_POS_X, 1),
            kv_i32(STRUCT_PORT_POS_Y, 0),
            kv_i32(STRUCT_PORT_DIR_Z, 0),
        ]
    )
    io = tlv(STRUCT_IO_PORT, port_in) + tlv(STRUCT_IO_PORT, port_out)

    payload = build_kv(
        [
            kv_u32(F_ID, 5001),
            kv_str(F_STRUCT_NAME, "Demo Machine"),
            kv_blob(F_STRUCT_LAYOUT, layout),
            kv_blob(F_STRUCT_IO, io),
        ]
    )
    return build_stream([(SCHEMA_STRUCTURE, payload)])


def demo_pack_manifest(content_stream):
    payload = build_kv(
        [
            kv_u32(F_PACK_ID, 1),
            kv_u32(F_PACK_VERSION, 1),
            kv_str(F_PACK_NAME, "Demo Pack"),
            kv_str(F_PACK_DESCRIPTION, "Demo pack manifest for toolchain"),
            kv_blob(F_PACK_CONTENT, content_stream),
        ]
    )
    return payload


def demo_mod_manifest(content_stream):
    payload = build_kv(
        [
            kv_u32(F_MOD_ID, 1),
            kv_u32(F_MOD_VERSION, 1),
            kv_str(F_MOD_NAME, "tools_demo"),
            kv_str(F_MOD_DESCRIPTION, "Demo mod manifest for toolchain"),
            kv_blob(F_MOD_CONTENT, content_stream),
        ]
    )
    return payload


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_dir = os.path.join(root, "data", "tools_demo")
    os.makedirs(out_dir, exist_ok=True)

    items = demo_material_item_stream()
    processes = demo_process_stream()
    struct_demo = demo_structure_stream()
    spline_demo = demo_spline_stream()

    files = {
        "blueprint_demo.tlv": demo_blueprint_stream(5001, 5001),
        "tech_demo.tlv": demo_research_stream(),
        "policy_demo.tlv": demo_policy_stream(),
        "process_demo.tlv": build_stream(
            [
                (SCHEMA_MATERIAL, build_kv([kv_u32(F_ID, 1001), kv_str(F_MAT_NAME, "Iron")])),
                (SCHEMA_ITEM, build_kv([kv_u32(F_ID, 2001), kv_str(F_ITEM_NAME, "Ore"), kv_u32(F_ITEM_MATERIAL, 1001)])),
                (SCHEMA_ITEM, build_kv([kv_u32(F_ID, 2002), kv_str(F_ITEM_NAME, "Plate"), kv_u32(F_ITEM_MATERIAL, 1001)])),
                (SCHEMA_ITEM, build_kv([kv_u32(F_ID, 2003), kv_str(F_ITEM_NAME, "Widget"), kv_u32(F_ITEM_MATERIAL, 1001)])),
            ]
        )
        + processes,
        "transport_demo.tlv": spline_demo,
        "struct_demo.tlv": struct_demo,
        "items_demo.tlv": items,
        "pack_demo.tlv": demo_pack_manifest(items),
        "mod_demo.tlv": demo_mod_manifest(build_stream([(SCHEMA_MATERIAL, build_kv([kv_u32(F_ID, 1001), kv_str(F_MAT_NAME, "Iron")]))]) + processes),
    }

    for name, data in files.items():
        path = os.path.join(out_dir, name)
        with open(path, "wb") as f:
            f.write(data)
        print("Wrote %d bytes -> %s" % (len(data), path))

    print("Done. World demo is generated separately via dominium_game headless.")


if __name__ == "__main__":
    main()
