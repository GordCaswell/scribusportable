!macro CustomCodePreInstall
	${If} ${FileExists} $InstDir\Data\.scribus
		Rename $InstDir\Data\.scribus $InstDir\Data\Scribus
	${EndIf}
!macroend