!define PRODUCT_NAME "[[ib.appname]]"
!define PRODUCT_VERSION "[[ib.version]]"
!define PY_VERSION "[[ib.py_version]]"
!define PY_MAJOR_VERSION "[[ib.py_major_version]]"
!define BITNESS "[[ib.py_bitness]]"
!define ARCH_TAG "[[arch_tag]]"
!define INSTALLER_NAME "[[ib.installer_name]]"
!define PRODUCT_ICON "[[icon]]"
 
SetCompressor lzma

RequestExecutionLevel admin

[% block modernui %]
; Modern UI installer stuff 
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"

; UI pages
[% block ui_pages %]
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
[% endblock ui_pages %]
!insertmacro MUI_LANGUAGE "English"
[% endblock modernui %]

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${INSTALLER_NAME}"
InstallDir "$PROGRAMFILES${BITNESS}\${PRODUCT_NAME}"
ShowInstDetails show

Section -SETTINGS
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
SectionEnd

[% block sections %]

Section "!${PRODUCT_NAME}" sec_app
  SectionIn RO
  SetShellVarContext all
  File ${PRODUCT_ICON}
  SetOutPath "$INSTDIR\pkgs"
  File /r "pkgs\*.*"
  SetOutPath "$INSTDIR"

  [% block install_files %]
  ; Install files
  [% for destination, group in grouped_files %]
    SetOutPath "[[destination]]"
    [% for file in group %]
      File "[[ file ]]"
    [% endfor %]
  [% endfor %]
  
  ; Install directories
  [% for dir, destination in ib.install_dirs %]
    SetOutPath "[[ pjoin(destination, dir) ]]"
    File /r "[[dir]]\*.*"
  [% endfor %]
  [% endblock install_files %]
  
  [% block install_shortcuts %]
  ; Install shortcuts
  ; The output path becomes the working directory for shortcuts
  SetOutPath "%HOMEDRIVE%\%HOMEPATH%"
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  [% for scname, sc in ib.shortcuts.items() %]
  SearchPath $0 "[[sc['target'] ]].exe"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\[[scname]].lnk" $0 \
    '[[ sc['parameters'] ]]' "$INSTDIR\[[ sc['icon'] ]]"
  [% endfor %]
  ; Create shortcut to uninstaller
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall ${PRODUCT_NAME}.lnk" \
    "$INSTDIR\uninstall.exe"
  SetOutPath "$INSTDIR"
  [% endblock install_shortcuts %]

  [% block install_commands %]
  [% if has_commands %]
    nsExec::ExecToLog '[[ python ]] -Es "$INSTDIR\_rewrite_shebangs.py" "$INSTDIR\bin"'
    nsExec::ExecToLog '[[ python ]] -Es "$INSTDIR\_system_path.py" add "$INSTDIR\bin"'
  [% endif %]
  [% endblock install_commands %]
  
  ; Byte-compile Python files.
  DetailPrint "Byte-compiling Python modules..."
  nsExec::ExecToLog '[[ python ]] -m compileall -q "$INSTDIR\pkgs"'
  WriteUninstaller $INSTDIR\uninstall.exe
  ; Add ourselves to Add/remove programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayIcon" "$INSTDIR\${PRODUCT_ICON}"
  [% if ib.publisher is not none %]
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "Publisher" "[[ib.publisher]]"
  [% endif %]
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "NoRepair" 1

  ; Check if we need to reboot
  IfRebootFlag 0 noreboot
    MessageBox MB_YESNO "A reboot is required to finish the installation. Do you wish to reboot now?" \
                /SD IDNO IDNO noreboot
      Reboot
  noreboot:
SectionEnd

Section "Uninstall"
  # Ask the user whether they really wish to uninstall - last chance to back out
  MessageBox MB_OKCANCEL "Uninstall ${PRODUCT_NAME}.  Are you sure?" IDOK Ok
    Abort
  Ok:
  SetShellVarContext all
  Delete "$INSTDIR\${PRODUCT_ICON}"
  RMDir /r "$INSTDIR\pkgs"

  ; Remove ourselves from %PATH%
  [% block uninstall_commands %]
  [% if has_commands %]
    nsExec::ExecToLog '[[ python ]] -Es "$INSTDIR\_system_path.py" remove "$INSTDIR\bin"'
  [% endif %]
  [% endblock uninstall_commands %]

  [% block uninstall_files %]
  ; Uninstall files
  [% for file, destination in ib.install_files %]
    Delete "[[pjoin(destination, file)]]"
  [% endfor %]
  ; Uninstall directories
  [% for dir, destination in ib.install_dirs %]
    RMDir /r "[[pjoin(destination, dir)]]"
  [% endfor %]
  [% endblock uninstall_files %]

  [% block uninstall_shortcuts %]
  ; Uninstall shortcuts
  RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
  ; Uninstall the uninstaller
  [% endblock uninstall_shortcuts %]
  Delete $INSTDIR\uninstall.exe
  RMDir $INSTDIR
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
SectionEnd

[% endblock sections %]

; Functions

Function .onMouseOverSection
    ; Find which section the mouse is over, and set the corresponding description.
    FindWindow $R0 "#32770" "" $HWNDPARENT
    GetDlgItem $R0 $R0 1043 ; description item (must be added to the UI)

    [% block mouseover_messages %]
    StrCmp $0 ${sec_app} "" +2
      SendMessage $R0 ${WM_SETTEXT} 0 "STR:${PRODUCT_NAME}"
    
    [% endblock mouseover_messages %]
FunctionEnd
