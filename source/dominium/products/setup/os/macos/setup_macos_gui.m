#import <Cocoa/Cocoa.h>

static NSString* dom_default_user_path(void)
{
    NSString* home = NSHomeDirectory();
    return [home stringByAppendingPathComponent:@"Library/Application Support/Dominium"];
}

static NSString* dom_default_system_path(void)
{
    return @"/Library/Application Support/Dominium";
}

static NSString* dom_default_portable_path(void)
{
    return [[NSFileManager defaultManager] currentDirectoryPath];
}

static NSString* dom_cli_path(void)
{
    NSString* bundled = [[NSBundle mainBundle] pathForResource:@"dominium-setup-cli" ofType:nil];
    if (bundled) {
        return bundled;
    }
    NSString* sibling = [[[NSBundle mainBundle] bundlePath] stringByAppendingPathComponent:@"Contents/MacOS/dominium-setup-cli"];
    if ([[NSFileManager defaultManager] isExecutableFileAtPath:sibling]) {
        return sibling;
    }
    return @"dominium-setup-cli";
}

@interface DomSetupController : NSObject <NSApplicationDelegate>
@property(nonatomic, strong) NSWindow* window;
@property(nonatomic, strong) NSPopUpButton* scopePopup;
@property(nonatomic, strong) NSTextField* pathField;
@property(nonatomic, strong) NSProgressIndicator* spinner;
@property(nonatomic, strong) NSTextField* statusLabel;
@property(nonatomic, assign) BOOL actionRunning;
@end

@implementation DomSetupController

- (void)applicationDidFinishLaunching:(NSNotification*)notification
{
    (void)notification;
    NSRect frame = NSMakeRect(0, 0, 560, 260);
    self.window = [[NSWindow alloc] initWithContentRect:frame
                                              styleMask:(NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskMiniaturizable)
                                                backing:NSBackingStoreBuffered
                                                  defer:NO];
    [self.window setTitle:@"Dominium Setup"];
    [self.window center];

    NSView* content = [self.window contentView];
    NSRect bounds = [content bounds];
    CGFloat left = 20.0;
    CGFloat top = NSMaxY(bounds) - 40.0;

    NSTextField* intro = [[NSTextField alloc] initWithFrame:NSMakeRect(left, top, 400, 18)];
    [intro setStringValue:@"Install, repair, or remove Dominium using the setup CLI."];
    [intro setEditable:NO];
    [intro setBezeled:NO];
    [intro setDrawsBackground:NO];
    [content addSubview:intro];

    top -= 26.0;
    NSTextField* scopeLabel = [[NSTextField alloc] initWithFrame:NSMakeRect(left, top, 60, 18)];
    [scopeLabel setStringValue:@"Scope:"];
    [scopeLabel setEditable:NO];
    [scopeLabel setBezeled:NO];
    [scopeLabel setDrawsBackground:NO];
    [content addSubview:scopeLabel];

    self.scopePopup = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(left + 70, top - 2, 300, 24)];
    [self.scopePopup addItemsWithTitles:@[
        @"Per-user (~/Library/Application Support/Dominium)",
        @"System (/Library/Application Support/Dominium)",
        @"Portable (custom folder)"
    ]];
    [self.scopePopup setTarget:self];
    [self.scopePopup setAction:@selector(scopeChanged:)];
    [content addSubview:self.scopePopup];
    [self.scopePopup selectItemAtIndex:0];

    top -= 32.0;
    NSTextField* pathLabel = [[NSTextField alloc] initWithFrame:NSMakeRect(left, top, 100, 18)];
    [pathLabel setStringValue:@"Install location:"];
    [pathLabel setEditable:NO];
    [pathLabel setBezeled:NO];
    [pathLabel setDrawsBackground:NO];
    [content addSubview:pathLabel];

    self.pathField = [[NSTextField alloc] initWithFrame:NSMakeRect(left + 110, top - 2, 320, 24)];
    [content addSubview:self.pathField];

    NSButton* browse = [[NSButton alloc] initWithFrame:NSMakeRect(left + 440, top - 4, 90, 28)];
    [browse setTitle:@"Browse…"];
    [browse setTarget:self];
    [browse setAction:@selector(browse:)];
    [content addSubview:browse];

    top -= 50.0;
    NSArray<NSString*>* actions = @[ @"Install", @"Repair", @"Uninstall", @"Verify" ];
    for (NSUInteger i = 0; i < [actions count]; ++i) {
        NSButton* button = [[NSButton alloc] initWithFrame:NSMakeRect(left + (i * 110), top, 100, 30)];
        [button setTitle:actions[i]];
        [button setButtonType:NSButtonTypeMomentaryPushIn];
        [button setBezelStyle:NSBezelStyleRounded];
        [button setTarget:self];
        [button setAction:@selector(triggerAction:)];
        [content addSubview:button];
    }

    top -= 36.0;
    self.spinner = [[NSProgressIndicator alloc] initWithFrame:NSMakeRect(left, top, 420, 12)];
    [self.spinner setStyle:NSProgressIndicatorSpinningStyle];
    [self.spinner setControlSize:NSControlSizeSmall];
    [self.spinner setDisplayedWhenStopped:NO];
    [content addSubview:self.spinner];

    top -= 22.0;
    self.statusLabel = [[NSTextField alloc] initWithFrame:NSMakeRect(left, top, 520, 18)];
    [self.statusLabel setStringValue:@"Ready"];
    [self.statusLabel setEditable:NO];
    [self.statusLabel setBezeled:NO];
    [self.statusLabel setDrawsBackground:NO];
    [content addSubview:self.statusLabel];

    [self updatePathForScope];
    [self.window makeKeyAndOrderFront:nil];
}

