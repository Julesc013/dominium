#ifndef DOM_TOOL_VALIDATE_H
#define DOM_TOOL_VALIDATE_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
}

namespace dom {
namespace tools {

/* Validates a schema payload (no outer record tag). */
bool validate_schema_payload(u32 schema_id,
                             const std::vector<unsigned char> &payload,
                             std::string *err);

/* Validates a record stream: [schema_id, len, payload]* and validates each payload. */
bool validate_record_stream(const std::vector<unsigned char> &stream,
                            std::string *err);

/* Load record stream into d_content and run relevant validators. */
bool validate_with_engine_content(const std::vector<unsigned char> &content_stream,
                                  std::string *err);

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_VALIDATE_H */

