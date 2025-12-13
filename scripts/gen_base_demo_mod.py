import os
import struct


def tlv(tag, payload):
    return struct.pack("<II", tag, len(payload)) + payload


def field_u32(tag, value):
    return tlv(tag, struct.pack("<I", value))

def field_u16(tag, value):
    return tlv(tag, struct.pack("<H", value))


def field_i32(tag, value):
    return tlv(tag, struct.pack("<i", value))


def field_str(tag, text):
    data = text.encode("utf-8") + b"\0"
    return tlv(tag, data)


def field_q16(tag, value):
    raw = int(round(value * 65536))
    return tlv(tag, struct.pack("<i", raw))


SCHEMA_MATERIAL = 0x0101
SCHEMA_ITEM = 0x0102
SCHEMA_CONTAINER = 0x0103
SCHEMA_PROCESS = 0x0104
SCHEMA_DEPOSIT = 0x0105
SCHEMA_STRUCTURE = 0x0106
SCHEMA_SPLINE = 0x0108
SCHEMA_JOB_TEMPLATE = 0x0109
SCHEMA_BLUEPRINT = 0x010B
SCHEMA_MOD = 0x0202

F_MAT_ID = 0x01
F_MAT_NAME = 0x02
F_MAT_TAGS = 0x03
F_MAT_DENSITY = 0x04
F_MAT_HARDNESS = 0x05
F_MAT_MELT = 0x06

F_ITEM_ID = 0x01
F_ITEM_NAME = 0x02
F_ITEM_MATERIAL = 0x03
F_ITEM_TAGS = 0x04
F_ITEM_UNIT_MASS = 0x05
F_ITEM_UNIT_VOL = 0x06

F_CONT_ID = 0x01
F_CONT_NAME = 0x02
F_CONT_TAGS = 0x03
F_CONT_MAX_VOL = 0x04
F_CONT_MAX_MASS = 0x05
F_CONT_SLOTS = 0x06
F_CONT_PACKING_MODE = 0x07
F_CONT_PARAMS = 0x08

F_PROC_ID = 0x01
F_PROC_NAME = 0x02
F_PROC_TAGS = 0x03
F_PROC_PARAMS = 0x04
F_PROC_BASE_DURATION = 0x05
F_PROC_IO_TERM = 0x06

F_PROC_IO_KIND = 0x01
F_PROC_IO_ITEM_ID = 0x02
F_PROC_IO_RATE = 0x03
F_PROC_IO_FLAGS = 0x04

F_DEP_ID = 0x01
F_DEP_NAME = 0x02
F_DEP_MATERIAL = 0x03
F_DEP_MODEL = 0x04
F_DEP_TAGS = 0x05
F_DEP_PARAMS = 0x06

F_STRUCT_ID = 0x01
F_STRUCT_NAME = 0x02
F_STRUCT_TAGS = 0x03
F_STRUCT_LAYOUT = 0x04
F_STRUCT_IO = 0x05
F_STRUCT_PROCESSES = 0x06

F_SPLINE_ID = 0x01
F_SPLINE_NAME = 0x02
F_SPLINE_TAGS = 0x03
F_SPLINE_PARAMS = 0x04
F_SPLINE_TYPE = 0x05
F_SPLINE_FLAGS = 0x06
F_SPLINE_BASE_SPEED = 0x07
F_SPLINE_MAX_GRADE = 0x08
F_SPLINE_CAPACITY = 0x09

F_JOB_ID = 0x01
F_JOB_NAME = 0x02
F_JOB_PURPOSE = 0x03
F_JOB_TAGS = 0x04
F_JOB_PROCESS_ID = 0x05
F_JOB_STRUCTURE_ID = 0x06
F_JOB_SPLINE_PROFILE_ID = 0x07
F_JOB_REQUIREMENTS = 0x08
F_JOB_REWARDS = 0x09

