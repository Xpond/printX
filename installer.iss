[Setup]
AppId={{C7F8B843-FB03-43BC-9CD0-B04303E88C80}
AppName=PrintShop Tools
AppVersion=0.1.2
AppPublisher=PrintShop Tools
AppPublisherURL=https://github.com/Xpond/printX
DefaultDirName={localappdata}\Programs\PrintShop Tools
DefaultGroupName=PrintShop Tools
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=dist\installer
OutputBaseFilename=PrintShop-Tools-Setup
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\PrintShop Tools.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "dist\PrintShop Tools\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PrintShop Tools"; Filename: "{app}\PrintShop Tools.exe"
Name: "{group}\Sample files"; Filename: "{app}\samples"
Name: "{autodesktop}\PrintShop Tools"; Filename: "{app}\PrintShop Tools.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PrintShop Tools.exe"; Description: "Open PrintShop Tools"; Flags: nowait postinstall skipifsilent
