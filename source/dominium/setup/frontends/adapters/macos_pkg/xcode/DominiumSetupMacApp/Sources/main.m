#import <Cocoa/Cocoa.h>

static int has_flag(int argc, const char **argv, const char *flag) {
    int i;
    if (!flag) {
        return 0;
    }
    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], flag) == 0) {
            return 1;
        }
    }
    return 0;
}

static const char *get_arg_value(int argc, const char **argv, const char *name) {
    int i;
    if (!name) {
        return NULL;
    }
    for (i = 1; i < argc - 1; ++i) {
        if (strcmp(argv[i], name) == 0) {
            return argv[i + 1];
        }
    }
    return NULL;
}

static NSString *env_value(NSString *key) {
    NSDictionary<NSString *, NSString *> *env = [[NSProcessInfo processInfo] environment];
    NSString *value = env[key];
    return value ? value : @"";
}

static NSString *resolve_cli_path(const char *override) {
    if (override && override[0]) {
        return [NSString stringWithUTF8String:override];
    }
    NSString *cli = env_value(@"DOMINIUM_SETUP_CLI");
    return cli.length > 0 ? cli : @"dominium-setup";
}

static NSString *resolve_sandbox_root(const char *override) {
    if (override && override[0]) {
        return [NSString stringWithUTF8String:override];
    }
    NSString *root = env_value(@"DOMINIUM_SETUP_SANDBOX_ROOT");
    if (root.length > 0) {
        return root;
    }
    return [NSTemporaryDirectory() stringByAppendingPathComponent:@"dominium_setup_gui_cli"];
}

static BOOL use_fake_services(void) {
    NSString *flag = env_value(@"DOMINIUM_SETUP_USE_FAKE_SERVICES");
    if (flag.length == 0) {
        return env_value(@"DOMINIUM_SETUP_SANDBOX_ROOT").length > 0;
    }
    return ![flag isEqualToString:@"0"];
}

static void print_usage(void) {
    fprintf(stderr,
            "DominiumSetupMacApp --export-request --manifest <path> --op <install|upgrade|repair|uninstall|verify|status>\n"
            "  --scope <user|system|portable> [--components <csv>] [--exclude <csv>] [--root <path>]\n"
            "  [--ownership <any|portable|pkg|steam>] [--requested-splat <id>] [--platform <triple>]\n"
            "  [--payload-root <path>] [--frontend-id <id>] [--deterministic 0|1]\n"
            "  [--out-request <path>] [--sandbox-root <dir>] [--setup-cli <path>]\n");
}

static int run_export_request(int argc, const char **argv) {
    const char *manifest = get_arg_value(argc, argv, "--manifest");
    const char *op = get_arg_value(argc, argv, "--op");
    const char *scope = get_arg_value(argc, argv, "--scope");
    const char *components = get_arg_value(argc, argv, "--components");
    const char *exclude = get_arg_value(argc, argv, "--exclude");
    const char *root = get_arg_value(argc, argv, "--root");
    const char *ownership = get_arg_value(argc, argv, "--ownership");
    const char *requested_splat = get_arg_value(argc, argv, "--requested-splat");
    const char *platform = get_arg_value(argc, argv, "--platform");
    const char *payload_root = get_arg_value(argc, argv, "--payload-root");
    const char *frontend_id = get_arg_value(argc, argv, "--frontend-id");
    const char *deterministic = get_arg_value(argc, argv, "--deterministic");
    const char *out_request = get_arg_value(argc, argv, "--out-request");
    const char *sandbox_root = get_arg_value(argc, argv, "--sandbox-root");
    const char *cli_override = get_arg_value(argc, argv, "--setup-cli");

    if (!manifest || !op || !scope) {
        print_usage();
        return 2;
    }

    @autoreleasepool {
        NSString *sandbox = resolve_sandbox_root(sandbox_root);
        [[NSFileManager defaultManager] createDirectoryAtPath:sandbox
                                  withIntermediateDirectories:YES
                                                   attributes:nil
                                                        error:nil];

        NSString *requestPath = out_request && out_request[0]
            ? [NSString stringWithUTF8String:out_request]
            : [sandbox stringByAppendingPathComponent:@"install_request.tlv"];

        NSMutableArray<NSString *> *args = [NSMutableArray array];
        [args addObject:@"request"];
        [args addObject:@"make"];
        [args addObject:@"--manifest"];
        [args addObject:[NSString stringWithUTF8String:manifest]];
        [args addObject:@"--op"];
        [args addObject:[NSString stringWithUTF8String:op]];
        [args addObject:@"--scope"];
        [args addObject:[NSString stringWithUTF8String:scope]];
        [args addObject:@"--ui-mode"];
        [args addObject:@"gui"];

        if (components && components[0]) {
            [args addObject:@"--components"];
            [args addObject:[NSString stringWithUTF8String:components]];
        }
        if (exclude && exclude[0]) {
            [args addObject:@"--exclude"];
            [args addObject:[NSString stringWithUTF8String:exclude]];
        }
        if (root && root[0]) {
            [args addObject:@"--root"];
            [args addObject:[NSString stringWithUTF8String:root]];
        }
        if (ownership && ownership[0]) {
            [args addObject:@"--ownership"];
            [args addObject:[NSString stringWithUTF8String:ownership]];
        }
        if (requested_splat && requested_splat[0]) {
            [args addObject:@"--requested-splat"];
            [args addObject:[NSString stringWithUTF8String:requested_splat]];
        }
        if (platform && platform[0]) {
            [args addObject:@"--platform"];
            [args addObject:[NSString stringWithUTF8String:platform]];
        }
        if (payload_root && payload_root[0]) {
            [args addObject:@"--payload-root"];
            [args addObject:[NSString stringWithUTF8String:payload_root]];
        }

        [args addObject:@"--frontend-id"];
        [args addObject:(frontend_id && frontend_id[0])
            ? [NSString stringWithUTF8String:frontend_id]
            : @"dominium-setup-macos-gui"];
        [args addObject:@"--deterministic"];
        [args addObject:(deterministic && deterministic[0])
            ? [NSString stringWithUTF8String:deterministic]
            : @"1"];
        [args addObject:@"--out-request"];
        [args addObject:requestPath];

        if (use_fake_services()) {
            [args addObject:@"--use-fake-services"];
            [args addObject:sandbox];
        }

        NSTask *task = [[NSTask alloc] init];
        [task setLaunchPath:resolve_cli_path(cli_override)];
        [task setArguments:args];
        [task setCurrentDirectoryPath:sandbox];
        @try {
            [task launch];
        } @catch (NSException *ex) {
            fprintf(stderr, "Failed to launch: %s\n", ex.reason.UTF8String);
            return 1;
        }
        [task waitUntilExit];
        return (int)task.terminationStatus;
    }
}

int main(int argc, const char **argv) {
    if (has_flag(argc, argv, "--export-request")) {
        return run_export_request(argc, argv);
    }
    return NSApplicationMain(argc, argv);
}
