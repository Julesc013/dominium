#ifndef DOMINO_VERSION_H
#define DOMINO_VERSION_H

#define DOMINO_VERSION_MAJOR 0
#define DOMINO_VERSION_MINOR 1
#define DOMINO_VERSION_PATCH 0

#define DOMINO_VERSION_STRING "0.1.0"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct domino_semver {
    int major;
    int minor;
    int patch;
} domino_semver;

typedef struct domino_semver_range {
    domino_semver min_version;
    domino_semver max_version;
    int has_min;
    int has_max;
} domino_semver_range;

int domino_semver_parse(const char* str, domino_semver* out);
int domino_semver_compare(const domino_semver* a, const domino_semver* b);
int domino_semver_in_range(const domino_semver* v,
                           const domino_semver_range* range);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_VERSION_H */
