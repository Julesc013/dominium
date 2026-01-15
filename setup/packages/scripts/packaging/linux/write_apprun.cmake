if(NOT DEFINED OUT OR OUT STREQUAL "")
    message(FATAL_ERROR "write_apprun.cmake: OUT is required")
endif()

file(WRITE "${OUT}" "#!/bin/sh\nset -eu\nHERE=\"$(cd \"$(dirname \"$0\")\" && pwd)\"\nexec \"$HERE/bin/dominium-launcher\" --home=\"$HERE\" \"$@\"\n")

file(CHMOD "${OUT}"
    PERMISSIONS
        OWNER_READ OWNER_WRITE OWNER_EXECUTE
        GROUP_READ GROUP_EXECUTE
        WORLD_READ WORLD_EXECUTE)

