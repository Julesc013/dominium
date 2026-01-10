/*
FILE: source/dominium/tools/coredata_validate/coredata_validate_report.cpp
MODULE: Dominium
PURPOSE: Coredata validation report structures and formatting.
*/
#include "coredata_validate_report.h"

#include <algorithm>
#include <cstdio>
#include <sstream>

#include "dominium/core_tlv.h"

namespace dom {
namespace tools {

CoredataValidationReport::CoredataValidationReport()
    : tool_version("1"),
      mode(),
      input_path(),
      issues(),
      error_count(0u),
      warning_count(0u) {
}

static int class_rank(CoredataValidationClass cls) {
    switch (cls) {
        case CORE_DATA_SCHEMA_ERROR: return 1;
        case CORE_DATA_REFERENCE_ERROR: return 2;
        case CORE_DATA_DETERMINISM_ERROR: return 3;
        case CORE_DATA_POLICY_ERROR: return 4;
        case CORE_DATA_RANGE_ERROR: return 5;
        case CORE_DATA_MIGRATION_ERROR: return 6;
        default: return 99;
    }
}

static int severity_rank(CoredataValidationSeverity sev) {
    return (sev == CORE_DATA_SEVERITY_ERROR) ? 1 : 2;
}

void coredata_report_init(CoredataValidationReport &report,
                          const std::string &mode,
                          const std::string &input_path) {
    report = CoredataValidationReport();
    report.mode = mode;
    report.input_path = input_path;
}

void coredata_report_add_issue(CoredataValidationReport &report,
                               CoredataValidationClass cls,
                               CoredataValidationSeverity severity,
                               const std::string &code,
                               const std::string &message,
                               const std::string &path,
                               int line) {
    CoredataValidationIssue issue;
    issue.cls = cls;
    issue.severity = severity;
    issue.code = code;
    issue.message = message;
    issue.path = path;
    issue.line = line;
    report.issues.push_back(issue);
    if (severity == CORE_DATA_SEVERITY_ERROR) {
        report.error_count += 1u;
    } else {
        report.warning_count += 1u;
    }
}

void coredata_report_sort(CoredataValidationReport &report) {
    struct IssueLess {
        bool operator()(const CoredataValidationIssue &a,
                        const CoredataValidationIssue &b) const {
            int ar = severity_rank(a.severity);
            int br = severity_rank(b.severity);
            if (ar != br) return ar < br;
            ar = class_rank(a.cls);
            br = class_rank(b.cls);
            if (ar != br) return ar < br;
            if (a.path != b.path) return a.path < b.path;
            if (a.line != b.line) return a.line < b.line;
            if (a.code != b.code) return a.code < b.code;
            return a.message < b.message;
        }
    };
    std::sort(report.issues.begin(), report.issues.end(), IssueLess());
}

int coredata_report_exit_code(const CoredataValidationReport &report) {
    if (report.error_count == 0u) {
        return 0;
    }
    if (coredata_report_has_error_class(report, CORE_DATA_SCHEMA_ERROR)) return 10;
    if (coredata_report_has_error_class(report, CORE_DATA_REFERENCE_ERROR)) return 11;
    if (coredata_report_has_error_class(report, CORE_DATA_DETERMINISM_ERROR)) return 12;
    if (coredata_report_has_error_class(report, CORE_DATA_POLICY_ERROR)) return 13;
    if (coredata_report_has_error_class(report, CORE_DATA_RANGE_ERROR)) return 14;
    if (coredata_report_has_error_class(report, CORE_DATA_MIGRATION_ERROR)) return 15;
    return 10;
}

static void json_escape(const std::string &in, std::string &out) {
    size_t i;
    out.clear();
    for (i = 0u; i < in.size(); ++i) {
        char c = in[i];
        switch (c) {
            case '\\': out += "\\\\"; break;
            case '"': out += "\\\""; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default: out.push_back(c); break;
        }
    }
}

static const char *class_name(CoredataValidationClass cls) {
    switch (cls) {
        case CORE_DATA_SCHEMA_ERROR: return "SCHEMA_ERROR";
        case CORE_DATA_REFERENCE_ERROR: return "REFERENCE_ERROR";
        case CORE_DATA_DETERMINISM_ERROR: return "DETERMINISM_ERROR";
        case CORE_DATA_POLICY_ERROR: return "POLICY_ERROR";
        case CORE_DATA_RANGE_ERROR: return "RANGE_ERROR";
        case CORE_DATA_MIGRATION_ERROR: return "MIGRATION_ERROR";
        default: return "UNKNOWN";
    }
}

static const char *severity_name(CoredataValidationSeverity sev) {
    return (sev == CORE_DATA_SEVERITY_WARNING) ? "WARNING" : "ERROR";
}

std::string coredata_report_text(const CoredataValidationReport &report) {
    std::ostringstream oss;
    size_t i;
    oss << "coredata_validate: mode=" << report.mode
        << " input=" << report.input_path
        << " errors=" << report.error_count
        << " warnings=" << report.warning_count << "\n";
    for (i = 0u; i < report.issues.size(); ++i) {
        const CoredataValidationIssue &iss = report.issues[i];
        oss << severity_name(iss.severity) << " "
            << class_name(iss.cls) << " "
            << iss.code;
        if (!iss.path.empty()) {
            oss << " " << iss.path;
            if (iss.line > 0) {
                oss << ":" << iss.line;
            }
        }
        if (!iss.message.empty()) {
            oss << " - " << iss.message;
        }
        oss << "\n";
    }
    return oss.str();
}

std::string coredata_report_json(const CoredataValidationReport &report) {
    std::ostringstream oss;
    size_t i;
    std::string esc;

    oss << "{";
    json_escape(report.tool_version, esc);
    oss << "\"tool_version\":\"" << esc << "\",";
    json_escape(report.mode, esc);
    oss << "\"mode\":\"" << esc << "\",";
    json_escape(report.input_path, esc);
    oss << "\"input_path\":\"" << esc << "\",";
    oss << "\"error_count\":" << report.error_count << ",";
    oss << "\"warning_count\":" << report.warning_count << ",";
    oss << "\"issues\":[";
    for (i = 0u; i < report.issues.size(); ++i) {
        const CoredataValidationIssue &iss = report.issues[i];
        if (i != 0u) {
            oss << ",";
        }
        oss << "{";
        oss << "\"severity\":\"" << severity_name(iss.severity) << "\",";
        oss << "\"class\":\"" << class_name(iss.cls) << "\",";
        json_escape(iss.code, esc);
        oss << "\"code\":\"" << esc << "\",";
        json_escape(iss.message, esc);
        oss << "\"message\":\"" << esc << "\",";
        json_escape(iss.path, esc);
        oss << "\"path\":\"" << esc << "\",";
        oss << "\"line\":" << (iss.line < 0 ? 0 : iss.line);
        oss << "}";
    }
    oss << "]}";
    return oss.str();
}

std::vector<unsigned char> coredata_report_tlv(const CoredataValidationReport &report) {
    dom::core_tlv::TlvWriter w;
    size_t i;
    enum {
        TAG_SCHEMA_VERSION = 1u,
        TAG_TOOL_VERSION = 2u,
        TAG_MODE = 3u,
        TAG_INPUT = 4u,
        TAG_ERROR_COUNT = 5u,
        TAG_WARNING_COUNT = 6u,
        TAG_ISSUE = 7u
    };
    enum {
        TAG_ISSUE_SEVERITY = 1u,
        TAG_ISSUE_CLASS = 2u,
        TAG_ISSUE_CODE = 3u,
        TAG_ISSUE_MESSAGE = 4u,
        TAG_ISSUE_PATH = 5u,
        TAG_ISSUE_LINE = 6u
    };

    w.add_u32(TAG_SCHEMA_VERSION, 1u);
    w.add_string(TAG_TOOL_VERSION, report.tool_version);
    w.add_string(TAG_MODE, report.mode);
    w.add_string(TAG_INPUT, report.input_path);
    w.add_u32(TAG_ERROR_COUNT, report.error_count);
    w.add_u32(TAG_WARNING_COUNT, report.warning_count);

    for (i = 0u; i < report.issues.size(); ++i) {
        const CoredataValidationIssue &iss = report.issues[i];
        dom::core_tlv::TlvWriter inner;
        inner.add_u32(TAG_ISSUE_SEVERITY, (u32)iss.severity);
        inner.add_u32(TAG_ISSUE_CLASS, (u32)iss.cls);
        inner.add_string(TAG_ISSUE_CODE, iss.code);
        inner.add_string(TAG_ISSUE_MESSAGE, iss.message);
        inner.add_string(TAG_ISSUE_PATH, iss.path);
        if (iss.line > 0) {
            inner.add_u32(TAG_ISSUE_LINE, (u32)iss.line);
        }
        w.add_container(TAG_ISSUE, inner.bytes());
    }

    return w.bytes();
}

bool coredata_report_has_error_class(const CoredataValidationReport &report,
                                     CoredataValidationClass cls) {
    size_t i;
    for (i = 0u; i < report.issues.size(); ++i) {
        if (report.issues[i].severity == CORE_DATA_SEVERITY_ERROR &&
            report.issues[i].cls == cls) {
            return true;
        }
    }
    return false;
}

bool coredata_report_has_io_error(const CoredataValidationReport &report) {
    size_t i;
    for (i = 0u; i < report.issues.size(); ++i) {
        if (report.issues[i].code == "file_error" ||
            report.issues[i].code == "open_failed" ||
            report.issues[i].code == "read_failed") {
            return true;
        }
    }
    return false;
}

} // namespace tools
} // namespace dom
