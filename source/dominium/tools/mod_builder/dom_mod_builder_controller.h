#ifndef DOM_MOD_BUILDER_CONTROLLER_H
#define DOM_MOD_BUILDER_CONTROLLER_H

#include "dominium/tools/common/dom_tool_app.h"

#include <string>
#include <vector>

namespace dom {
namespace tools {

class DomModBuilderController : public DomToolController {
public:
    DomModBuilderController();

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
    bool canonicalize_kv_payload(const std::vector<unsigned char> &in,
                                 std::vector<unsigned char> &out);
    bool canonicalize_record_stream(const std::vector<unsigned char> &in,
                                    std::vector<unsigned char> &out);
    bool extract_kv_tag_payload(const std::vector<unsigned char> &kv_payload,
                                u32 tag,
                                std::vector<unsigned char> &out_payload) const;

    bool build_canonical_manifest(std::string &status);
    bool build_dmod_archive(std::vector<unsigned char> &out,
                            std::string &status) const;

    static unsigned long long fnv1a64(const unsigned char *data, size_t len);

    static bool read_u32_field(const std::vector<unsigned char> &kv_payload, u32 tag, u32 &out);
    static bool read_string_field(const std::vector<unsigned char> &kv_payload, u32 tag, std::string &out);

    static std::string dirname_of(const std::string &path);
    static std::string join_slash(const std::string &a, const std::string &b);
    static std::string version_u32(unsigned v);

private:
    std::vector<unsigned char> m_file_bytes;
    std::vector<unsigned char> m_content_stream;
    std::vector<unsigned char> m_canonical_content_stream;
    std::vector<unsigned char> m_canonical_manifest;

    u32 m_mod_id;
    u32 m_mod_version;
    std::string m_mod_name;

    size_t m_record_count;
};

} // namespace tools
} // namespace dom

#endif /* DOM_MOD_BUILDER_CONTROLLER_H */

