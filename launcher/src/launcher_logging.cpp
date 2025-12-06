#include "launcher_logging.h"

#include <iostream>

void launcher_log_info(const std::string &msg)
{
    std::cout << "[launcher] " << msg << std::endl;
}

void launcher_log_error(const std::string &msg)
{
    std::cerr << "[launcher:error] " << msg << std::endl;
}
