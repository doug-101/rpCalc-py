; rpcalc.nsi

; Created       : 2004-3-11
; By            : Doug Bell
; License       : Free to use, modify and distribute, but with no warranty.
; Last modified : 2006-10-02

; rpCalc is an RPN calculator
; Please check the website for details and updates <http://www.bellz.org/>.

;--------------------------------

!include "MUI.nsh"


; The name of the installer

!define NAME "rpCalc"
!define VERSION "0.5.0"

; Uncomment next line to include pyQt libraries in the installer
!define PYQT

!ifdef PYQT
	!define SUFFIX "-install"
!else
	!define SUFFIX "-upgrade"
!endif

Name "${NAME} ${VERSION} by Doug Bell"


; The file to write
OutFile "rpcalc-${VERSION}${SUFFIX}.exe"
SetCompressor lzma

!define MUI_ICON "install.ico"
!define MUI_UNICON "uninstall.ico"

XPStyle on

; The default installation directory
InstallDir "$PROGRAMFILES\${NAME}"

; Registry key to check for directory (so if you install again, it will
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\${NAME}" "Install_Dir"

;--------------------------------

!define MUI_COMPONENTSPAGE
!define MUI_COMPONENTSPAGE_SMALLDESC
!define MUI_LICENSEPAGE_TEXT_BOTTOM "Press Continue to install."
!define MUI_LICENSEPAGE_BUTTON "Continue"

!insertmacro MUI_PAGE_LICENSE ".\doc\LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

!insertmacro MUI_LANGUAGE "English"


;--------------------------------

AutoCloseWindow false
ShowInstDetails show

InstType Typical
SetOverwrite ifnewer


; The stuff to install
Section "${NAME} (required)" rpcalc

	SectionIn 1 RO

	; Set output path to the installation directory.
	SetOutPath "$INSTDIR\lib"

	; Put files there
	File ".\lib\rpcalc.exe"
        File ".\lib\library.zip"
	File ".\rpcalc.ico"

        ; Set output path to the doc install directory.
        SetOutPath "$INSTDIR\doc"

        ; Put files there
        File ".\doc\LICENSE"
        File ".\doc\README.html"

SectionEnd

!ifdef PYQT

	Section "PyQt libraries (required)" py_qt

		SectionIn 1 RO

                SetOutPath "$INSTDIR\lib"

		File ".\lib\_socket.pyd"
		File ".\lib\_ssl.pyd"
                File ".\lib\bz2.pyd"
                File ".\lib\mingwm10.dll"
                File ".\lib\MSVCR71.dll"
		File ".\lib\python24.dll"
                File ".\lib\QtCore4.dll"
                File ".\lib\QtCore.pyd"
                File ".\lib\QtGui4.dll"
                File ".\lib\QtGui.pyd"
                File ".\lib\sip.pyd"
                File ".\lib\unicodedata.pyd"
                File ".\lib\w9xpopen.exe"
                File ".\lib\zlib.pyd"

	SectionEnd
!endif

Section "Start menu shortcuts" startmenu
	; Optional section (can be disabled by the user)
  SectionIn 1
  CreateDirectory "$SMPROGRAMS\${NAME}"
  CreateShortCut "$SMPROGRAMS\${NAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortCut "$SMPROGRAMS\${NAME}\Readme.lnk" "$INSTDIR\doc\Readme.html"
  CreateShortCut "$SMPROGRAMS\${NAME}\${NAME}.lnk" "$INSTDIR\lib\rpcalc.exe" "" "$INSTDIR\lib\rpcalc.exe" 0

SectionEnd

Section "Desktop shortcut" deskicon
	; Optional section (can be disabled by the user)
  SectionIn 1
  CreateShortCut "$DESKTOP\${NAME}.lnk" "$INSTDIR\lib\rpcalc.exe" "" "$INSTDIR\lib\rpcalc.exe" 0

SectionEnd

Section "Install and uninstall registry keys" reg_keys
        ; Optional section (can be disabled by the user)
        SectionIn 1

	; Write the installation path into the registry
	WriteRegStr HKLM "SOFTWARE\${NAME}" "Install_Dir" "$INSTDIR"

	; Write the uninstall keys for Windows
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}" "DisplayName" "${NAME}"
	WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
	WriteUninstaller "uninstall.exe"

SectionEnd

Section /o "${NAME} source code" source
	; Optional section (can be disabled by the user)
        SectionIn 1

        SetOutPath "$INSTDIR\source"

	File ".\rpcalc.nsi"
	File ".\install.ico"
	File ".\uninstall.ico"

        File ".\source\calcbutton.py"
        File ".\source\calccore.py"
        File ".\source\calcdlg.py"
        File ".\source\calclcd.py"
        File ".\source\calcstack.py"
        File ".\source\extradisplay.py"
        File ".\source\helpview.py"
        File ".\source\icons.py"
        File ".\source\option.py"
        File ".\source\optiondefaults.py"
        File ".\source\optiondlg.py"
        File ".\source\rpcalc.py"
        File ".\source\setup.py"

