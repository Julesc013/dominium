/*
FILE: source/dominium/launcher/core/include/launcher_tlv.h
MODULE: Dominium
PURPOSE: Launcher TLV helpers (forwarding wrapper over core_tlv).
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_H

#include "dominium/core_tlv.h"

namespace dom {
namespace launcher_core {

using dom::core_tlv::TlvReader;
using dom::core_tlv::TlvWriter;
using dom::core_tlv::TlvRecord;

enum { LAUNCHER_TLV_HEADER_BYTES = dom::core_tlv::CORE_TLV_HEADER_BYTES };
enum { LAUNCHER_TLV_MAX_RECORDS = dom::core_tlv::CORE_TLV_MAX_RECORDS };
enum { LAUNCHER_TLV_TAG_SCHEMA_VERSION = dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION };

using dom::core_tlv::tlv_fnv1a64;
using dom::core_tlv::tlv_write_u32_le;
using dom::core_tlv::tlv_write_u64_le;
using dom::core_tlv::tlv_read_u32_le;
using dom::core_tlv::tlv_read_i32_le;
using dom::core_tlv::tlv_read_u64_le;
using dom::core_tlv::tlv_read_string;
using dom::core_tlv::tlv_read_schema_version_or_default;

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_TLV_H */
