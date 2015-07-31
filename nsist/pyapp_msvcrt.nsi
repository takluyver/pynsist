[% extends "pyapp.nsi" %]

[% block sections %]
!addplugindir [[ pynsist_pkg_dir ]]
!include windowsversion.nsh
!include x64.nsh

Section "-msvcrt"
  ${GetWindowsVersion} $R0

  StrCpy $0 "--"

  ${If} ${RunningX64}
    ${If} $R0 == "8.1"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x64/Windows8.1-KB2999226-x64.msu"
    ${ElseIf} $R0 == "8"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x64/Windows8-RT-KB2999226-x64.msu"
    ${ElseIf} $R0 == "7"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x64/Windows6.1-KB2999226-x64.msu"
    ${ElseIf} $R0 == "Vista"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x64/Windows6-KB2999226-x64.msu"
    ${EndIf}
  ${Else}
    ${If} $R0 == "8.1"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x86/Windows8.1-KB2999226-x86.msu"
    ${ElseIf} $R0 == "8"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x86/Windows8-RT-KB2999226-x86.msu"
    ${ElseIf} $R0 == "7"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x86/Windows6.1-KB2999226-x86.msu"
    ${ElseIf} $R0 == "Vista"
      StrCpy $0 "https://github.com/takluyver/pynsist/raw/msvcrt-2015-msus/x86/Windows6-KB2999226-x86.msu"
    ${EndIf}
  ${EndIf}

  IfFileExists "$SYSDIR\ucrtbase.dll" skip_msvcrt
  StrCmp $0 "--" skip_msvcrt

  DetailPrint "Need to install MSVCRT 2015. This may take a few minutes."
  DetailPrint "Downloading $0"
  inetc::get /RESUME "" "$0" "$INSTDIR\msvcrt.msu"
  Pop $2
  DetailPrint "Download finished ($2)"
  ${If} $2 == "OK"
    DetailPrint "Running wusa to install update package"
    ExecWait 'wusa "$INSTDIR\msvcrt.msu" /quiet /norestart' $1
    Delete "$INSTDIR\msvcrt.msu"
  ${Else}
    MessageBox MB_OK "Failed to download important update! \
            ${PRODUCT_NAME} will not run until you install the Visual C++ \
            redistributable for Visual Studio 2015.\
            $\n$\nhttp://www.microsoft.com/en-us/download/details.aspx?id=48145"
  ${EndIf}

  # This WUSA exit code means a reboot is needed.
  ${If} $1 = 0x00240005
    SetRebootFlag true
  ${EndIf}

  skip_msvcrt:
SectionEnd

[[ super() ]]
[% endblock sections %]
