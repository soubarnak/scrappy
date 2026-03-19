; ─────────────────────────────────────────────────────────────────────────────
; Scrappy — Inno Setup 6 Script
; Produces a fully self-contained installer — no Python, Node.js, or internet
; connection required on the end-user's machine.
;
; Bundled in the installer:
;   - Scrappy executable + all Python packages (PyInstaller bundle)
;   - React frontend (pre-built, served by FastAPI)
;   - Playwright Chromium browser (copied by build_windows.bat)
;   - Microsoft Edge WebView2 Standalone Installer (fully offline, ~170 MB)
;
; Author   : Soubarna Karmakar
; Requires : Inno Setup 6  https://jrsoftware.org/isdl.php
; Usage    : Run build_windows.bat  OR  ISCC installer.iss
; ─────────────────────────────────────────────────────────────────────────────

#define AppName      "Scrappy"
#define AppVersion   "2.0"
#define AppPublisher "Soubarna Karmakar"
#define AppExe       "Scrappy.exe"
#define AppURL       "https://github.com/soubarnak/scrappy"

; ── [Setup] ───────────────────────────────────────────────────────────────────
[Setup]
; Note: {{ escapes a literal { in Inno Setup string values
AppId={{F8A12B3C-4D5E-6F78-9A0B-1C2D3E4F5A99}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Installation directory
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

; Allow non-admin install (no UAC prompt)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Appearance
WizardStyle=modern
SetupIconFile=assets\icon.ico

; Output
OutputDir=installer_output
OutputBaseFilename=Scrappy_Setup_v{#AppVersion}
Compression=lzma2/max
SolidCompression=yes

UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}

; ── [Languages] ───────────────────────────────────────────────────────────────
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; ── [Tasks] ───────────────────────────────────────────────────────────────────
[Tasks]
Name: "desktopicon";   Description: "Create a &Desktop shortcut";  GroupDescription: "Additional shortcuts:"
Name: "startmenuicon"; Description: "Add to &Start Menu";          GroupDescription: "Additional shortcuts:"; Flags: checkedonce

; ── [Files] ───────────────────────────────────────────────────────────────────
[Files]
; Main app: entire PyInstaller output folder.
; Includes Python runtime, all packages, React build, and Playwright Chromium.
Source: "dist\Scrappy\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

; Edge WebView2 Standalone Installer — fully offline, no internet needed on target machine.
; Downloaded by build_windows.bat into redist\ (~170 MB).
; Only extracted and run if WebView2 is not already installed (registry check below).
Source: "redist\MicrosoftEdgeWebView2RuntimeInstallerX64.exe"; \
    DestDir: "{tmp}"; \
    Flags: deleteafterinstall; \
    Check: NeedsWebView2

; ── [Icons] ───────────────────────────────────────────────────────────────────
[Icons]
Name: "{group}\{#AppName}";            Filename: "{app}\{#AppExe}"; Tasks: startmenuicon
Name: "{group}\Uninstall {#AppName}";  Filename: "{uninstallexe}";  Tasks: startmenuicon
Name: "{commondesktop}\{#AppName}";    Filename: "{app}\{#AppExe}"; Tasks: desktopicon

; ── [Run] ─────────────────────────────────────────────────────────────────────
[Run]
; 1. Silently install Edge WebView2 Runtime if not already present.
;    Uses the fully offline standalone installer — no internet required on target machine.
Filename: "{tmp}\MicrosoftEdgeWebView2RuntimeInstallerX64.exe"; \
    Parameters: "/silent /install"; \
    StatusMsg: "Installing Microsoft Edge WebView2 Runtime..."; \
    Flags: waituntilterminated; \
    Check: NeedsWebView2

; 2. Offer to launch Scrappy right after install finishes.
Filename: "{app}\{#AppExe}"; \
    Description: "Launch {#AppName} now"; \
    Flags: nowait postinstall skipifsilent

; ── [UninstallDelete] ─────────────────────────────────────────────────────────
[UninstallDelete]
Type: files; Name: "{app}\scrappy_*.xlsx"

; ── [Code] ────────────────────────────────────────────────────────────────────
[Code]

{ Check whether Edge WebView2 Runtime is already installed.
  WebView2 records its version in the registry at one of two paths. }
function IsWebView2Installed(): Boolean;
var
  Version: String;
begin
  Result := False;

  { Per-user (HKCU) }
  if RegQueryStringValue(HKCU,
      'Software\Microsoft\EdgeUpdate\ClientState\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}',
      'pv', Version) then
    if (Version <> '') and (Version <> '0.0.0.0') then
    begin
      Result := True;
      Exit;
    end;

  { Machine-wide 32-bit view (HKLM) }
  if RegQueryStringValue(HKLM,
      'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\ClientState\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}',
      'pv', Version) then
    if (Version <> '') and (Version <> '0.0.0.0') then
    begin
      Result := True;
      Exit;
    end;
end;

{ Returns True when the WebView2 installer should run }
function NeedsWebView2(): Boolean;
begin
  Result := not IsWebView2Installed();
end;
