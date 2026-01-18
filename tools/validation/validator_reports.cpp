/*
FILE: tools/validation/validator_reports.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validation
RESPONSIBILITY: Formats validation reports as JSON and text.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Report output is deterministic for a given report.
*/
#include "validator_reports.h"

#include <sstream>

namespace dom {
namespace validation {

static std::string json_escape(const std::string& value) {
    std::string out;
    out.reserve(value.size());
    for (size_t i = 0u; i < value.size(); ++i) {
        const char c = value[i];
        switch (c) {
            case '\\': out += "\\\\"; break;
            case '"': out += "\\\""; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default: out.push_back(c); break;
        }
    }
    return out;
}

std::string report_to_json(const ValidationReport& report) {
    std::ostringstream out;
    out << "{";
    out << "\"ok\":" << (report.error_count == 0u ? "true" : "false") << ",";
    out << "\"errors\":" << report.error_count << ",";
    out << "\"warnings\":" << report.warning_count << ",";
    out << "\"issues\":[";
    for (size_t i = 0u; i < report.issues.size(); ++i) {
        const ValidationIssue& issue = report.issues[i];
        if (i > 0u) {
            out << ",";
        }
        out << "{";
        out << "\"rule_id\":\"" << json_escape(issue.rule_id) << "\",";
        out << "\"severity\":\"" << (issue.severity == VAL_SEV_ERROR ? "error" : "warn") << "\",";
        out << "\"path\":\"" << json_escape(issue.path) << "\",";
        out << "\"line\":" << issue.line << ",";
        out << "\"message\":\"" << json_escape(issue.message) << "\",";
        out << "\"remediation\":\"" << json_escape(issue.remediation) << "\"";
        out << "}";
    }
    out << "]}";
    return out.str();
}

std::string report_to_text(const ValidationReport& report) {
    std::ostringstream out;
    if (report.issues.empty()) {
        out << "Validation OK.\n";
        return out.str();
    }
    for (size_t i = 0u; i < report.issues.size(); ++i) {
        const ValidationIssue& issue = report.issues[i];
        out << issue.rule_id << ": " << issue.message << "\n";
        out << "  " << issue.path << ":" << issue.line << "\n";
        out << "Fix: " << issue.remediation << "\n";
    }
    return out.str();
}

} /* namespace validation */
} /* namespace dom */
