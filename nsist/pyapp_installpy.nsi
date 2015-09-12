[% extends "pyapp.nsi" %]

[% block ui_pages %]
[# We only need to add COMPONENTS, but they have to be in order #]
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
[% endblock ui_pages %]

[% block sections %]
Section "Python ${PY_VERSION}" sec_py

  DetailPrint "Installing Python ${PY_MAJOR_VERSION}, ${BITNESS} bit"
  [% if ib.py_version_tuple >= (3, 5) %]
    [% set filename = 'python-' ~ ib.py_version ~ ('-amd64' if ib.py_bitness==64 else '') ~ '.exe' %]
    File "[[filename]]"
    ExecWait '"$INSTDIR\[[filename]]" /passive Include_test=0 InstallAllUsers=1'
  [% else %]
    [% set filename = 'python-' ~ ib.py_version ~ ('.amd64' if ib.py_bitness==64 else '') ~ '.msi' %]
    File "[[filename]]"
    ExecWait 'msiexec /i "$INSTDIR\[[filename]]" \
            /qb ALLUSERS=1 TARGETDIR="$COMMONFILES${BITNESS}\Python\${PY_MAJOR_VERSION}"'
  [% endif %]
  Delete "$INSTDIR\[[filename]]"
SectionEnd

[[ super() ]]
[% endblock sections %]

[% block mouseover_messages %]
    StrCmp $0 ${sec_py} 0 +2
      SendMessage $R0 ${WM_SETTEXT} 0 "STR:The Python interpreter. \
            This is required for ${PRODUCT_NAME} to run."

[[ super() ]]
[% endblock mouseover_messages %]
