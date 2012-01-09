!macro CustomCodePreInstall
	${If} ${FileExists} $InstDir\Data\.scribus
		Rename $InstDir\Data\.scribus\scribus13.rc $InstDir\Data\.scribus\scribus140.rc
		Rename $InstDir\Data\.scribus\prefs13.xml $InstDir\Data\.scribus\prefs140.xml
		Rename $InstDir\Data\.scribus $InstDir\Data\Scribus
	${EndIf}
!macroend