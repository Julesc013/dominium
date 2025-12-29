#include "dss_fs_internal.h"

#include <algorithm>

static dss_error_t dss_fs_err(dss_u16 code, dss_u16 subcode) {
    return dss_error_make(DSS_DOMAIN_SERVICES, code, subcode, 0u);
}

static dss_bool dss_fs_is_alpha(char c) {
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}

static void dss_fs_replace_seps(std::string &s) {
    size_t i;
    for (i = 0u; i < s.size(); ++i) {
        if (s[i] == '\\') {
            s[i] = '/';
        }
    }
}

static void dss_fs_lowercase(std::string &s) {
    size_t i;
    for (i = 0u; i < s.size(); ++i) {
        char c = s[i];
        if (c >= 'A' && c <= 'Z') {
            s[i] = (char)(c - 'A' + 'a');
        }
    }
}

static std::string dss_fs_trim_trailing_slash(const std::string &s) {
    if (s.size() <= 1u) {
        return s;
    }
    if (s.size() == 3u && dss_fs_is_alpha(s[0]) && s[1] == ':' && s[2] == '/') {
        return s;
    }
    size_t end = s.size();
    while (end > 0u && s[end - 1u] == '/') {
        --end;
    }
    return s.substr(0u, end);
}

dss_bool dss_fs_is_abs_path(const std::string &path) {
    if (path.empty()) {
        return DSS_FALSE;
    }
    if (path[0] == '/' || path[0] == '\\') {
        return DSS_TRUE;
    }
    if (path.size() >= 2u && path[0] == '\\' && path[1] == '\\') {
        return DSS_TRUE;
    }
    if (path.size() >= 2u && dss_fs_is_alpha(path[0]) && path[1] == ':') {
        return DSS_TRUE;
    }
    return DSS_FALSE;
}

dss_bool dss_fs_path_has_prefix(const std::string &path, const std::string &root) {
    std::string p = path;
    std::string r = root;
    dss_fs_replace_seps(p);
    dss_fs_replace_seps(r);
    dss_fs_lowercase(p);
    dss_fs_lowercase(r);
    p = dss_fs_trim_trailing_slash(p);
    r = dss_fs_trim_trailing_slash(r);
    if (r.empty() || r == ".") {
        return DSS_TRUE;
    }
    if (p.size() < r.size()) {
        return DSS_FALSE;
    }
    if (p.compare(0u, r.size(), r) != 0) {
        return DSS_FALSE;
    }
    if (p.size() == r.size()) {
        return DSS_TRUE;
    }
    return p[r.size()] == '/';
}

dss_error_t dss_fs_canonicalize_path(const char *path,
                                     dss_bool reject_parent,
                                     std::string *out_path) {
    std::string in;
    std::string prefix;
    std::vector<std::string> segs;
    size_t i;
    size_t start;
    dss_bool abs = DSS_FALSE;

    if (!path || !out_path) {
        return dss_fs_err(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    in.assign(path);
    if (in.empty()) {
        return dss_fs_err(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    dss_fs_replace_seps(in);

    i = 0u;
    if (in.size() >= 2u && dss_fs_is_alpha(in[0]) && in[1] == ':') {
        prefix = in.substr(0u, 2u);
        i = 2u;
        if (i < in.size() && in[i] == '/') {
            abs = DSS_TRUE;
            ++i;
        }
    } else if (in.size() >= 2u && in[0] == '/' && in[1] == '/') {
        prefix = "//";
        abs = DSS_TRUE;
        i = 2u;
    } else if (in[0] == '/') {
        abs = DSS_TRUE;
        i = 1u;
    }

    start = i;
    for (; i <= in.size(); ++i) {
        char c = (i < in.size()) ? in[i] : '/';
        if (c == '/') {
            size_t len = i - start;
            if (len != 0u) {
                std::string seg = in.substr(start, len);
                if (seg == ".") {
                    /* skip */
                } else if (seg == "..") {
                    if (reject_parent) {
                        return dss_fs_err(DSS_CODE_SANDBOX_VIOLATION,
                                          DSS_SUBCODE_PATH_TRAVERSAL);
                    }
                    if (!segs.empty() && segs.back() != "..") {
                        segs.pop_back();
                    } else if (!abs) {
                        segs.push_back(seg);
                    }
                } else {
                    segs.push_back(seg);
                }
            }
            start = i + 1u;
        }
    }

    {
        std::string out;
        if (!prefix.empty()) {
            out += prefix;
        }
        if (abs) {
            if (out.empty() || out[out.size() - 1u] != '/') {
                out += "/";
            }
        }
        for (i = 0u; i < segs.size(); ++i) {
            if (!out.empty() && out[out.size() - 1u] != '/' && out[out.size() - 1u] != ':') {
                out += "/";
            }
            out += segs[i];
        }
        if (out.empty()) {
            out = abs ? "/" : ".";
        }
        *out_path = out;
    }

    return dss_error_make(DSS_DOMAIN_SERVICES, DSS_CODE_OK, DSS_SUBCODE_NONE, 0u);
}

dss_error_t dss_fs_join_path(const char *a,
                             const char *b,
                             std::string *out_path) {
    std::string left;
    std::string right;
    if (!out_path) {
        return dss_fs_err(DSS_CODE_INVALID_ARGS, DSS_SUBCODE_NONE);
    }
    left = a ? a : "";
    right = b ? b : "";
    if (left.empty()) {
        return dss_fs_canonicalize_path(right.c_str(), DSS_FALSE, out_path);
    }
    if (right.empty()) {
        return dss_fs_canonicalize_path(left.c_str(), DSS_FALSE, out_path);
    }
    if (dss_fs_is_abs_path(right)) {
        return dss_fs_canonicalize_path(right.c_str(), DSS_FALSE, out_path);
    }
    if (left[left.size() - 1u] != '/' && left[left.size() - 1u] != '\\') {
        left += "/";
    }
    left += right;
    return dss_fs_canonicalize_path(left.c_str(), DSS_FALSE, out_path);
}
