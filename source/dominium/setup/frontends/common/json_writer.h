#ifndef DSK_FRONTEND_JSON_WRITER_H
#define DSK_FRONTEND_JSON_WRITER_H

#include "dsk/dsk_types.h"

#include <string>
#include <vector>

struct dsk_json_writer_t {
    std::string out;
    std::vector<dsk_u8> container;
    std::vector<dsk_bool> first;
    dsk_bool after_key;
};

void dsk_json_writer_init(dsk_json_writer_t *writer);
void dsk_json_writer_reset(dsk_json_writer_t *writer);
const std::string &dsk_json_writer_str(const dsk_json_writer_t *writer);

void dsk_json_begin_object(dsk_json_writer_t *writer);
void dsk_json_end_object(dsk_json_writer_t *writer);
void dsk_json_begin_array(dsk_json_writer_t *writer);
void dsk_json_end_array(dsk_json_writer_t *writer);
void dsk_json_key(dsk_json_writer_t *writer, const char *key);
void dsk_json_string(dsk_json_writer_t *writer, const char *value);
void dsk_json_bool(dsk_json_writer_t *writer, dsk_bool value);
void dsk_json_u32(dsk_json_writer_t *writer, dsk_u32 value);
void dsk_json_u64(dsk_json_writer_t *writer, dsk_u64 value);
void dsk_json_u64_hex(dsk_json_writer_t *writer, dsk_u64 value);
void dsk_json_raw(dsk_json_writer_t *writer, const char *raw);

#endif
