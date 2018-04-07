; rpcalc-user.iss

; Inno Setup installer script for rpCalc, an RPN calculator
; This will install for a single user, no admin rights are required.

[Setup]
AppName=rpCalc
AppVersion=0.8.2
DefaultDirName={userappdata}\rpCalc
DefaultGroupName=rpCalc
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=rpcalc-0.8.2-install-user
PrivilegesRequired=lowest
SetupIconFile=rpcalc.ico
Uninstallable=IsTaskSelected('adduninstall')
UninstallDisplayIcon={app}\rpcalc.exe,0

[Tasks]
Name: "startmenu"; Description: "Add start menu shortcuts"
Name: "deskicon"; Description: "Add a desktop shortcut"
Name: "adduninstall"; Description: "Create an uninstaller"
Name: "source"; Description: "Include source code"
Name: "portable"; Description: "Use portable config file"; Flags: unchecked

[Files]
Source: "rpcalc.exe"; DestDir: "{app}"
Source: "python35.zip"; DestDir: "{app}"
Source: "*.dll"; DestDir: "{app}"
Source: "*.pyd"; DestDir: "{app}"
Source: "imageformats\*.dll"; DestDir: "{app}\imageformats"
Source: "platforms\*.dll"; DestDir: "{app}\platforms"
Source: "doc\*.html"; DestDir: "{app}\doc"
Source: "doc\LICENSE"; DestDir: "{app}\doc"
Source: "icons\*.png"; DestDir: "{app}\icons"
Source: "source\*.py"; DestDir: "{app}\source"; Tasks: "source"
Source: "rpcalc.ico"; DestDir: "{app}"; Tasks: "source"
Source: "*.iss"; DestDir: "{app}"; Tasks: "source"
Source: "rpcalc.ini"; DestDir: "{app}"; Tasks: "portable"

[Icons]
Name: "{userstartmenu}\rpCalc"; Filename: "{app}\rpcalc.exe"; \
      WorkingDir: "{app}"; Tasks: "startmenu"
Name: "{group}\rpCalc"; Filename: "{app}\rpcalc.exe"; \
      WorkingDir: "{app}"; Tasks: "startmenu"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"; Tasks: "startmenu"
Name: "{userdesktop}\rpCalc"; Filename: "{app}\rpcalc.exe"; \
      WorkingDir: "{app}"; Tasks: "deskicon"
