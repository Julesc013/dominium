include_guard(GLOBAL)

include("${CMAKE_CURRENT_LIST_DIR}/dominium_dist.cmake")

macro(dist_init)
    dominium_dist_init(${ARGN})
endmacro()

function(dist_set_role target role_dir)
    dominium_dist_set_role(${target} ROLE ${role_dir})
endfunction()
