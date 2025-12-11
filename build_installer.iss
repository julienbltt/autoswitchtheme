#define MyAppName "AutoSwitchTheme"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "NOVENTARIS"
#define MyAppURL "https://autoswitchtheme.noventaris.fr/"
#define MyAppExeName "autoswitchtheme.exe"

[Setup]
AppId={{4644540B-516F-4E7E-B442-7A01550F9C1E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
UsePreviousPrivileges=yes
Uninstallable=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
OutputDir=autoswitchtheme.setup
OutputBaseFilename=auto-switch-theme_{#MyAppVersion}_x86
SetupIconFile=assets\icon.ico
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
Compression=lzma2

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Lancer au démarrage de Windows"; GroupDescription: "Options de démarrage:"

[Files]
Source: "autoswitchtheme.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Dirs]
Name: "{commonappdata}\{#MyAppName}"; Permissions: users-full
Name: "{commonappdata}\{#MyAppName}\config"; Permissions: users-full
Name: "{commonappdata}\{#MyAppName}\logs"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{commonstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{commonappdata}\{#MyAppName}\logs"
Type: filesandordirs; Name: "{commonappdata}\{#MyAppName}\config"
Type: filesandordirs; Name: "{commonappdata}\{#MyAppName}"
Type: files; Name: "{commonstartup}\{#MyAppName}.lnk"
Type: files; Name: "{userstartup}\{#MyAppName}.lnk"

[Code]
// Vérifie si l'application est en cours d'exécution
function IsAppRunning(): Boolean;
var
  FSWbemLocator: Variant;
  FWMIService: Variant;
  FWbemObjectSet: Variant;
begin
  Result := False;
  try
    FSWbemLocator := CreateOleObject('WBEMScripting.SWbemLocator');
    FWMIService := FSWbemLocator.ConnectServer('', 'root\CIMV2', '', '');
    FWbemObjectSet := FWMIService.ExecQuery(
      Format('SELECT * FROM Win32_Process WHERE Name="%s"', ['{#MyAppExeName}'])
    );
    Result := (FWbemObjectSet.Count > 0);
  except
    Result := False;
  end;
end;

// Tente de fermer l'application
function CloseRunningApp(): Boolean;
var
  ResultCode: Integer;
  Counter: Integer;
begin
  Result := True;
  
  // Essayer de fermer proprement
  Exec('taskkill', '/IM {#MyAppExeName} /T', '', SW_HIDE, 
       ewWaitUntilTerminated, ResultCode);
  
  // Attendre 5 secondes max
  Counter := 0;
  while IsAppRunning() and (Counter < 10) do
  begin
    Sleep(500);
    Counter := Counter + 1;
  end;
  
  // Si toujours actif, forcer
  if IsAppRunning() then
  begin
    Exec('taskkill', '/IM {#MyAppExeName} /F /T', '', SW_HIDE, 
         ewWaitUntilTerminated, ResultCode);
    Sleep(1000);
  end;
  
  Result := not IsAppRunning();
end;

// Avant la désinstallation
function InitializeUninstall(): Boolean;
var
  Response: Integer;
begin
  Result := True;
  
  if IsAppRunning() then
  begin
    Response := MsgBox(
      '{#MyAppName} est actuellement en cours d''exécution.' + #13#10 + #13#10 +
      'L''application doit être fermée avant de continuer la désinstallation.' + #13#10 + #13#10 +
      'Voulez-vous la fermer automatiquement maintenant ?',
      mbConfirmation, 
      MB_YESNO
    );
    
    if Response = IDYES then
    begin
      if CloseRunningApp() then
      begin
        MsgBox('{#MyAppName} a été fermé avec succès.', mbInformation, MB_OK);
      end
      else
      begin
        MsgBox(
          'Impossible de fermer {#MyAppName}.' + #13#10 + #13#10 +
          'Veuillez fermer l''application manuellement puis relancer la désinstallation.',
          mbError, 
          MB_OK
        );
        Result := False;
      end;
    end
    else
    begin
      MsgBox('La désinstallation a été annulée.', mbInformation, MB_OK);
      Result := False;
    end;
  end;
end;

// Avant l'installation (optionnel)
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  
  if IsAppRunning() then
  begin
    if MsgBox(
      '{#MyAppName} est en cours d''exécution.' + #13#10 +
      'Voulez-vous le fermer pour continuer l''installation ?',
      mbConfirmation, MB_YESNO) = IDYES then
    begin
      if not CloseRunningApp() then
      begin
        Result := 'Impossible de fermer {#MyAppName}. Veuillez le fermer manuellement.';
      end;
    end
    else
    begin
      Result := 'Installation annulée.';
    end;
  end;
end;