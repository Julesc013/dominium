#import <Cocoa/Cocoa.h>

@interface DominiumSetupViewController : NSViewController

@property (weak) IBOutlet NSTextField *manifestField;
@property (weak) IBOutlet NSPopUpButton *operationPopup;
@property (weak) IBOutlet NSPopUpButton *scopePopup;
@property (weak) IBOutlet NSTextField *installRootField;
@property (weak) IBOutlet NSTextField *componentsField;
@property (weak) IBOutlet NSTextField *excludeComponentsField;
@property (weak) IBOutlet NSPopUpButton *ownershipPopup;
@property (weak) IBOutlet NSTextField *requestedSplatField;
@property (weak) IBOutlet NSTextField *platformField;
@property (weak) IBOutlet NSTextField *payloadRootField;
@property (weak) IBOutlet NSButton *deterministicCheck;
@property (weak) IBOutlet NSButton *offlineCheck;
@property (weak) IBOutlet NSTextField *statusLabel;

- (IBAction)exportRequestPressed:(id)sender;
- (IBAction)runPressed:(id)sender;

@end
