[% extends "pyapp.nsi" %]

[% block sections %]
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

  DetailPrint "Downloading and installing MSVCRT from $0"
  NSISdl::download $0 msvcrt.msu
  ExecWait 'wusa /quiet /norestart "$INSTDIR\msvcrt.msu"' $1
  Delete "$INSTDIR\msvcrt.msu"

  # This WUSA exit code means a reboot is needed.
  ${If} $1 = 0x00240005
    SetRebootFlag true
  ${EndIf}

  skip_msvcrt:
SectionEnd
[% endblock sections %]