F_BLUEPRINT_ID = 0x01
F_BLUEPRINT_NAME = 0x02
F_BLUEPRINT_TAGS = 0x03
F_BLUEPRINT_PAYLOAD = 0x04

F_MOD_ID = 0x01
F_MOD_VERSION = 0x02
F_MOD_NAME = 0x03
F_MOD_DESCRIPTION = 0x04
F_MOD_DEPS = 0x05
F_MOD_CONTENT = 0x06

RES_MEAN_GRADE = 0x01
RES_MEAN_QUANTITY = 0x02
RES_NOISE_SCALE = 0x03
RES_REGEN_RATE = 0x04

LAYOUT_W = 0x01
LAYOUT_H = 0x02
LAYOUT_ANCHOR = 0x03
LAYOUT_INV_IN = 0x04
LAYOUT_INV_OUT = 0x05

PORT_BLOCK = 0x10
PORT_KIND = 0x01
PORT_X = 0x02
PORT_Y = 0x03
PORT_DIR_Z = 0x04

PROCESS_ALLOWED = 0x20
BLUEPRINT_STRUCT = 0x01

TAG_MATERIAL_SOLID = 1 << 0
TAG_GENERIC_METALLIC = 1 << 6
TAG_ITEM_RAW = 1 << 10
TAG_ITEM_STACKABLE = 1 << 8
TAG_CONTAINER_BULK = 1 << 12
TAG_CONTAINER_SLOTS = 1 << 13
TAG_PROCESS_TRANSFORM = 1 << 17
TAG_STRUCTURE_MACHINE = 1 << 22
TAG_STRUCTURE_TRANSPORT = 1 << 21
TAG_DEPOSIT_STRATA_SOLID = 1 << 26

TAG_CAP_OPERATE_PROCESS = 1 << 29

DRES_MODEL_STRATA_SOLID = 1

SPLINE_TYPE_ITEM = 1

PROC_IO_INPUT_ITEM = 1
PROC_IO_OUTPUT_ITEM = 2

JOB_PURPOSE_OPERATE_PROCESS = 1

JOB_REQ_AGENT_TAGS = 0x11