SectionEnd

;--------------------------------
;Descriptions

LangString DESC_rpcalc ${LANG_ENGLISH} "rpCalc program and help files."
LangString DESC_pyqt ${LANG_ENGLISH} "Required PyQt library files."
LangString DESC_startmenu ${LANG_ENGLISH} "Add rpCalc to the Start menu."
LangString DESC_deskicon ${LANG_ENGLISH} "Add a rpCalc shortcut to the desktop."
LangString DESC_reg_keys ${LANG_ENGLISH} "Write install and uninstall information."
LangString DESC_source ${LANG_ENGLISH} "rpCalc source code (for developers)."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
	!insertmacro MUI_DESCRIPTION_TEXT ${rpcalc} $(DESC_rpcalc)

	!ifdef PYQT
		!insertmacro MUI_DESCRIPTION_TEXT ${py_qt} $(DESC_pyqt)
	!endif

	!insertmacro MUI_DESCRIPTION_TEXT ${startmenu} $(DESC_startmenu)
	!insertmacro MUI_DESCRIPTION_TEXT ${deskicon} $(DESC_deskicon)
        !insertmacro MUI_DESCRIPTION_TEXT ${reg_keys} $(DESC_reg_keys)
	!insertmacro MUI_DESCRIPTION_TEXT ${source} $(DESC_source)
!insertmacro MUI_FUNCTION_DESCRIPTION_END


;--------------------------------

; Uninstaller

Section "Uninstall"

	; Remove registry keys
	DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${NAME}"
	DeleteRegKey HKLM "SOFTWARE\${NAME}"

	; Remove files and uninstaller

	Delete "$INSTDIR\lib\rpcalc.exe"
        Delete "$INSTDIR\lib\library.zip"
	Delete "$INSTDIR\lib\rpcalc.ico"

        Delete "$INSTDIR\doc\LICENSE"
        Delete "$INSTDIR\doc\README.html"

	Delete "$INSTDIR\lib\_socket.pyd"
	Delete "$INSTDIR\lib\_ssl.pyd"
        Delete "$INSTDIR\lib\bz2.pyd"
        Delete "$INSTDIR\lib\mingwm10.dll"
        Delete "$INSTDIR\lib\MSVCR71.dll"
	Delete "$INSTDIR\lib\python24.dll"
        Delete "$INSTDIR\lib\QtCore4.dll"
        Delete "$INSTDIR\lib\QtCore.pyd"
        Delete "$INSTDIR\lib\QtGui4.dll"
        Delete "$INSTDIR\lib\QtGui.pyd"
        Delete "$INSTDIR\lib\sip.pyd"
        Delete "$INSTDIR\lib\unicodedata.pyd"
        Delete "$INSTDIR\lib\w9xpopen.exe"
        Delete "$INSTDIR\lib\zlib.pyd"

        Delete "$INSTDIR\lib\_sre.pyd"
        Delete "$INSTDIR\lib\libqtc.pyd"
        Delete "$INSTDIR\lib\libsip.dll"
        Delete "$INSTDIR\lib\python23.dll"
        Delete "$INSTDIR\lib\qt-mt230nc.dll"

	Delete "$INSTDIR\source\rpcalc.nsi"
	Delete "$INSTDIR\source\install.ico"
	Delete "$INSTDIR\source\uninstall.ico"

        Delete "$INSTDIR\source\calcbutton.py"
        Delete "$INSTDIR\source\calccore.py"
        Delete "$INSTDIR\source\calcdlg.py"
        Delete "$INSTDIR\source\calclcd.py"
        Delete "$INSTDIR\source\calcstack.py"
        Delete "$INSTDIR\source\extradisplay.py"
        Delete "$INSTDIR\source\helpview.py"
        Delete "$INSTDIR\source\icons.py"
        Delete "$INSTDIR\source\option.py"
        Delete "$INSTDIR\source\optiondefaults.py"
        Delete "$INSTDIR\source\optiondlg.py"
        Delete "$INSTDIR\source\rpcalc.py"
        Delete "$INSTDIR\source\setup.py"
        Delete "$INSTDIR\source\tmpcontrol.py"

	Delete "$INSTDIR\lib\rpcalc.ini"

	Delete "$INSTDIR\uninstall.exe"

	; Remove shortcuts, if any
	RMDir /r "$SMPROGRAMS\${NAME}"

	; Remove directories used
        RMDir "$INSTDIR\lib"
        RMDir "$INSTDIR\doc"
        RMDir "$INSTDIR\source"
	RMDir "$INSTDIR" ;remove if empty
	; RMDir /r "$INSTDIR" ;remove even if not empty

SectionEnd
