/*
FILE: source/dominium/tools/common/dom_tool_controller_content.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_controller_content
RESPONSIBILITY: Defines internal contract for `dom_tool_controller_content`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_TOOL_CONTROLLER_CONTENT_H
#define DOM_TOOL_CONTROLLER_CONTENT_H

#include "dom_tool_app.h"

#include <string>
#include <vector>

namespace dom {
namespace tools {

class DomContentToolController : public DomToolController {
public:
    DomContentToolController(const char *tool_id,
                             const char *tool_name,
                             const char *tool_description,
                             const u32 *focus_schema_ids,
                             size_t focus_schema_count,
                             const char *demo_rel_path);

    virtual const char *tool_id() const;
    virtual const char *tool_name() const;
    virtual const char *tool_description() const;

    virtual bool supports_demo() const;
    virtual std::string demo_path(const std::string &home) const;

    virtual bool load(const std::string &path, std::string &status);
    virtual bool validate(std::string &status);
    virtual bool save(const std::string &path, std::string &status);
    virtual void summary(std::string &out) const;

private:
    enum SourceKind {
        SRC_NONE = 0,
        SRC_RECORD_STREAM,
        SRC_MOD_MANIFEST,
        SRC_PACK_MANIFEST,
        SRC_SINGLE_PAYLOAD
    };

    bool compute_counts_and_canonicalize(std::string &status);
    bool canonicalize_record_stream(const std::vector<unsigned char> &in,
                                    std::vector<unsigned char> &out);
    bool canonicalize_kv_payload(const std::vector<unsigned char> &in,
                                 std::vector<unsigned char> &out);
    bool canonicalize_kv_payload_replace_blob_tag(const std::vector<unsigned char> &in,
                                                  u32 replace_tag,
                                                  const std::vector<unsigned char> &replacement,
                                                  std::vector<unsigned char> &out);

    bool extract_kv_blob_tag(const std::vector<unsigned char> &kv_payload,
                             u32 tag,
                             std::vector<unsigned char> &out_payload) const;

    bool is_focus_schema(u32 schema_id) const;

private:
    std::string m_tool_id;
    std::string m_tool_name;
    std::string m_tool_desc;
    std::vector<u32> m_focus_schemas;
    std::string m_demo_rel_path;

    SourceKind m_kind;
    u32 m_single_schema_id;

    std::vector<unsigned char> m_file_bytes;
    std::vector<unsigned char> m_content_stream;
    std::vector<unsigned char> m_canonical_content_stream;
    std::vector<unsigned char> m_canonical_file_bytes;

    size_t m_total_records;
    size_t m_focus_records;
};

} // namespace tools
} // namespace dom

#endif /* DOM_TOOL_CONTROLLER_CONTENT_H */

