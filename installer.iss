; ─────────────────────────────────────────────────────────────────────────────
; Google Maps Scraper — Inno Setup 6 Script
; Author:   Soubarna Karmakar
; Requires: Inno Setup 6  https://jrsoftware.org/isdl.php
; Usage:    Run build_windows.bat  OR  ISCC installer.iss
; ─────────────────────────────────────────────────────────────────────────────

#define AppName      "Google Maps Scraper"
#define AppVersion   "2.0"
#define AppPublisher "Soubarna Karmakar"
#define AppExe       "GoogleMapsScraper.exe"
#define AppURL       "https://github.com"
#define AppId        "{F8A12B3C-4D5E-6F78-9A0B-1C2D3E4F5A99}"

; ── [Setup] ──────────────────────────────────────────────────────────────────
[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Installation directory — user can change this in the wizard
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

; Allow non-admin install (no UAC prompt needed)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Installer appearance
WizardStyle=modern
SetupIconFile=assets\icon.ico

; Output
OutputDir=installer_output
OutputBaseFilename=GoogleMapsScraper_Setup_v{#AppVersion}
Compression=lzma2/max
SolidCompression=yes

; Splash / sidebar image (optional — must be 164x314 BMP)
; WizardImageFile=assets\installer_side.bmp
; WizardSmallImageFile=assets\installer_top.bmp

UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}

; ── [Languages] ──────────────────────────────────────────────────────────────
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; ── [Tasks] ───────────────────────────────────────────────────────────────────
[Tasks]
Name: "desktopicon";    Description: "Create a &Desktop shortcut";       GroupDescription: "Additional shortcuts:"
Name: "startmenuicon";  Description: "Add to &Start Menu";               GroupDescription: "Additional shortcuts:"; Flags: checkedonce

; ── [Files] ───────────────────────────────────────────────────────────────────
[Files]
; Copy the entire PyInstaller output folder into the installation directory
Source: "dist\GoogleMapsScraper\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

; ── [Icons] ───────────────────────────────────────────────────────────────────
[Icons]
; Start Menu
Name: "{group}\{#AppName}";                   Filename: "{app}\{#AppExe}"; \
    Tasks: startmenuicon
Name: "{group}\Uninstall {#AppName}";         Filename: "{uninstallexe}"; \
    Tasks: startmenuicon

; Desktop
Name: "{commondesktop}\{#AppName}";           Filename: "{app}\{#AppExe}"; \
    Tasks: desktopicon

; ── [Run] after install ───────────────────────────────────────────────────────
[Run]
; Offer to launch the app immediately after install
Filename: "{app}\{#AppExe}"; \
    Description: "Launch {#AppName} now"; \
    Flags: nowait postinstall skipifsilent

; ── [UninstallDelete] ─────────────────────────────────────────────────────────
[UninstallDelete]
; Remove any Excel exports left in the install folder
Type: files; Name: "{app}\google_maps_*.xlsx"

; ── [Code] — custom installer logic ──────────────────────────────────────────
[Code]

{ ─── Show a pre-install info page about Chromium download ─── }
function InitializeSetup(): Boolean;
var
  Res: Integer;
begin
  Result := True;

  { Warn the user that Chromium (~120 MB) will be downloaded on first launch }
  Res := MsgBox(
    'Welcome to Google Maps Scraper v{#AppVersion} Setup.' + #13#10 + #13#10 +
    'On the FIRST launch the app will automatically download' + #13#10 +
    'the Chromium browser (~120 MB). An internet connection' + #13#10 +
    'is required for that one-time setup.' + #13#10 + #13#10 +
    'Continue with installation?',
    mbConfirmation, MB_YESNO);

  if Res <> IDYES then
    Result := False;
end;
