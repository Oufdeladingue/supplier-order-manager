; Script Inno Setup pour Gestionnaire Commandes Fournisseurs
; Nécessite Inno Setup 6.x : https://jrsoftware.org/isinfo.php

#define MyAppName "Gestionnaire Commandes Fournisseurs"
#define MyAppVersion "1.0.5"
#define MyAppPublisher "M-Jardin"
#define MyAppExeName "SupplierOrderManager.exe"
#define MyAppURL "https://github.com/Oufdeladingue/supplier-order-manager"

[Setup]
; Informations de base
AppId={{F8A9B2C1-3D4E-5F6A-7B8C-9D0E1F2A3B4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Demander des privilèges admin pour installer dans Program Files
PrivilegesRequired=admin
; Sortie de la compilation
OutputDir=installer_output
OutputBaseFilename=SupplierOrderManager-Setup-v{#MyAppVersion}
; Icône de l'installeur
SetupIconFile=assets\logo\logo.ico
; Compression
Compression=lzma2/ultra64
SolidCompression=yes
; Interface moderne
WizardStyle=modern
; Désinstalleur
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; GroupDescription: "Raccourcis supplémentaires:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Créer un raccourci dans la barre de lancement rapide"; GroupDescription: "Raccourcis supplémentaires:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Exécutable principal
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Assets (si nécessaires - commenté car l'exe est standalone)
; Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Menu Démarrer
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Bureau (optionnel)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Barre de lancement rapide (optionnel, Windows 7 et antérieur)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Proposer de lancer l'application après l'installation
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
// Fonction pour vérifier si une ancienne version est installée
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

// Fonction pour vérifier si l'application est en cours d'exécution
function IsAppRunning(): Boolean;
var
  FWMIService: Variant;
  FSWbemLocator: Variant;
  FWbemObjectSet: Variant;
begin
  Result := false;
  try
    FSWbemLocator := CreateOleObject('WBEMScripting.SWbemLocator');
    FWMIService := FSWbemLocator.ConnectServer('', 'root\CIMV2', '', '');
    FWbemObjectSet := FWMIService.ExecQuery(Format('SELECT * FROM Win32_Process WHERE Name="%s"', ['{#MyAppExeName}']));
    Result := (FWbemObjectSet.Count > 0);
  except
  end;
end;

// Fonction appelée avant l'installation
function InitializeSetup(): Boolean;
var
  V: Integer;
  iResultCode: Integer;
  sUnInstallString: String;
begin
  Result := True;

  // Vérifier si l'application est en cours d'exécution
  if IsAppRunning() then
  begin
    MsgBox('L''application est actuellement en cours d''exécution. Veuillez la fermer avant de continuer.', mbError, MB_OK);
    Result := False;
    Exit;
  end;

  // Vérifier si une version antérieure est installée
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then
  begin
    V := MsgBox('Une version précédente est installée. Voulez-vous la désinstaller avant de continuer?', mbConfirmation, MB_YESNO or MB_DEFBUTTON1);
    if V = IDYES then
    begin
      sUnInstallString := RemoveQuotes(sUnInstallString);
      if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
        Result := True
      else
      begin
        MsgBox('La désinstallation de l''ancienne version a échoué. Code erreur: ' + IntToStr(iResultCode) + '.', mbError, MB_OK);
        Result := False;
      end;
    end
    else
      Result := False;
  end;
end;
