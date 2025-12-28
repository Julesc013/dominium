/*
FILE: source/dominium/setup/installers/macos_classic/gui/classic_installer_app/src/resources.r
MODULE: Dominium Setup (Classic GUI)
PURPOSE: Classic dialog resources (period-correct wizard layout).
*/

resource 'DLOG' (128, "Welcome") {
    {40, 40, 220, 360},
    dBoxProc,
    visible,
    noGoAway,
    0x0,
    "Welcome"
};

resource 'DITL' (128, "Welcome Items") {
    { /* array DITL */
        { {20, 20, 80, 300}, StaticText { enabled, "Welcome to the Dominium Setup." } },
        { {150, 230, 170, 300}, Button { enabled, "Continue" } },
        { {150, 140, 170, 210}, Button { enabled, "Cancel" } }
    }
};

resource 'DLOG' (129, "Install Type") {
    {40, 40, 240, 360},
    dBoxProc,
    visible,
    noGoAway,
    0x0,
    "Install Type"
};

resource 'DITL' (129, "Install Type Items") {
    {
        { {20, 20, 40, 300}, StaticText { enabled, "Choose an installation type:" } },
        { {60, 40, 80, 300}, RadioButton { enabled, "Easy Install" } },
        { {90, 40, 110, 300}, RadioButton { enabled, "Custom Install" } },
        { {180, 230, 200, 300}, Button { enabled, "Continue" } },
        { {180, 140, 200, 210}, Button { enabled, "Back" } }
    }
};

resource 'DLOG' (130, "Destination") {
    {40, 40, 240, 360},
    dBoxProc,
    visible,
    noGoAway,
    0x0,
    "Destination"
};

resource 'DITL' (130, "Destination Items") {
    {
        { {20, 20, 40, 300}, StaticText { enabled, "Select a destination folder." } },
        { {60, 20, 80, 300}, StaticText { enabled, "Applications:Dominium" } },
        { {110, 230, 130, 300}, Button { enabled, "Choose..." } },
        { {180, 230, 200, 300}, Button { enabled, "Continue" } },
        { {180, 140, 200, 210}, Button { enabled, "Back" } }
    }
};

resource 'DLOG' (131, "Components") {
    {40, 40, 260, 360},
    dBoxProc,
    visible,
    noGoAway,
    0x0,
    "Components"
};

resource 'DITL' (131, "Components Items") {
    {
        { {20, 20, 40, 300}, StaticText { enabled, "Select components to install." } },
        { {60, 40, 80, 300}, CheckBox { enabled, "Core Runtime" } },
        { {90, 40, 110, 300}, CheckBox { enabled, "Tools" } },
        { {200, 230, 220, 300}, Button { enabled, "Continue" } },
        { {200, 140, 220, 210}, Button { enabled, "Back" } }
    }
};

resource 'DLOG' (132, "Summary") {
    {40, 40, 240, 360},
    dBoxProc,
    visible,
    noGoAway,
    0x0,
    "Summary"
};

resource 'DITL' (132, "Summary Items") {
    {
        { {20, 20, 60, 300}, StaticText { enabled, "Ready to install." } },
        { {180, 230, 200, 300}, Button { enabled, "Install" } },
        { {180, 140, 200, 210}, Button { enabled, "Back" } }
    }
};

resource 'DLOG' (133, "Progress") {
    {40, 40, 200, 360},
    dBoxProc,
    visible,
    noGoAway,
    0x0,
    "Progress"
};

resource 'DITL' (133, "Progress Items") {
    {
        { {20, 20, 40, 300}, StaticText { enabled, "Installing..." } },
        { {60, 20, 80, 300}, UserItem { enabled } }
    }
};

resource 'DLOG' (134, "Complete") {
    {40, 40, 220, 360},
    dBoxProc,
    visible,
    noGoAway,
    0x0,
    "Complete"
};

resource 'DITL' (134, "Complete Items") {
    {
        { {20, 20, 60, 300}, StaticText { enabled, "Installation complete." } },
        { {150, 230, 170, 300}, Button { enabled, "Finish" } }
    }
};
