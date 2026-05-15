# libs Abi Build Scan

## Status

- Scan type: `abi_build_scan`
- Findings: 1887
- Moves/rewrites applied: `false`

## Markers Found

- `libs/CMakeLists.txt:3` add_library
- `libs/CMakeLists.txt:5` CMAKE
- `libs/CMakeLists.txt:7` add_library
- `libs/CMakeLists.txt:9` add_library
- `libs/CMakeLists.txt:11` CMAKE
- `libs/CMakeLists.txt:13` add_library
- `libs/CMakeLists.txt:15` add_library
- `libs/CMakeLists.txt:17` CMAKE
- `libs/CMakeLists.txt:19` add_library
- `libs/CMakeLists.txt:21` add_library
- `libs/CMakeLists.txt:23` CMAKE
- `libs/CMakeLists.txt:25` add_library
- `libs/CMakeLists.txt:27` contract
- `libs/CMakeLists.txt:28` appcore
- `libs/appcore/CMakeLists.txt:3` add_library
- `libs/appcore/CMakeLists.txt:3` appcore
- `libs/appcore/CMakeLists.txt:4` appcore
- `libs/appcore/CMakeLists.txt:5` appcore
- `libs/appcore/CMakeLists.txt:6` appcore
- `libs/appcore/CMakeLists.txt:7` appcore
- `libs/appcore/CMakeLists.txt:8` appcore
- `libs/appcore/CMakeLists.txt:11` appcore
- `libs/appcore/CMakeLists.txt:12` ui_bind
- `libs/appcore/CMakeLists.txt:13` ui_bind
- `libs/appcore/CMakeLists.txt:16` appcore
- `libs/appcore/CMakeLists.txt:16` public
- `libs/appcore/CMakeLists.txt:17` CMAKE
- `libs/appcore/CMakeLists.txt:18` CMAKE
- `libs/appcore/CMakeLists.txt:21` appcore
- `libs/appcore/CMakeLists.txt:27` add_library
- `libs/appcore/CMakeLists.txt:27` appcore
- `libs/appcore/command/command_dispatch.c:2` appcore
- `libs/appcore/command/command_dispatch.c:7` #include
- `libs/appcore/command/command_dispatch.c:9` appcore
- `libs/appcore/command/command_registry.c:2` appcore
- `libs/appcore/command/command_registry.c:7` #include
- `libs/appcore/command/command_registry.c:8` #include
- `libs/appcore/command/command_registry.c:31` struct
- `libs/appcore/command/command_registry.c:38` schema
- `libs/appcore/command/command_registry.c:40` schema
- `libs/appcore/command/command_registry.c:42` ABI
- `libs/appcore/command/command_registry.c:42` schema
- `libs/appcore/command/command_registry.c:44` schema
- `libs/appcore/command/command_registry.c:46` schema
- `libs/appcore/command/command_registry.c:48` schema
- `libs/appcore/command/command_registry.c:50` schema
- `libs/appcore/command/command_registry.c:52` schema
- `libs/appcore/command/command_registry.c:54` schema
- `libs/appcore/command/command_registry.c:56` schema
- `libs/appcore/command/command_registry.c:58` schema

## Highest-Risk Files

- `libs/CMakeLists.txt`
- `libs/appcore/CMakeLists.txt`
- `libs/appcore/command/command_dispatch.c`
- `libs/appcore/command/command_registry.c`
- `libs/appcore/command/command_registry.h`
- `libs/appcore/discover/appcore_discover.c`
- `libs/appcore/discover/appcore_discover.h`
- `libs/appcore/invoke/appcore_invoke.c`
- `libs/appcore/invoke/appcore_invoke.h`
- `libs/appcore/output/appcore_output.c`
- `libs/appcore/output/appcore_output.h`
- `libs/appcore/profile/appcore_profile.c`
- `libs/appcore/profile/appcore_profile.h`
- `libs/appcore/repox/appcore_repox.c`
- `libs/appcore/repox/appcore_repox.h`
- `libs/appcore/ui_bind/ui_accessibility_map.c`
- `libs/appcore/ui_bind/ui_accessibility_map.h`
- `libs/appcore/ui_bind/ui_command_binding_table.c`
- `libs/appcore/ui_bind/ui_command_binding_table.h`
- `libs/appcore/ui_bind/ui_localisation_usage_report.json`
- `libs/appcore/validate/appcore_validate.c`
- `libs/appcore/validate/appcore_validate.h`
- `libs/build_identity/build_identity.c`
- `libs/build_identity/CMakeLists.txt`
- `libs/build_identity/include/dom_build_identity/build_identity.h`

## Unknowns

- preserve_unknown entries: 103

## Future Validator Needs

Dedicated validators are required before moving any sensitive files from this root.
