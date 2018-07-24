!define PRODUCT_NAME "[[ib.appname]]"
!define PRODUCT_VERSION "[[ib.version]]"
!define PY_VERSION "[[ib.py_version]]"
!define PY_MAJOR_VERSION "[[ib.py_major_version]]"
!define BITNESS "[[ib.py_bitness]]"
!define ARCH_TAG "[[arch_tag]]"
!define INSTALLER_NAME "[[ib.installer_name]]"
!define PRODUCT_ICON "[[icon]]"

[% if has_checkDirContains or has_checkDirStartsWith or has_checkDirEndsWith or has_checkDirLike or has_checkRegistry %]
var str_filePath
var str_dirPath
var str_returnVar
[% endif %]

[% if has_checkRegistry %]
var root_key
var checkBitness
!macro _checkRegistryConstructor rootKey subKey name bitness
  ; Example Input: ${checkRegistry} "HKLM" "Software\NSIS" "";$str_returnVar = "true"
  StrCpy $root_key "${rootKey}"
  StrCpy $str_dirPath "${subKey}"
  StrCpy $str_filePath "${name}"
  StrCpy $checkBitness "${bitness}"
  Call checkRegistry
!macroend
!define checkRegistry '!insertmacro "_checkRegistryConstructor"'
[% endif %]

[% if has_checkDirContains %]
!macro _checkDirContainsConstructor dirPath filePath 
  ; Example Input: ${checkDirContains} "$INSTDIR";$str_returnVar = "true"
  StrCpy $str_dirPath "${dirPath}"
  StrCpy $str_filePath "${filePath}"
  Call checkDirContains
!macroend
!define checkDirContains '!insertmacro "_checkDirContainsConstructor"'
[% endif %]

[% if has_checkDirStartsWith %]
!macro _checkDirStartsWithConstructor dirPath filePath 
  ; Example Input: ${StrEndsWith} "This" "This is just an example" ;$str_returnVar = "true"
  ; Example Input: ${StrEndsWith} "missing" "This is another example" ;$str_returnVar = "false"
  StrCpy $str_dirPath "${dirPath}"
  StrCpy $str_filePath "${filePath}"
  Call checkDirStartsWith
!macroend
!define checkDirStartsWith '!insertmacro "_checkDirStartsWithConstructor"'
[% endif %]

[% if has_checkDirEndsWith %]
!macro _checkDirEndsWithConstructor dirPath filePath 
  ; Example Input: ${StrEndsWith} "example" "This is just an example" ;$str_returnVar = "true"
  ; Example Input: ${StrEndsWith} "missing" "This is another example" ;$str_returnVar = "false"
  StrCpy $str_dirPath "${dirPath}"
  StrCpy $str_filePath "${filePath}"
  Call checkDirEndsWith
!macroend
!define checkDirEndsWith '!insertmacro "_checkDirEndsWithConstructor"'
[% endif %]

[% if has_checkDirLike %]
var str_strContains_var1
var str_strContains_var2
var str_strContains_var3
var str_strContains_var4
!macro _checkDirLikeConstructor dirPath filePath
  ; Example Input: ${checkDirLike} "just" "This is just an example" ;$str_returnVar = "true"
  ; Example Input: ${checkDirLike} "missing" "This is another example" ;$str_returnVar = "false"
  StrCpy $str_dirPath "${dirPath}"
  StrCpy $str_filePath "${filePath}"
  Call checkDirLike
!macroend
!define checkDirLike '!insertmacro "_checkDirLikeConstructor"'
[% endif %]

; Marker file to tell the uninstaller that it's a user installation
!define USER_INSTALL_MARKER _user_install_marker
 
SetCompressor lzma

!define MULTIUSER_EXECUTIONLEVEL Highest
!define MULTIUSER_INSTALLMODE_DEFAULT_CURRENTUSER
!define MULTIUSER_MUI
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!define MULTIUSER_INSTALLMODE_INSTDIR "[[ib.appname]]"
[% if ib.py_bitness == 64 %]
!define MULTIUSER_INSTALLMODE_FUNCTION correct_prog_files
[% endif %]
!include MultiUser.nsh

[% block modernui %]
; Modern UI installer stuff 
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "[[icon]]"
!define MUI_UNICON "[[icon]]"