- (void)scopeChanged:(id)sender
{
    (void)sender;
    [self updatePathForScope];
}

- (void)browse:(id)sender
{
    (void)sender;
    NSOpenPanel* panel = [NSOpenPanel openPanel];
    [panel setCanChooseDirectories:YES];
    [panel setCanChooseFiles:NO];
    [panel setAllowsMultipleSelection:NO];
    [panel setMessage:@"Select install location"];
    [panel beginSheetModalForWindow:self.window completionHandler:^(NSModalResponse result) {
        if (result == NSModalResponseOK) {
            NSURL* url = [[panel URLs] firstObject];
            if (url) {
                [self.pathField setStringValue:[url path]];
            }
        }
    }];
}

- (void)triggerAction:(id)sender
{
    if (self.actionRunning) {
        return;
    }
    NSString* title = [(NSButton*)sender title];
    NSString* action = [title lowercaseString];
    [self startAction:action];
}

- (NSString*)scopeValue
{
    NSInteger idx = [self.scopePopup indexOfSelectedItem];
    switch (idx) {
        case 1: return @"system";
        case 2: return @"portable";
        default: return @"user";
    }
}

- (void)updatePathForScope
{
    NSString* path = nil;
    NSString* scope = [self scopeValue];
    if ([scope isEqualToString:@"system"]) {
        path = dom_default_system_path();
    } else if ([scope isEqualToString:@"portable"]) {
        path = dom_default_portable_path();
    } else {
        path = dom_default_user_path();
    }
    [self.pathField setStringValue:path];
}

- (void)setUIRunning:(BOOL)running
{
    self.actionRunning = running;
    [self.spinner setHidden:!running];
    if (running) {
        [self.spinner startAnimation:nil];
        [self.statusLabel setStringValue:@"Running dominium-setup-cli…"];
    } else {
        [self.spinner stopAnimation:nil];
    }
}

- (void)startAction:(NSString*)action
{
    NSString* cli = dom_cli_path();
    NSString* scope = [self scopeValue];
    NSString* targetDir = [self.pathField stringValue];

    if (targetDir.length == 0) {
        [self.statusLabel setStringValue:@"Choose an install location."];
        return;
    }

    [self setUIRunning:YES];

    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        NSTask* task = [[NSTask alloc] init];
        [task setLaunchPath:cli];
        [task setArguments:@[
            [NSString stringWithFormat:@"--scope=%@", scope],
            [NSString stringWithFormat:@"--action=%@", action],
            [NSString stringWithFormat:@"--dir=%@", targetDir]
        ]];

        NSPipe* pipe = [NSPipe pipe];
        [task setStandardOutput:pipe];
        [task setStandardError:pipe];

        __block NSData* outputData = nil;
        @try {
            [task launch];
            outputData = [[pipe fileHandleForReading] readDataToEndOfFile];
            [task waitUntilExit];
        } @catch (NSException* ex) {
            (void)ex;
        }

        int status = task.terminationStatus;
        NSString* output = [[NSString alloc] initWithData:outputData ?: [NSData data] encoding:NSUTF8StringEncoding];

        dispatch_async(dispatch_get_main_queue(), ^{
            [self setUIRunning:NO];
            if (status == 0) {
                [self.statusLabel setStringValue:@"Completed successfully."];
                NSAlert* alert = [[NSAlert alloc] init];
                [alert setMessageText:@"Dominium setup completed."];
                [alert setInformativeText:@"You can now launch Dominium from Applications or keep verifying installs here."];
                [alert addButtonWithTitle:@"OK"];
                [alert runModal];
            } else {
                [self.statusLabel setStringValue:@"Setup reported an error."];
                NSAlert* alert = [[NSAlert alloc] init];
                [alert setMessageText:@"dominium-setup-cli failed"];
                NSString* info = output.length > 0 ? output : @"Check logs or run the CLI from Terminal for details.";
                [alert setInformativeText:info];
                [alert addButtonWithTitle:@"OK"];
                [alert runModal];
            }
        });
    });
}

@end

int main(int argc, const char* argv[])
{
    @autoreleasepool {
        DomSetupController* controller = [[DomSetupController alloc] init];
        NSApplication* app = [NSApplication sharedApplication];
        [app setActivationPolicy:NSApplicationActivationPolicyRegular];
        [app setDelegate:controller];
        [app run];
    }
    return 0;
}
