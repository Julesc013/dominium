#include "json_writer.h"

#include <cstdio>

namespace {

enum {
    DSK_JSON_CONTAINER_OBJECT = 1,
    DSK_JSON_CONTAINER_ARRAY = 2
};

static void dsk_json_append_char(dsk_json_writer_t *writer, char c) {
    if (!writer) {
        return;
    }
    writer->out.push_back(c);
}

static void dsk_json_append_str(dsk_json_writer_t *writer, const char *s) {
    if (!writer) {
        return;
    }
    writer->out += s ? s : "";
}

static void dsk_json_begin_value(dsk_json_writer_t *writer) {
    if (!writer) {
        return;
    }
    if (writer->after_key) {
        writer->after_key = DSK_FALSE;
        return;
    }
    if (writer->container.empty()) {
        return;
    }
    if (writer->first.back()) {
        writer->first.back() = DSK_FALSE;
    } else {
        dsk_json_append_char(writer, ',');
    }
}

static void dsk_json_escape_append(dsk_json_writer_t *writer, const char *value) {
    const char *p = value ? value : "";
    while (*p) {
        unsigned char c = (unsigned char)*p++;
        switch (c) {
        case '\\': dsk_json_append_str(writer, "\\\\"); break;
        case '\"': dsk_json_append_str(writer, "\\\""); break;
        case '\b': dsk_json_append_str(writer, "\\b"); break;
        case '\f': dsk_json_append_str(writer, "\\f"); break;
        case '\n': dsk_json_append_str(writer, "\\n"); break;
        case '\r': dsk_json_append_str(writer, "\\r"); break;
        case '\t': dsk_json_append_str(writer, "\\t"); break;
        default:
            if (c < 0x20u) {
                char buf[7];
                std::snprintf(buf, sizeof(buf), "\\u%04x", (unsigned)c);
                dsk_json_append_str(writer, buf);
            } else {
                dsk_json_append_char(writer, (char)c);
            }
            break;
        }
    }
}

} // namespace

void dsk_json_writer_init(dsk_json_writer_t *writer) {
    if (!writer) {
        return;
    }
    writer->out.clear();
    writer->container.clear();
    writer->first.clear();
    writer->after_key = DSK_FALSE;
}

void dsk_json_writer_reset(dsk_json_writer_t *writer) {
    dsk_json_writer_init(writer);
}

const std::string &dsk_json_writer_str(const dsk_json_writer_t *writer) {
    static std::string empty;
    if (!writer) {
        return empty;
    }
    return writer->out;
}

void dsk_json_begin_object(dsk_json_writer_t *writer) {
    dsk_json_begin_value(writer);
    dsk_json_append_char(writer, '{');
    writer->container.push_back(DSK_JSON_CONTAINER_OBJECT);
    writer->first.push_back(DSK_TRUE);
    writer->after_key = DSK_FALSE;
}

void dsk_json_end_object(dsk_json_writer_t *writer) {
    if (!writer || writer->container.empty()) {
        return;
    }
    dsk_json_append_char(writer, '}');
    writer->container.pop_back();
    writer->first.pop_back();
    writer->after_key = DSK_FALSE;
}

void dsk_json_begin_array(dsk_json_writer_t *writer) {
    dsk_json_begin_value(writer);
    dsk_json_append_char(writer, '[');
    writer->container.push_back(DSK_JSON_CONTAINER_ARRAY);
    writer->first.push_back(DSK_TRUE);
    writer->after_key = DSK_FALSE;
}

void dsk_json_end_array(dsk_json_writer_t *writer) {
    if (!writer || writer->container.empty()) {
        return;
    }
    dsk_json_append_char(writer, ']');
    writer->container.pop_back();
    writer->first.pop_back();
    writer->after_key = DSK_FALSE;
}

void dsk_json_key(dsk_json_writer_t *writer, const char *key) {
    if (!writer || writer->container.empty() ||
        writer->container.back() != DSK_JSON_CONTAINER_OBJECT) {
        return;
    }
    if (writer->first.back()) {
        writer->first.back() = DSK_FALSE;
    } else {
        dsk_json_append_char(writer, ',');
    }
    dsk_json_append_char(writer, '"');
    dsk_json_escape_append(writer, key);
    dsk_json_append_str(writer, "\":");
    writer->after_key = DSK_TRUE;
}

void dsk_json_string(dsk_json_writer_t *writer, const char *value) {
    dsk_json_begin_value(writer);
    dsk_json_append_char(writer, '"');
    dsk_json_escape_append(writer, value);
    dsk_json_append_char(writer, '"');
}

void dsk_json_bool(dsk_json_writer_t *writer, dsk_bool value) {
    dsk_json_begin_value(writer);
    dsk_json_append_str(writer, value ? "true" : "false");
}

void dsk_json_u32(dsk_json_writer_t *writer, dsk_u32 value) {
    char buf[32];
    dsk_json_begin_value(writer);
    std::snprintf(buf, sizeof(buf), "%u", (unsigned)value);
    dsk_json_append_str(writer, buf);
}

void dsk_json_u64(dsk_json_writer_t *writer, dsk_u64 value) {
    char buf[32];
    dsk_json_begin_value(writer);
    std::snprintf(buf, sizeof(buf), "%llu", (unsigned long long)value);
    dsk_json_append_str(writer, buf);
}

void dsk_json_u64_hex(dsk_json_writer_t *writer, dsk_u64 value) {
    char buf[32];
    dsk_json_begin_value(writer);
    std::snprintf(buf, sizeof(buf), "\"0x%016llx\"", (unsigned long long)value);
    dsk_json_append_str(writer, buf);
}

void dsk_json_raw(dsk_json_writer_t *writer, const char *raw) {
    dsk_json_begin_value(writer);
    dsk_json_append_str(writer, raw);
}

