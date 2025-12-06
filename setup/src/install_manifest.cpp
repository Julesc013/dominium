#include "dom_setup_install_manifest.h"

#include <ctime>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <sstream>

// Minimal JSON helpers; this stays intentionally small to keep dependencies light.
static void trim_ws(const std::string &s, size_t &i)
{
    while (i < s.size()) {
        char c = s[i];
        if (c == ' ' || c == '\t' || c == '\r' || c == '\n') {
            ++i;
        } else {
            break;
        }
    }
}

static bool parse_string_field(const std::string &content, const std::string &key, std::string &out)
{
    std::string needle = "\"" + key + "\"";
    size_t pos = content.find(needle);
    if (pos == std::string::npos) return false;
    pos = content.find(':', pos + needle.size());
    if (pos == std::string::npos) return false;
    ++pos;
    trim_ws(content, pos);
    if (pos >= content.size() || content[pos] != '"') {
        return false;
    }
    ++pos;
    std::string value;
    while (pos < content.size() && content[pos] != '"') {
        if (content[pos] == '\\' && pos + 1 < content.size()) {
            ++pos;
        }
        value.push_back(content[pos]);
        ++pos;
    }
    out = value;
    return true;
}

static bool parse_int_field(const std::string &content, const std::string &key, int &out)
{
    std::string needle = "\"" + key + "\"";
    size_t pos = content.find(needle);
    if (pos == std::string::npos) return false;
    pos = content.find(':', pos + needle.size());
    if (pos == std::string::npos) return false;
    ++pos;
    trim_ws(content, pos);
    std::string number;
    while (pos < content.size()) {
        char c = content[pos];
        if ((c >= '0' && c <= '9') || c == '-') {
            number.push_back(c);
        } else {
            break;
        }
        ++pos;
    }
    if (number.empty()) return false;
    out = std::atoi(number.c_str());
    return true;
}

static std::string escape_json(const std::string &s)
{
    std::string out;
    for (size_t i = 0; i < s.size(); ++i) {
        char c = s[i];
        if (c == '"' || c == '\\') {
            out.push_back('\\');
        }
        out.push_back(c);
    }
    return out;
}

bool dom_manifest_read(const std::string &path, DomInstallManifest &out, std::string &err)
{
    FILE *f = std::fopen(path.c_str(), "rb");
    if (!f) {
        err = "failed to open manifest";
        return false;
    }
    std::string content;
    char buf[512];
    size_t n;
    while ((n = std::fread(buf, 1, sizeof(buf), f)) > 0) {
        content.append(buf, n);
    }
    std::fclose(f);

    if (!parse_int_field(content, "schema_version", out.schema_version)) {
        err = "missing schema_version";
        return false;
    }
    if (!parse_string_field(content, "install_id", out.install_id)) {
        err = "missing install_id";
        return false;
    }
    if (!parse_string_field(content, "install_type", out.install_type)) {
        err = "missing install_type";
        return false;
    }
    if (!parse_string_field(content, "platform", out.platform)) {
        err = "missing platform";
        return false;
    }
    if (!parse_string_field(content, "version", out.version)) {
        err = "missing version";
        return false;
    }
    if (!parse_string_field(content, "created_at", out.created_at)) {
        err = "missing created_at";
        return false;
    }
    if (!parse_string_field(content, "created_by", out.created_by)) {
        err = "missing created_by";
        return false;
    }
    return true;
}

bool dom_manifest_write(const std::string &path, const DomInstallManifest &manifest, std::string &err)
{
    FILE *f = std::fopen(path.c_str(), "wb");
    if (!f) {
        err = "failed to open manifest for write";
        return false;
    }
    std::fprintf(f, "{\n");
    std::fprintf(f, "  \"schema_version\": %d,\n", manifest.schema_version);
    std::fprintf(f, "  \"install_id\": \"%s\",\n", escape_json(manifest.install_id).c_str());
    std::fprintf(f, "  \"install_type\": \"%s\",\n", escape_json(manifest.install_type).c_str());
    std::fprintf(f, "  \"platform\": \"%s\",\n", escape_json(manifest.platform).c_str());
    std::fprintf(f, "  \"version\": \"%s\",\n", escape_json(manifest.version).c_str());
    std::fprintf(f, "  \"created_at\": \"%s\",\n", escape_json(manifest.created_at).c_str());
    std::fprintf(f, "  \"created_by\": \"%s\"\n", escape_json(manifest.created_by).c_str());
    std::fprintf(f, "}\n");
    std::fclose(f);
    return true;
}

static unsigned int random_u32()
{
    return (unsigned int)std::rand();
}

static std::string hex4(unsigned int v)
{
    char buf[9];
    std::sprintf(buf, "%04x%04x", (v >> 16) & 0xFFFFu, v & 0xFFFFu);
    return std::string(buf, 8);
}

std::string dom_manifest_generate_uuid()
{
    std::srand((unsigned int)std::time(0));
    std::string a = hex4(random_u32());
    std::string b = hex4(random_u32());
    std::string c = hex4(random_u32());
    std::string d = hex4(random_u32());
    std::string e = hex4(random_u32());
    return a + "-" + b + "-" + c + "-" + d + "-" + e;
}

std::string dom_manifest_platform_tag()
{
#ifdef _WIN32
    return "win_nt";
#elif defined(__APPLE__)
    return "mac";
#else
    return "linux";
#endif
}
