#ifndef DOM_BUILD_VERSION_H
#define DOM_BUILD_VERSION_H

/* Fallback build/version metadata for dom_core_version. */
#ifndef DOM_VERSION_SEMVER
#define DOM_VERSION_SEMVER "0.0.0"
#endif

#ifndef DOM_BUILD_NUMBER
#define DOM_BUILD_NUMBER 0
#endif

#ifndef DOM_STRINGIFY
#define DOM_STRINGIFY_HELPER(x) #x
#define DOM_STRINGIFY(x) DOM_STRINGIFY_HELPER(x)
#endif

#ifndef DOM_VERSION_BUILD_STR
#define DOM_VERSION_BUILD_STR DOM_VERSION_SEMVER " (build " DOM_STRINGIFY(DOM_BUILD_NUMBER) ")"
#endif

#endif /* DOM_BUILD_VERSION_H */