; UI pages
[% block ui_pages %]
!insertmacro MUI_PAGE_WELCOME
[% if license_file %]
!insertmacro MUI_PAGE_LICENSE [[license_file]]
[% endif %]
!insertmacro MULTIUSER_PAGE_INSTALLMODE
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
[% endblock ui_pages %]
!insertmacro MUI_LANGUAGE "English"
[% endblock modernui %]

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${INSTALLER_NAME}"
ShowInstDetails show

Section -SETTINGS
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
SectionEnd

[% block sections %]
[% if has_prereq %]
Section -Prerequisites
  [[gen_prereq()]]
SectionEnd
[% endif %]

Section "!${PRODUCT_NAME}" sec_app
  SetRegView [[ib.py_bitness]]
  SectionIn RO
  File ${PRODUCT_ICON}
  SetOutPath "$INSTDIR\pkgs"
  File /r "pkgs\*.*"
  SetOutPath "$INSTDIR"

  ; Marker file for per-user install
  StrCmp $MultiUser.InstallMode CurrentUser 0 +3
    FileOpen $0 "$INSTDIR\${USER_INSTALL_MARKER}" w
    FileClose $0
    SetFileAttributes "$INSTDIR\${USER_INSTALL_MARKER}" HIDDEN

  [% block install_files %]
  ; Install files
  [% for destination, group in grouped_files %]
    SetOutPath "[[ensurePathFormat(destination)]]"
    [% for target, file in group %]
      File /oname=[[ ensurePathFormat(target) ]] "[[ ensurePathFormat(file) ]]" 
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
  [% if single_shortcut %]
    [% for scname, sc in ib.shortcuts.items() %]
    CreateShortCut "$SMPROGRAMS\[[scname]].lnk" "[[sc['target'] ]]" \
      '[[ sc['parameters'] ]]' "$INSTDIR\[[ sc['icon'] ]]"
    [% endfor %]
  [% else %]
    [# Multiple shortcuts: create a directory for them #]
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    [% for scname, sc in ib.shortcuts.items() %]
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\[[scname]].lnk" "[[sc['target'] ]]" \
      '[[ sc['parameters'] ]]' "$INSTDIR\[[ sc['icon'] ]]"
    [% endfor %]
  [% endif %]
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
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "InstallLocation" "$INSTDIR"
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayIcon" "$INSTDIR\${PRODUCT_ICON}"
  [% if ib.publisher is not none %]
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                     "Publisher" "[[ib.publisher]]"
  [% endif %]
  WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegDWORD SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "NoModify" 1
  WriteRegDWORD SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" \
                   "NoRepair" 1

  ; Check if we need to reboot
  IfRebootFlag 0 noreboot
    MessageBox MB_YESNO "A reboot is required to finish the installation. Do you wish to reboot now?" \
                /SD IDNO IDNO noreboot
      Reboot
  noreboot:
SectionEnd

Section "Uninstall"
  SetRegView [[ib.py_bitness]]
  SetShellVarContext all
  IfFileExists "$INSTDIR\${USER_INSTALL_MARKER}" 0 +3
    SetShellVarContext current
    Delete "$INSTDIR\${USER_INSTALL_MARKER}"

  Delete $INSTDIR\uninstall.exe
  Delete "$INSTDIR\${PRODUCT_ICON}"
  RMDir /r "$INSTDIR\pkgs"

  ; Remove ourselves from %PATH%
  [% block uninstall_commands %]
  [% if has_commands %]
    nsExec::ExecToLog '[[ python ]] -Es "$INSTDIR\_system_path.py" remove "$INSTDIR\bin"'
  [% endif %]
  [% endblock uninstall_commands %]

  ; Remove prerequisites
  [% if has_prereq %]
    RMDir /r "$INSTDIR\\Prerequisites"
  [% endif %]

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
  [% if single_shortcut %]
    [% for scname in ib.shortcuts %]
      Delete "$SMPROGRAMS\[[scname]].lnk"
    [% endfor %]
  [% else %]
    RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
  [% endif %]
  [% endblock uninstall_shortcuts %]
  RMDir $INSTDIR
  DeleteRegKey SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
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

Function .onInit
  !insertmacro MULTIUSER_INIT
FunctionEnd

Function un.onInit
  !insertmacro MULTIUSER_UNINIT
FunctionEnd

[% if ib.py_bitness == 64 %]
Function correct_prog_files
  ; The multiuser machinery doesn't know about the different Program files
  ; folder for 64-bit applications. Override the install dir it set.
  StrCmp $MultiUser.InstallMode AllUsers 0 +2
    StrCpy $INSTDIR "$PROGRAMFILES64\${MULTIUSER_INSTALLMODE_INSTDIR}"
FunctionEnd
[% endif %]

[% if has_checkRegistry %]
Function checkRegistry
  ${Select} $checkBitness
    ${Case} "64"
      Setregview 64
    ${Case} "32"
      Setregview 32
    ${CaseElse}
      SetRegView [[ib.py_bitness]]
  ${EndSelect}
  
  Push $R0
  ${Select} $root_key
    ${Case} "HKLM"
      ReadRegStr $R0 HKLM $str_dirPath $str_filePath
    ${Case} "HKCR"
      ReadRegStr $R0 HKCR $str_dirPath $str_filePath
    ${Case} "HKCU"
      ReadRegStr $R0 HKCU $str_dirPath $str_filePath
    ${Case} "HKU"
      ReadRegStr $R0 HKU $str_dirPath $str_filePath
    ${Case} "HKCC"
      ReadRegStr $R0 HKCC $str_dirPath $str_filePath
    ${Case} "HKDD"
      ReadRegStr $R0 HKDD $str_dirPath $str_filePath
    ${Case} "HKPD"
      ReadRegStr $R0 HKPD $str_dirPath $str_filePath
    ${Case} "SHCTX"
      ReadRegStr $R0 SHCTX $str_dirPath $str_filePath
    ${CaseElse}
      StrCpy $R0 ""
  ${EndSelect}

  ${If} $R0 == ""
    StrCpy $str_returnVar "false"
  ${ELSE}
    StrCpy $str_returnVar "true"
  ${EndIf}
  ; MessageBox MB_OK $str_returnVar, $R0"
  Pop $R0
  SetRegView [[ib.py_bitness]]
FunctionEnd
[% endif %]

[% if has_checkDirContains %]
Function checkDirContains
  ${If} ${FileExists} "$str_dirPath\\\\$str_filePath"
    StrCpy $str_returnVar "true"
  ${ELSE}
    StrCpy $str_returnVar "false"
  ${EndIf}
FunctionEnd
[% endif %]

[% if has_checkDirStartsWith %]
Function checkDirStartsWith
  ; Modified Code from http://nsis.sourceforge.net/EnsureEndsWith

  ; TO DO: Make this loop through the given directory
  ; $str_value will be the current file that it is looking at
  ; Keep looping until a match is found or all files have been examined

  Push $R0
  Push $R1
  Push $R2

  StrLen $R0 $str_filePath ; how long is the ending string
  IntOp $R1 0 - $R0 ; how far to offset back from the end of the string
  StrCpy $R2 $str_value $R0 $R1 ;take N chars starting N from the end of str_value put in R2
  StrCmp $R2 $str_filePath found ;if the last N chars = str_filePath, good.
  Goto notFound ; This will go to nextFile instead
  found:
    StrCpy $str_returnVar "true"
    Goto done
  notFound:
    StrCpy $str_returnVar "false"
    Goto done
  done:
 
  Pop $R2
  Pop $R1
  Pop $R0
FunctionEnd
[% endif %]

[% if has_checkDirEndsWith %]
Function checkDirEndsWith
  ; TO DO: Modify checkDirStartsWith

  StrCpy $str_returnVar "true"
FunctionEnd
[% endif %]

[% if has_checkDirLike %]
Function checkDirLike
  ; Modified Code From kenglish_hi on http://nsis.sourceforge.net/StrContains

  ; TO DO: Make this loop through the given directory
  ; $str_haystack will be the current file that it is looking at
  ; Keep looping until a match is found or all files have been examined

  StrCpy $str_returnVar ""
  StrCpy $str_strContains_var1 -1
  StrLen $str_strContains_var2 $str_filePath
  StrLen $str_strContains_var4 $str_haystack
  loop:
    IntOp $str_strContains_var1 $str_strContains_var1 + 1
    StrCpy $str_strContains_var3 $str_haystack $str_strContains_var2 $str_strContains_var1
    StrCmp $str_strContains_var3 $str_filePath found
    StrCmp $str_strContains_var1 $str_strContains_var4 notFound ; This will go to nextFile instead
    Goto loop
  found:
    StrCpy $str_returnVar "true"
    Goto done
  notFound:
    StrCpy $str_returnVar "false"
    Goto done
  done:
FunctionEnd
[% endif %]