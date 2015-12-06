; rpcalc-all.iss

; Inno Setup installer script for rpCalc, an RPN calculator
; This will install for all users, admin rights are required.

[Setup]
AppName=rpCalc
AppVersion=0.7.1
DefaultDirName={pf}\rpCalc
DefaultGroupName=rpCalc
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=rpcalc-0.7.1-install-all
PrivilegesRequired=poweruser
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
Source: "library.zip"; DestDir: "{app}"
Source: "*.dll"; DestDir: "{app}"
Source: "*.pyd"; DestDir: "{app}"
Source: "doc\*.html"; DestDir: "{app}\doc"
Source: "doc\LICENSE"; DestDir: "{app}\doc"
Source: "icons\*.png"; DestDir: "{app}\icons"
Source: "source\*.py"; DestDir: "{app}\source"; Tasks: "source"
Source: "rpcalc.ico"; DestDir: "{app}"; Tasks: "source"
Source: "*.iss"; DestDir: "{app}"; Tasks: "source"
Source: "rpcalc.ini"; DestDir: "{app}"; Tasks: "portable"

[Icons]
Name: "{commonstartmenu}\rpCalc"; Filename: "{app}\rpcalc.exe"; \
      WorkingDir: "{app}"; Tasks: "startmenu"
Name: "{group}\rpCalc"; Filename: "{app}\rpcalc.exe"; \
      WorkingDir: "{app}"; Tasks: "startmenu"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"; Tasks: "startmenu"
Name: "{commondesktop}\rpCalc"; Filename: "{app}\rpcalc.exe"; \
      WorkingDir: "{app}"; Tasks: "deskicon"