def build_content_blob():
    entries = []

    mat_payload = b"".join(
        [
            field_u32(F_MAT_ID, 1001),
            field_str(F_MAT_NAME, "Test Solid"),
            field_u32(F_MAT_TAGS, TAG_MATERIAL_SOLID | TAG_GENERIC_METALLIC),
            field_q16(F_MAT_DENSITY, 2.0),
            field_q16(F_MAT_HARDNESS, 1.0),
            field_q16(F_MAT_MELT, 1000.0),
        ]
    )
    entries.append(tlv(SCHEMA_MATERIAL, mat_payload))

    raw_item = b"".join(
        [
            field_u32(F_ITEM_ID, 10001),
            field_str(F_ITEM_NAME, "Demo Raw Unit"),
            field_u32(F_ITEM_MATERIAL, 1001),
            field_u32(F_ITEM_TAGS, TAG_ITEM_RAW | TAG_ITEM_STACKABLE),
            field_q16(F_ITEM_UNIT_MASS, 1.0),
            field_q16(F_ITEM_UNIT_VOL, 1.0),
        ]
    )
    entries.append(tlv(SCHEMA_ITEM, raw_item))

    mid_item = b"".join(
        [
            field_u32(F_ITEM_ID, 10002),
            field_str(F_ITEM_NAME, "Demo Intermediate Unit"),
            field_u32(F_ITEM_MATERIAL, 1001),
            field_u32(F_ITEM_TAGS, TAG_ITEM_STACKABLE),
            field_q16(F_ITEM_UNIT_MASS, 1.0),
            field_q16(F_ITEM_UNIT_VOL, 1.0),
        ]
    )
    entries.append(tlv(SCHEMA_ITEM, mid_item))

    fin_item = b"".join(
        [
            field_u32(F_ITEM_ID, 10003),
            field_str(F_ITEM_NAME, "Demo Final Unit"),
            field_u32(F_ITEM_MATERIAL, 1001),
            field_u32(F_ITEM_TAGS, TAG_ITEM_STACKABLE),
            field_q16(F_ITEM_UNIT_MASS, 1.0),
            field_q16(F_ITEM_UNIT_VOL, 1.0),
        ]
    )
    entries.append(tlv(SCHEMA_ITEM, fin_item))

    cont_payload = b"".join(
        [
            field_u32(F_CONT_ID, 50001),
            field_str(F_CONT_NAME, "Demo Buffer"),
            field_u32(F_CONT_TAGS, TAG_CONTAINER_SLOTS),
            field_q16(F_CONT_MAX_VOL, 9999.0),
            field_q16(F_CONT_MAX_MASS, 9999.0),
            field_u16(F_CONT_SLOTS, 8),
            field_u16(F_CONT_PACKING_MODE, 1),
            tlv(F_CONT_PARAMS, b""),
        ]
    )
    entries.append(tlv(SCHEMA_CONTAINER, cont_payload))

    storage_payload = b"".join(
        [
            field_u32(F_CONT_ID, 50002),
            field_str(F_CONT_NAME, "Demo Storage"),
            field_u32(F_CONT_TAGS, TAG_CONTAINER_SLOTS),
            field_q16(F_CONT_MAX_VOL, 9999.0),
            field_q16(F_CONT_MAX_MASS, 9999.0),
            field_u16(F_CONT_SLOTS, 16),
            field_u16(F_CONT_PACKING_MODE, 1),
            tlv(F_CONT_PARAMS, b""),
        ]
    )
    entries.append(tlv(SCHEMA_CONTAINER, storage_payload))

    spline_payload = b"".join(
        [
            field_u32(F_SPLINE_ID, 70001),
            field_str(F_SPLINE_NAME, "Demo Item Conveyor"),
            field_u32(F_SPLINE_TYPE, SPLINE_TYPE_ITEM),
            field_u16(F_SPLINE_FLAGS, 0),
            field_q16(F_SPLINE_BASE_SPEED, 2.0),
            field_q16(F_SPLINE_MAX_GRADE, 0.2),
            field_q16(F_SPLINE_CAPACITY, 4.0),
            field_u32(F_SPLINE_TAGS, 0),
            tlv(F_SPLINE_PARAMS, b""),
        ]
    )
    entries.append(tlv(SCHEMA_SPLINE, spline_payload))

    def proc_io_term(kind, item_id, rate_per_tick, flags=0):
        inner = b"".join(
            [
                field_u16(F_PROC_IO_KIND, kind),
                field_u32(F_PROC_IO_ITEM_ID, item_id),
                field_q16(F_PROC_IO_RATE, rate_per_tick),
                field_u16(F_PROC_IO_FLAGS, flags),
            ]
        )
        return tlv(F_PROC_IO_TERM, inner)

    base_duration = 64.0
    rate_1_per_cycle = 1.0 / 64.0

    proc_extract = b"".join(
        [
            field_u32(F_PROC_ID, 30001),
            field_str(F_PROC_NAME, "Demo Extract"),
            field_u32(F_PROC_TAGS, TAG_PROCESS_TRANSFORM),
            tlv(F_PROC_PARAMS, b""),
            field_q16(F_PROC_BASE_DURATION, base_duration),
            proc_io_term(PROC_IO_OUTPUT_ITEM, 10001, rate_1_per_cycle, 0),
        ]
    )
    entries.append(tlv(SCHEMA_PROCESS, proc_extract))

    proc_refine = b"".join(
        [
            field_u32(F_PROC_ID, 30002),
            field_str(F_PROC_NAME, "Demo Refine"),
            field_u32(F_PROC_TAGS, TAG_PROCESS_TRANSFORM),
            tlv(F_PROC_PARAMS, b""),
            field_q16(F_PROC_BASE_DURATION, base_duration),
            proc_io_term(PROC_IO_INPUT_ITEM, 10001, rate_1_per_cycle, 0),
            proc_io_term(PROC_IO_OUTPUT_ITEM, 10002, rate_1_per_cycle, 0),
        ]
    )
    entries.append(tlv(SCHEMA_PROCESS, proc_refine))

    proc_assemble = b"".join(
        [
            field_u32(F_PROC_ID, 30003),
            field_str(F_PROC_NAME, "Demo Assemble"),
            field_u32(F_PROC_TAGS, TAG_PROCESS_TRANSFORM),
            tlv(F_PROC_PARAMS, b""),
            field_q16(F_PROC_BASE_DURATION, base_duration),
            proc_io_term(PROC_IO_INPUT_ITEM, 10002, rate_1_per_cycle, 0),
            proc_io_term(PROC_IO_OUTPUT_ITEM, 10003, rate_1_per_cycle, 0),
        ]
    )
    entries.append(tlv(SCHEMA_PROCESS, proc_assemble))

    model_params = b"".join(
        [
            field_q16(RES_MEAN_GRADE, 1.0),
            field_q16(RES_MEAN_QUANTITY, 400.0),
            field_q16(RES_NOISE_SCALE, 0.25),
            field_q16(RES_REGEN_RATE, 0.0),
        ]
    )
    deposit_payload = b"".join(
        [
            field_u32(F_DEP_ID, 20001),
            field_str(F_DEP_NAME, "Test Deposit"),
            field_u32(F_DEP_MATERIAL, 1001),
            field_u16(F_DEP_MODEL, DRES_MODEL_STRATA_SOLID),
            field_u32(F_DEP_TAGS, TAG_DEPOSIT_STRATA_SOLID),
            tlv(F_DEP_PARAMS, model_params),
        ]
    )
    entries.append(tlv(SCHEMA_DEPOSIT, deposit_payload))

    layout_payload = b"".join(
        [
            field_u32(LAYOUT_W, 1),
            field_u32(LAYOUT_H, 1),
            field_q16(LAYOUT_ANCHOR, 0.0),
            field_u32(LAYOUT_INV_IN, 50001),
            field_u32(LAYOUT_INV_OUT, 50001),
        ]
    )
    port_out = b"".join(
        [
            field_u32(PORT_KIND, 10),
            field_i32(PORT_X, 1),
            field_i32(PORT_Y, 0),
            field_i32(PORT_DIR_Z, 0),
        ]
    )
    io_payload = b"".join([tlv(PORT_BLOCK, port_out)])
    process_list = tlv(PROCESS_ALLOWED, struct.pack("<I", 30001))
    structure_payload = b"".join(
        [
            field_u32(F_STRUCT_ID, 40001),
            field_str(F_STRUCT_NAME, "Demo Extractor"),
            field_u32(F_STRUCT_TAGS, TAG_STRUCTURE_MACHINE),
            tlv(F_STRUCT_LAYOUT, layout_payload),
            tlv(F_STRUCT_IO, io_payload),
            tlv(F_STRUCT_PROCESSES, process_list),
        ]
    )
    entries.append(tlv(SCHEMA_STRUCTURE, structure_payload))

    refine_layout = b"".join(
        [
            field_u32(LAYOUT_W, 1),
            field_u32(LAYOUT_H, 1),
            field_q16(LAYOUT_ANCHOR, 0.0),
            field_u32(LAYOUT_INV_IN, 50001),
            field_u32(LAYOUT_INV_OUT, 50001),
        ]
    )
    refine_port_in = b"".join(
        [
            field_u32(PORT_KIND, 11),
            field_i32(PORT_X, -1),
            field_i32(PORT_Y, 0),
            field_i32(PORT_DIR_Z, 0),
        ]
    )
    refine_port_out = b"".join(
        [
            field_u32(PORT_KIND, 10),
            field_i32(PORT_X, 1),
            field_i32(PORT_Y, 0),
            field_i32(PORT_DIR_Z, 0),
        ]
    )
    refine_io = b"".join([tlv(PORT_BLOCK, refine_port_in), tlv(PORT_BLOCK, refine_port_out)])
    refine_process_list = tlv(PROCESS_ALLOWED, struct.pack("<I", 30002))
    refine_struct_payload = b"".join(
        [
            field_u32(F_STRUCT_ID, 40002),
            field_str(F_STRUCT_NAME, "Demo Refiner"),
            field_u32(F_STRUCT_TAGS, TAG_STRUCTURE_MACHINE),
            tlv(F_STRUCT_LAYOUT, refine_layout),
            tlv(F_STRUCT_IO, refine_io),
            tlv(F_STRUCT_PROCESSES, refine_process_list),
        ]
    )
    entries.append(tlv(SCHEMA_STRUCTURE, refine_struct_payload))

    assemble_layout = b"".join(
        [
            field_u32(LAYOUT_W, 1),
            field_u32(LAYOUT_H, 1),
            field_q16(LAYOUT_ANCHOR, 0.0),
            field_u32(LAYOUT_INV_IN, 50001),
            field_u32(LAYOUT_INV_OUT, 50001),
        ]
    )
    assemble_port_in = b"".join(
        [
            field_u32(PORT_KIND, 11),
            field_i32(PORT_X, -1),
            field_i32(PORT_Y, 0),
            field_i32(PORT_DIR_Z, 0),
        ]
    )
    assemble_port_out = b"".join(
        [
            field_u32(PORT_KIND, 10),
            field_i32(PORT_X, 1),
            field_i32(PORT_Y, 0),
            field_i32(PORT_DIR_Z, 0),
        ]
    )
    assemble_io = b"".join([tlv(PORT_BLOCK, assemble_port_in), tlv(PORT_BLOCK, assemble_port_out)])
    assemble_process_list = tlv(PROCESS_ALLOWED, struct.pack("<I", 30003))
    assemble_struct_payload = b"".join(
        [
            field_u32(F_STRUCT_ID, 40003),
            field_str(F_STRUCT_NAME, "Demo Assembler"),
            field_u32(F_STRUCT_TAGS, TAG_STRUCTURE_MACHINE),
            tlv(F_STRUCT_LAYOUT, assemble_layout),
            tlv(F_STRUCT_IO, assemble_io),
            tlv(F_STRUCT_PROCESSES, assemble_process_list),
        ]
    )
    entries.append(tlv(SCHEMA_STRUCTURE, assemble_struct_payload))

    bin_layout = b"".join(
        [
            field_u32(LAYOUT_W, 1),
            field_u32(LAYOUT_H, 1),
            field_q16(LAYOUT_ANCHOR, 0.0),
            field_u32(LAYOUT_INV_OUT, 50002),
        ]
    )
    bin_port_in = b"".join(
        [
            field_u32(PORT_KIND, 11),
            field_i32(PORT_X, 0),
            field_i32(PORT_Y, 0),
            field_i32(PORT_DIR_Z, 0),
        ]
    )
    bin_io = tlv(PORT_BLOCK, bin_port_in)
    bin_struct_payload = b"".join(
        [
            field_u32(F_STRUCT_ID, 40004),
            field_str(F_STRUCT_NAME, "Demo Bin"),
            field_u32(F_STRUCT_TAGS, TAG_STRUCTURE_TRANSPORT),
            tlv(F_STRUCT_LAYOUT, bin_layout),
            tlv(F_STRUCT_IO, bin_io),
            tlv(F_STRUCT_PROCESSES, b""),
        ]
    )
    entries.append(tlv(SCHEMA_STRUCTURE, bin_struct_payload))

    op_req = tlv(JOB_REQ_AGENT_TAGS, struct.pack("<I", TAG_CAP_OPERATE_PROCESS))

    op_extract = b"".join(
        [
            field_u32(F_JOB_ID, 80001),
            field_str(F_JOB_NAME, "Demo Operate Extractor"),
            field_u16(F_JOB_PURPOSE, JOB_PURPOSE_OPERATE_PROCESS),
            field_u32(F_JOB_TAGS, 0),
            field_u32(F_JOB_PROCESS_ID, 30001),
            field_u32(F_JOB_STRUCTURE_ID, 40001),
            field_u32(F_JOB_SPLINE_PROFILE_ID, 0),
            tlv(F_JOB_REQUIREMENTS, op_req),
            tlv(F_JOB_REWARDS, b""),
        ]
    )
    entries.append(tlv(SCHEMA_JOB_TEMPLATE, op_extract))

    op_refine = b"".join(
        [
            field_u32(F_JOB_ID, 80002),
            field_str(F_JOB_NAME, "Demo Operate Refiner"),
            field_u16(F_JOB_PURPOSE, JOB_PURPOSE_OPERATE_PROCESS),
            field_u32(F_JOB_TAGS, 0),
            field_u32(F_JOB_PROCESS_ID, 30002),
            field_u32(F_JOB_STRUCTURE_ID, 40002),
            field_u32(F_JOB_SPLINE_PROFILE_ID, 0),
            tlv(F_JOB_REQUIREMENTS, op_req),
            tlv(F_JOB_REWARDS, b""),
        ]
    )
    entries.append(tlv(SCHEMA_JOB_TEMPLATE, op_refine))

    op_assemble = b"".join(
        [
            field_u32(F_JOB_ID, 80003),
            field_str(F_JOB_NAME, "Demo Operate Assembler"),
            field_u16(F_JOB_PURPOSE, JOB_PURPOSE_OPERATE_PROCESS),
            field_u32(F_JOB_TAGS, 0),
            field_u32(F_JOB_PROCESS_ID, 30003),
            field_u32(F_JOB_STRUCTURE_ID, 40003),
            field_u32(F_JOB_SPLINE_PROFILE_ID, 0),
            tlv(F_JOB_REQUIREMENTS, op_req),
            tlv(F_JOB_REWARDS, b""),
        ]
    )
    entries.append(tlv(SCHEMA_JOB_TEMPLATE, op_assemble))

    bp_payload = tlv(BLUEPRINT_STRUCT, struct.pack("<I", 40001))
    blueprint_payload = b"".join(
        [
            field_u32(F_BLUEPRINT_ID, 60001),
            field_str(F_BLUEPRINT_NAME, "Demo Extractor Kit"),
            field_u32(F_BLUEPRINT_TAGS, 0),
            tlv(F_BLUEPRINT_PAYLOAD, bp_payload),
        ]
    )
    entries.append(tlv(SCHEMA_BLUEPRINT, blueprint_payload))

    return b"".join(entries)


def build_mod_blob():
    content_blob = build_content_blob()
    mod_payload = b"".join(
        [
            field_u32(F_MOD_ID, 1),
            field_u32(F_MOD_VERSION, 1),
            field_str(F_MOD_NAME, "base_demo"),
            field_str(F_MOD_DESCRIPTION, "Data-driven demo"),
            tlv(F_MOD_CONTENT, content_blob),
        ]
    )
    return mod_payload


def main():
    out_dir = os.path.join("repo", "mods", "base_demo", "00000001")
    os.makedirs(out_dir, exist_ok=True)
    blob = build_mod_blob()
    out_path = os.path.join(out_dir, "mod.tlv")
    with open(out_path, "wb") as f:
        f.write(blob)
    print(f"Wrote {len(blob)} bytes to {out_path}")


if __name__ == "__main__":
    main()
