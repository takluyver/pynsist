[% extends "pyapp.nsi" %]
[# For Python 2, add the py/pyw Windows launcher. Python 3 includes it already. #]

[% block sections %]
[[ super() ]]

Section "PyLauncher" sec_pylauncher
    File "launchwin${ARCH_TAG}.msi"
    ExecWait 'msiexec /i "$INSTDIR\launchwin${ARCH_TAG}.msi" /qb ALLUSERS=1'
    Delete "$INSTDIR\launchwin${ARCH_TAG}.msi"
SectionEnd
[% endblock %]

[% block mouseover_messages %]
[[ super() ]]

StrCmp $0 ${sec_app} "" +2
  SendMessage $R0 ${WM_SETTEXT} 0 "STR:The Python launcher. \
      This is required for ${PRODUCT_NAME} to run."
[% endblock %]
