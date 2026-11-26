
[Setup]
AppId={{7D8B9C20-2E14-4D42-A5F1-9061E67B4C32}
AppName=PANELMSE
AppVersion=0.9.0
AppPublisher=Equipo PANELMSE
SetupIconFile=src\panelmse\assets\PANELMSE.ico

DefaultDirName={localappdata}\Programs\PANELMSE
DefaultGroupName=PANELMSE
DisableProgramGroupPage=yes
PrivilegesRequired=lowest

OutputDir=installer_output
OutputBaseFilename=PANELMSE_Instalador


Compression=lzma2
SolidCompression=yes
WizardStyle=modern

UninstallDisplayIcon={app}\PANELMSE.ico

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "dist\PANELMSE\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "src\panelmse\assets\PANELMSE.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{autodesktop}\PANELMSE"; Filename: "{app}\PANELMSE.exe"; IconFilename: "{app}\PANELMSE.ico"; IconIndex: 0

Name: "{autoprograms}\PANELMSE\PANELMSE"; Filename: "{app}\PANELMSE.exe"; IconFilename: "{app}\PANELMSE.ico"; IconIndex: 0

Name: "{autoprograms}\PANELMSE\Desinstalar PANELMSE"; Filename: "{uninstallexe}"


[Run]
Filename: "{app}\PANELMSE.exe"; Description: "Iniciar PANELMSE"; Flags: postinstall nowait skipifsilent
