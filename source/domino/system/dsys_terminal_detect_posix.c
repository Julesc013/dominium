#include "domino/system/dsys.h"

#include <unistd.h>

int dsys_running_in_terminal(void)
{
    int tty_in  = isatty(0); /* STDIN_FILENO */
    int tty_out = isatty(1); /* STDOUT_FILENO */
    return (tty_in || tty_out) ? 1 : 0;
}
