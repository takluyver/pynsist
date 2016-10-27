[% extends "pyapp.nsi" %]

[% block install_files %]
    [[ super() ]]

    ; Install MSVCRT if it's not already on the system
    IfFileExists "$SYSDIR\ucrtbase.dll" skip_msvcrt
    SetOutPath $INSTDIR\Python
    [% for file in ib.msvcrt_files %]
    File msvcrt\[[file]]
    [% endfor %]
    skip_msvcrt:

[% endblock %]
