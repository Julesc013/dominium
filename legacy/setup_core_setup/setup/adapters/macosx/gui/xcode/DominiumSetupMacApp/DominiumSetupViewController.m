#import "DominiumSetupViewController.h"

static NSString *dsk_trimmed(NSTextField *field) {
    if (!field) {
        return @"";
    }
    return [[field stringValue] stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
}

static NSString *dsk_env_value(NSString *key) {
    NSDictionary<NSString *, NSString *> *env = [[NSProcessInfo processInfo] environment];
    NSString *value = env[key];
    return value ? value : @"";
}

static NSString *dsk_default_platform(void) {
#if defined(__arm64__)
    return @"macos-arm64";
#else
    return @"macos-x64";
#endif
}

@implementation DominiumSetupViewController

- (void)viewDidLoad {
    [super viewDidLoad];

    [self.operationPopup removeAllItems];
    [self.operationPopup addItemsWithTitles:@[@"install", @"upgrade", @"repair", @"uninstall", @"verify", @"status"]];

    [self.scopePopup removeAllItems];
    [self.scopePopup addItemsWithTitles:@[@"user", @"system", @"portable"]];

    [self.ownershipPopup removeAllItems];
    [self.ownershipPopup addItemsWithTitles:@[@"any", @"portable", @"pkg", @"steam"]];

    self.deterministicCheck.state = NSControlStateValueOn;
    self.statusLabel.stringValue = @"Ready.";

    {
        NSString *manifest = dsk_env_value(@"DOMINIUM_SETUP_MANIFEST");
        if (manifest.length > 0) {
            self.manifestField.stringValue = manifest;
        }
    }
    {
        NSString *platform = dsk_env_value(@"DOMINIUM_SETUP_PLATFORM");
        self.platformField.stringValue = platform.length > 0 ? platform : dsk_default_platform();
    }
}

- (NSString *)setupCliPath {
    NSString *cli = dsk_env_value(@"DOMINIUM_SETUP_CLI");
    return cli.length > 0 ? cli : @"dominium-setup";
}

- (NSString *)frontendId {
    NSString *value = dsk_env_value(@"DOMINIUM_SETUP_FRONTEND_ID");
    return value.length > 0 ? value : @"dominium-setup-macos-gui";
}

- (NSString *)sandboxRoot {
    NSString *root = dsk_env_value(@"DOMINIUM_SETUP_SANDBOX_ROOT");
    if (root.length > 0) {
        return root;
    }
    return [NSTemporaryDirectory() stringByAppendingPathComponent:@"dominium_setup_gui"];
}

- (BOOL)useFakeServices {
    NSString *flag = dsk_env_value(@"DOMINIUM_SETUP_USE_FAKE_SERVICES");
    if (flag.length == 0) {
        return dsk_env_value(@"DOMINIUM_SETUP_SANDBOX_ROOT").length > 0;
    }
    return ![flag isEqualToString:@"0"];
}

- (BOOL)ensureDirectory:(NSString *)path {
    if (path.length == 0) {
        return NO;
    }
    return [[NSFileManager defaultManager] createDirectoryAtPath:path
                                    withIntermediateDirectories:YES
                                                     attributes:nil
                                                          error:nil];
}

- (void)updateStatus:(NSString *)message {
    dispatch_async(dispatch_get_main_queue(), ^{
        self.statusLabel.stringValue = message ?: @"";
    });
}

- (NSMutableArray<NSString *> *)buildRequestArgsWithOutPath:(NSString *)outPath {
    NSString *manifest = dsk_trimmed(self.manifestField);
    if (manifest.length == 0) {
        [self updateStatus:@"Manifest path is required."];
        return nil;
    }

    NSMutableArray<NSString *> *args = [NSMutableArray array];
    [args addObject:@"request"];
    [args addObject:@"make"];
    [args addObject:@"--manifest"];
    [args addObject:manifest];

    [args addObject:@"--op"];
    [args addObject:self.operationPopup.selectedItem.title ?: @"install"];

    [args addObject:@"--scope"];
    [args addObject:self.scopePopup.selectedItem.title ?: @"user"];

    [args addObject:@"--ui-mode"];
    [args addObject:@"gui"];

    NSString *installRoot = dsk_trimmed(self.installRootField);
    if (installRoot.length > 0) {
        [args addObject:@"--root"];
        [args addObject:installRoot];
    }

    NSString *components = dsk_trimmed(self.componentsField);
    if (components.length > 0) {
        [args addObject:@"--components"];
        [args addObject:components];
    }

    NSString *exclude = dsk_trimmed(self.excludeComponentsField);
    if (exclude.length > 0) {
        [args addObject:@"--exclude"];
        [args addObject:exclude];
    }

    NSString *ownership = self.ownershipPopup.selectedItem.title ?: @"any";
    if (ownership.length > 0) {
        [args addObject:@"--ownership"];
        [args addObject:ownership];
    }

    NSString *requestedSplat = dsk_trimmed(self.requestedSplatField);
    if (requestedSplat.length > 0) {
        [args addObject:@"--requested-splat"];
        [args addObject:requestedSplat];
    }

    NSString *platform = dsk_trimmed(self.platformField);
    if (platform.length > 0) {
        [args addObject:@"--platform"];
        [args addObject:platform];
    }

    NSString *payloadRoot = dsk_trimmed(self.payloadRootField);
    if (payloadRoot.length > 0) {
        [args addObject:@"--payload-root"];
        [args addObject:payloadRoot];
    }

    [args addObject:@"--frontend-id"];
    [args addObject:[self frontendId]];

    [args addObject:@"--deterministic"];
    [args addObject:(self.deterministicCheck.state == NSControlStateValueOn) ? @"1" : @"0"];

    if (outPath.length > 0) {
        [args addObject:@"--out-request"];
        [args addObject:outPath];
    }

    if ([self useFakeServices]) {
        [args addObject:@"--use-fake-services"];
        [args addObject:[self sandboxRoot]];
    }

    return args;
}

- (int)runTaskWithArgs:(NSArray<NSString *> *)args
                    cwd:(NSString *)cwd
                 output:(NSString **)output {
    NSTask *task = [[NSTask alloc] init];
    [task setLaunchPath:[self setupCliPath]];
    [task setArguments:args];
    if (cwd.length > 0) {
        [task setCurrentDirectoryPath:cwd];
    }

    NSPipe *pipe = [NSPipe pipe];
    [task setStandardOutput:pipe];
    [task setStandardError:pipe];

    @try {
        [task launch];
    } @catch (NSException *ex) {
        if (output) {
            *output = [NSString stringWithFormat:@"Failed to launch: %@", ex.reason];
        }
        return 1;
    }

    [task waitUntilExit];
    if (output) {
        NSData *data = [[pipe fileHandleForReading] readDataToEndOfFile];
        *output = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
    }
    return (int)task.terminationStatus;
}

- (IBAction)exportRequestPressed:(id)sender {
    (void)sender;
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        NSString *sandbox = [self sandboxRoot];
        [self ensureDirectory:sandbox];
        NSString *requestPath = [sandbox stringByAppendingPathComponent:@"install_request.tlv"];
        NSMutableArray<NSString *> *args = [self buildRequestArgsWithOutPath:requestPath];
        if (!args) {
            return;
        }

        NSString *output = nil;
        [self updateStatus:@"Exporting request..."];
        int code = [self runTaskWithArgs:args cwd:sandbox output:&output];
        if (code == 0) {
            [self updateStatus:[NSString stringWithFormat:@"Request exported: %@", requestPath]];
        } else {
            NSString *msg = output.length > 0 ? output : @"Request export failed.";
            [self updateStatus:msg];
        }
    });
}

