; BSM (BullShit Meter) NSIS Installer Script
; Creates Windows installer for BSM application

!include "MUI2.nsh"
!include "FileFunc.nsh"

; General definitions
!define PRODUCT_NAME "BSM - BullShit Meter"
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "BSM Development Team"
!define PRODUCT_WEB_SITE "https://github.com/bsm-app/bsm"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\BSM.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "..\..\assets\bsm.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "..\..\LICENSE"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Components page
!insertmacro MUI_PAGE_COMPONENTS
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\BSM.exe"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.md"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Installer attributes
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "BSM-${PRODUCT_VERSION}-setup.exe"
InstallDir "$PROGRAMFILES\BSM"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; Version information
VIProductVersion "${PRODUCT_VERSION}.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "© ${PRODUCT_PUBLISHER}"
VIAddVersionKey "FileDescription" "AI-powered fact checker and counter-argument generator"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"

Section "BSM Core (required)" SEC01
  SectionIn RO
  
  ; Set output path to installation directory
  SetOutPath "$INSTDIR"
  
  ; Copy application files
  File /r "..\..\dist\BSM\*.*"
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\BSM"
  CreateShortCut "$SMPROGRAMS\BSM\BSM.lnk" "$INSTDIR\BSM.exe"
  CreateShortCut "$DESKTOP\BSM.lnk" "$INSTDIR\BSM.exe"
  
  ; Write registry keys
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\BSM.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\BSM.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  
  ; Get install size
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "EstimatedSize" "$0"
SectionEnd

Section "Start Menu Shortcuts" SEC02
  CreateShortCut "$SMPROGRAMS\BSM\Uninstall.lnk" "$INSTDIR\uninst.exe"
  CreateShortCut "$SMPROGRAMS\BSM\README.lnk" "$INSTDIR\README.md"
SectionEnd

Section "Auto-start with Windows" SEC03
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "BSM" "$INSTDIR\BSM.exe --minimized"
SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\BSM\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "Core BSM application files (required)"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "Add shortcuts to Start Menu"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "Start BSM automatically when Windows starts"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Uninstaller
Section Uninstall
  ; Remove auto-start
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "BSM"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\BSM\Uninstall.lnk"
  Delete "$SMPROGRAMS\BSM\Website.lnk"
  Delete "$DESKTOP\BSM.lnk"
  Delete "$SMPROGRAMS\BSM\BSM.lnk"
  Delete "$SMPROGRAMS\BSM\README.lnk"
  
  ; Remove directories
  RMDir "$SMPROGRAMS\BSM"
  RMDir /r "$INSTDIR"
  
  ; Remove registry keys
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  
  SetAutoClose true
SectionEnd