- (IBAction)runPressed:(id)sender {
    (void)sender;
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        NSString *sandbox = [self sandboxRoot];
        [self ensureDirectory:sandbox];
        NSString *requestPath = [sandbox stringByAppendingPathComponent:@"install_request.tlv"];
        NSString *planPath = [sandbox stringByAppendingPathComponent:@"install_plan.tlv"];
        NSString *statePath = [sandbox stringByAppendingPathComponent:@"installed_state.tlv"];
        NSString *auditPath = [sandbox stringByAppendingPathComponent:@"setup_audit.tlv"];
        NSString *journalPath = [sandbox stringByAppendingPathComponent:@"job_journal.tlv"];
        NSMutableArray<NSString *> *requestArgs = [self buildRequestArgsWithOutPath:requestPath];
        if (!requestArgs) {
            return;
        }

        NSString *output = nil;
        [self updateStatus:@"Building request..."];
        if ([self runTaskWithArgs:requestArgs cwd:sandbox output:&output] != 0) {
            [self updateStatus:output.length > 0 ? output : @"Request build failed."];
            return;
        }

        NSMutableArray<NSString *> *planArgs = [NSMutableArray array];
        [planArgs addObject:@"plan"];
        [planArgs addObject:@"--manifest"];
        [planArgs addObject:dsk_trimmed(self.manifestField)];
        [planArgs addObject:@"--request"];
        [planArgs addObject:requestPath];
        [planArgs addObject:@"--out-plan"];
        [planArgs addObject:planPath];
        if ([self useFakeServices]) {
            [planArgs addObject:@"--use-fake-services"];
            [planArgs addObject:[self sandboxRoot]];
        }

        [self updateStatus:@"Planning..."];
        if ([self runTaskWithArgs:planArgs cwd:sandbox output:&output] != 0) {
            [self updateStatus:output.length > 0 ? output : @"Plan failed."];
            return;
        }

        NSMutableArray<NSString *> *applyArgs = [NSMutableArray array];
        [applyArgs addObject:@"apply"];
        [applyArgs addObject:@"--plan"];
        [applyArgs addObject:planPath];
        [applyArgs addObject:@"--out-state"];
        [applyArgs addObject:statePath];
        [applyArgs addObject:@"--out-audit"];
        [applyArgs addObject:auditPath];
        [applyArgs addObject:@"--out-journal"];
        [applyArgs addObject:journalPath];
        if ([self useFakeServices]) {
            [applyArgs addObject:@"--use-fake-services"];
            [applyArgs addObject:[self sandboxRoot]];
        }

        [self updateStatus:@"Applying..."];
        if ([self runTaskWithArgs:applyArgs cwd:sandbox output:&output] != 0) {
            [self updateStatus:output.length > 0 ? output : @"Apply failed."];
            return;
        }

        [self updateStatus:@"Setup complete."];
    });
}

@end
