#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Diese Skript exportiert ein Dokument mit Beschnittrand samt Marken als PDF.
Hierzu ist wie folgt vorzugehen:

0) Ihr Dokument muß eine minimale Ablagefläche oberhalb, links und rechts von 20 pt und
   einen minimalen vertikalen Abstand zwischen den Seiten von 40 pt aufweisen
   (siehe Datei->Dokument einrichten->Anzeige). Das Script ist nur für Dokumente getestet,
   bei denen alle Seiten gleich groß sind!

1) Speichern Sie Ihr Dokument.

2) Starten Sie dieses Skript.

3) Zuerst werden Sie nach Einheit und Größe des Beschnittrandes
   sowie die Farbnamen gefragt. Die Größe des Beschnittrandes wird automatisch verkleinert, wenn dieser
   größer als der halbe vertikale Abstand zwischen den Seiten ist.

4) Dann werden Sie nach dem Namen eines Verzeichnisses gefragt, in dem je ein Scribus-Dokument
   für linke und rechte Seiten abgelegt und die gedruckten Seiten abgelegt werden.

5) Wählen Sie die Optioen für die Beschnittmarken und die Beschriftung aus.


Sie erhalten nun für jede Seite eine PDF-Datei mit Beschnittrand und, falls gewählt, Schnittmarken, Passermarken und Hilfstext sowie einen Dateinamen aufgedruckt. Außerdem werden drei Scribus-Dateien angelegt.

Autor: Konrad Stania mit Ergänzungen durch Gregory Pittman und Petr Vanek

##########################################

This script exports a document with 20 pt bleed and crop-marks as PDF.

USAGE:


0) Make a document with min. 20 pt scratch space above and on the right of the page and 40 pt vertical distance
   between the pages. The script is tested only for documents in which every page the same size.

1) Save your document

2) Start the script.

3) Enter the unit and size of the bleed, the color names for the marks and text.
  The bleed will be automatically reduced if it's larger then the half vertical distance between the pages.

4) Choose a directory where the tempory files and the output is stored.

5) Choose whether you like to have marks and/or text.

Execution of the script will result in one pdf for each page and three Scribus-files

Author: Konrad Stania, with additions by Gregory Pittman and Petr Vanek

#############################################

LICENSE:

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

# Craig Bradney, Scribus Team
# 10/3/08: Added to Scribus 1.3.3.12svn distribution "as was" from Scribus wiki for bug #6826 and improved later on by Gregory Pittman and Petr Vanek.
# script is GPLd

import sys
from xml.dom import minidom
from datetime import date
import random
import os

try:
    from scribus import *
except ImportError:
    print "This script only runs from within Scribus."
    sys.exit(1)

def main():
    #setRedraw(False)

    #the xml-interpretation with expat does not like some chars. We will have to substitute them and
    #change this back before going to interpret the new files with scribus
    #Append this list, if you encounter an expat-error concerning xml with wrong chars
    #We have to decide if you are using it on Win or Linux

    charsToChangeWin1333 = ["&#x1a;","&#x1b;","&#x1c;","&#x1d;","&#x1e;","&#x18;","&#x4;", "&#x5;"]

    charsToChange = charsToChangeWin1333
    fgcolmesg = "Foreground Color for Marks\n (The script will create the color if it doesn't exist):"
    if (lang == "DE"):
        fgcolmesg = "Vordergrundfarbe für Marken\n (Das Skript erstellt die Farbe, wenn sie nicht vorhanden ist):"
    fgcol = valueDialog("Bleed and Marks", fgcolmesg ,"regcol")
    if fgcol == '':
        return
    try:
        colval = getColor(fgcol)
    except NotFoundError:
        defineColor(fgcol, 0, 0, 0, 255)
        colval = getColor(fgcol)

    defineColor("bleed_export_white_323567654", 0, 0, 0, 0)
    bgcol = "bleed_export_white_323567654"
    #bgcol = valueDialog("Bleed and Marks", "Background color for marks (script stops if color doesn't exist)\nHintergrundfarbe für Marken (Skript bricht ab, wenn Farbe nicht vorhanden):" ,"White")
    #olval = getColor(bgcol)

    userUnit = getUnit()
    setUnit(0)

    #deselectAll()
    baseDirmesg = "Output Directory"
    if (lang == "DE"):
        baseDirmesg = "Ausgabeverzeichnis"
    baseDirName = fileDialog("Bleed and Marks - " + baseDirmesg, "*","./" ,False, False, True)

    baseName = valueDialog("Bleed and Marks", "File names will begin with (prefix):", "scribus_print")
    baseFileName = baseDirName + baseName
    exportType = "pdf"
    UnitFakt = 1
    bleedVal = 20
    UnitType = "pt"

    UnitTypemesg = "Unit for Bleed: \npt, mm, cm, in"
    if (lang == "DE"):
        UnitTypemesg = "Maßeinheit für die Randgröße: \npt, mm, cm"
    UnitType = valueDialog("Bleed and Marks", UnitTypemesg, "mm")

    if UnitType == "mm":
        UnitFakt = 1/25.4*72
        bleedVal = int(20.0/72*2.54*10)

    if UnitType == "cm":
        UnitFakt = 1/2.54*72
        bleedVal = 0.1*int(20.0/72*2.54*10)

    if UnitType == "in":
        UnitFakt = 72
        bleedVal = 20.0/72

    if UnitType == "pt":
        UnitType = "pt"
        UnitFakt = 1
        bleedVal = 20
    bleedValmesg = "Size of Bleed, automatically limited\n to half of vertical gap between pages["+ UnitType +"]:"
    if (lang == "DE"):
        bleedValmesg = "Größe des Beschnittrandes, automatisch beschränkt\n auf den halben vertikalen Abstand zwischen den Seiten ["+ UnitType +"]:"
    bleedVal = float(valueDialog("Bleed and Marks", bleedValmesg ,'%5.3f'% bleedVal))

    pageTypemesg1 = "Page Type"
    pageTypemesg2 = "Double first right = dr, Double first left = dl,\nSingle pages = s"
    if (lang == "DE"):
        pageTypemesg1 = "Seitenart"
        pageTypemesg2 = "Doppelseite, erste rechts = dr, Doppelseite, erste links = dl,\nEinzelne Seiten = s"
    TypeOfPages = valueDialog("Bleed and Marks - " + pageTypemesg1, pageTypemesg2,"dr")
    #which marks can be "l", "r", "b" and defines whether left, right or both marks are printed
    whichMarks = "b"

    if TypeOfPages <> "errfind":
        printCropmesg = "Print Crop Marks: 1 = Yes, 2 = No"
        printRegmesg = "Print Registration Marks: 1 = Yes, 2 = No"
        printCBarmesg = "Print Color Bar: 1 = Yes, 2 = No"
    if (lang == "DE"):
        printCropmesg = "Drucke Schnittmarken: 1 = Ja, 2 = Nein"
        printRegmesg = "Drucke Paßkreuze: 1 = Ja, 2 = Nein"
        printCBarmesg = "Drucke Farbbalken: 1 = Ja, 2 = Nein"

    doCropMarks = int(valueDialog("Bleed and Marks", printCropmesg,"1"))
    doRegMarks = int(valueDialog("Bleed and Marks", printRegmesg,"1"))
    doColorSamples = int(valueDialog("Bleed and Marks", printCBarmesg,"1"))

    jobname = valueDialog("Bleed and Marks", "Info Text" ,"Created by Scribus")
    if len(jobname) > 0:
        doJobText = int("1")
    else:
        doJobText = int("0")

    #preparing the file-environment

    tmpFileName = baseDirName + "tmp.sla"
    rightPageName = baseDirName + "rightpage.sla"
    leftPageName = baseDirName + "leftpage.sla"
    saveDocAs(tmpFileName)
    processmesg = "Processing the document, please wait"
    if (lang == "DE"):
        processmesg = "Dokument in Bearbeitung, bitte warten"
    messagebarText(processmesg)
    #closeDoc()
#    messagebarText("Processing the document, please wait - Dokument in Bearbeitung, bitte warten")

    #Here we clean-up the xml documents from illegal characters
    #Here we replace \x1A \x1B \x1C etc. in the Document to prevent expat from crashing
    #these are stored in the list charsToChange
    inFile = open(tmpFileName,"r")
    richtig = inFile.read()
    inFile.close()

    # define an uniqe string to replace the bad chars
    charsToChangeMark = "__bleed_and_export_" + '%4.0f'% (10000+80000*random.random())
    while richtig.find(charsToChangeMark) > (-1) :
       charsToChangeMark = "__bleed_and_export_" + '%4.0f'% (10000+80000*random.random())

    # change all bad chars
    toChangeCounter = 1000
    for toChange in charsToChange:
        richtig = richtig.replace(toChange,charsToChangeMark +"_"+ '%4i'% toChangeCounter)
        toChangeCounter = toChangeCounter + 1

    # write the corrected tmp-file
    outFile = open(tmpFileName,"w")
    outFile.write(richtig)
    outFile.close()

    if TypeOfPages == "errfind":
      # this helps to find the illegal ones
      LineNumber = int(valueDialog("bleed_and_export.py", "Line-Zeile" ,"1"))
      #ColNumber = int(valueDialog("bleed_and_export.py", "Collumn-Spalte" ,"1"))

      inFile = open(tmpFileName,"r")
      for x in range(LineNumber):
        Zeile = inFile.readline()

      inFile.close()
      suspectList = "Dangerous chars: "
      Spalte = 0

      for x in Zeile:
        if Zeile[Spalte:Spalte+3] == "&#x":
          suspect = Zeile[Spalte:Spalte+6]
          suspectList = suspectList + suspect[0:1+suspect.find(";")] + " "

        Spalte = Spalte + 1

      suspectListmesg = "The following would be valid: &#x9, &#xa, &#xd"
      if (lang == "DE"):
           suspectListmesg = "Achtung, folgende wären gültig: &#x9, &#xa, &#xd"
      messageBox("Bleed and Marks", suspectList + suspectListmesg, ICON_INFORMATION)


    if TypeOfPages == "s" or TypeOfPages =="dr" or TypeOfPages =="dl":
      #Here we make the xml-operations for left pages:

      xmldoc = minidom.parse(tmpFileName)
      theDocumentNode = xmldoc.getElementsByTagName('DOCUMENT')
      theDocumentNodeRef = theDocumentNode[0]

      thePageSetSetsNodeRef = theDocumentNodeRef.getElementsByTagName('PageSets')[0].getElementsByTagName('Set')

      for xRef in thePageSetSetsNodeRef:

          if float(xRef.attributes["GapBelow"].value) <= (2 * bleedVal*UnitFakt):

              bleedVal = float(xRef.attributes["GapBelow"].value) / UnitFakt / 2


      for xRef in thePageSetSetsNodeRef:
          xRef.attributes["GapBelow"].value = '%5.3f'%(float(xRef.attributes["GapBelow"].value) - 2 *bleedVal*UnitFakt)

      theDocumentNodeRef.attributes["PAGEHEIGHT"].value =  '%5.3f'%(float(theDocumentNodeRef.attributes["PAGEHEIGHT"].value) + 2 * bleedVal*UnitFakt)
      theDocumentNodeRef.attributes["PAGEWIDTH"].value =  '%5.3f'%(float(theDocumentNodeRef.attributes["PAGEWIDTH"].value) + 2 * bleedVal*UnitFakt)
      theDocumentNodeRef.attributes["ScratchTop"].value =  '%5.3f'%(float(theDocumentNodeRef.attributes["ScratchTop"].value) - bleedVal*UnitFakt)
      theDocumentNodeRef.attributes["ScratchLeft"].value =  '%5.3f'%(float(theDocumentNodeRef.attributes["ScratchLeft"].value) - bleedVal*UnitFakt)

      thePageNodeRef = theDocumentNodeRef.getElementsByTagName('PAGE')
      for xRef in thePageNodeRef :
          xRef.attributes["PAGEHEIGHT"].value =   '%5.3f'%(float(xRef.attributes["PAGEHEIGHT"].value) + 2 * bleedVal*UnitFakt)
          xRef.attributes["PAGEWIDTH"].value =   '%5.3f'%(float(xRef.attributes["PAGEWIDTH"].value) + 2 * bleedVal*UnitFakt)

      theMasterPageNodeRef = theDocumentNodeRef.getElementsByTagName('MASTERPAGE')

      for xRef in theMasterPageNodeRef :
          xRef.attributes["PAGEHEIGHT"].value = '%5.3f'%(float(xRef.attributes["PAGEHEIGHT"].value) + 2 * bleedVal*UnitFakt)
          xRef.attributes["PAGEWIDTH"].value =  '%5.3f'%(float(xRef.attributes["PAGEWIDTH"].value) + 2 * bleedVal*UnitFakt)
          xRef.attributes["PAGEXPOS"].value =   '%5.3f'%(float(xRef.attributes["PAGEXPOS"].value)  -  bleedVal*UnitFakt)
          xRef.attributes["PAGEYPOS"].value =   '%5.3f'%(float(xRef.attributes["PAGEYPOS"].value) -  bleedVal*UnitFakt)

      outxml  = xmldoc.toxml()

      #put back the bad  chars
      toChangeCounter = 1000
      for toChange in charsToChange:
        outxml = outxml.replace(charsToChangeMark +"_" + '%4i'% toChangeCounter, toChange)
        toChangeCounter = toChangeCounter + 1

      outFile = open(leftPageName, 'w')
      outFile.write(outxml[outxml.find("<SCRIBUS"):len(outxml)])
      outFile.close()
      outxml = "n"


    if TypeOfPages =="dr" or TypeOfPages =="dl":
       #Here we make the xml-operations for right pages of double sides documents

      theDocumentNodeRef.attributes["ScratchLeft"].value =  '%5.3f'%(float(theDocumentNodeRef.attributes["ScratchLeft"].value) - 2 * bleedVal*UnitFakt)

      outxml  = xmldoc.toxml()

      #put back the illegal char

      toChangeCounter = 1000
      for toChange in charsToChange:
        outxml = outxml.replace(charsToChangeMark +"_" + '%4i'% toChangeCounter, toChange)
        toChangeCounter = toChangeCounter + 1

      outFile = open(rightPageName, 'w')
      outFile.write(outxml[outxml.find("<SCRIBUS"):len(outxml)])
      outFile.close()
      outxml = "n"


    #From here we do the drawing and exporting to pdf

    if TypeOfPages == "dr":
      ##and here we open it

      openDoc(rightPageName)

      messagebarText(processmesg)

      seitenanzahl = pageCount()
      for xcounter in range(seitenanzahl):
          seitennummer = xcounter + 1
          if seitennummer%2 > 0:
             gotoPage(seitennummer)
             resultFileName = baseFileName + '_%(0)05i'% {"0":seitennummer} + "." + exportType
             # draw marks etc
             if doColorSamples == 1:
                DrawColorSamples(bleedVal,bgcol,fgcol,UnitFakt)
             if doCropMarks == 1:
                DrawCropMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks)
             if doJobText == 1:
                PrintJobName(jobname, resultFileName, bleedVal,bgcol,fgcol,UnitFakt,UnitType, seitennummer)
             if doRegMarks == 1:
                DrawRegMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks)
             # export one page
             dotheExport(exportType,resultFileName,seitennummer,bleedVal,UnitFakt)


      saveDoc()
      closeDoc()

      messagebarText(processmesg)

      openDoc(leftPageName)

      messagebarText(processmesg)

      seitenanzahl = pageCount()
      for xcounter in range(seitenanzahl ):
          seitennummer = xcounter + 1
          if seitennummer%2 == 0:
             gotoPage(seitennummer)
             resultFileName = baseFileName + '_%(0)05i'% {"0":seitennummer} + "." + exportType
             # draw marks etc
             if doColorSamples == 1:
                DrawColorSamples(bleedVal,bgcol,fgcol,UnitFakt)
             if doCropMarks == 1:
                DrawCropMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks)
             if doJobText == 1:
                PrintJobName(jobname, resultFileName, bleedVal,bgcol,fgcol,UnitFakt,UnitType, seitennummer)
             if doRegMarks == 1:
                DrawRegMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks)
             # export one page
             dotheExport(exportType,resultFileName,seitennummer,bleedVal,UnitFakt)


      saveDoc()
      closeDoc()
      os.remove(tmpFileName)


    if TypeOfPages == "s":

    ##and here we open it

      openDoc(leftPageName)

      messagebarText(processmesg)

      seitenanzahl = pageCount()

      for xcounter in range(seitenanzahl):
          seitennummer = xcounter + 1

          gotoPage(seitennummer)
          resultFileName = baseFileName + '_%(0)05i'% {"0":seitennummer} + "." + exportType
          # draw marks etc
          if doColorSamples == 1:
                DrawColorSamples(bleedVal,bgcol,fgcol,UnitFakt)
          if doCropMarks == 1:
                DrawCropMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks)
          if doJobText == 1:
                PrintJobName(jobname, resultFileName, bleedVal,bgcol,fgcol,UnitFakt,UnitType, seitennummer)
          if doRegMarks == 1:
                DrawRegMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks)

             # export one page
          dotheExport(exportType,resultFileName,seitennummer,bleedVal,UnitFakt)


      saveDoc()
      #closeDoc()
      os.remove(tmpFileName)


    if TypeOfPages == "dl":


      ##and here we open it

      openDoc(rightPageName)

      messagebarText(processmesg)

      seitenanzahl = pageCount()
      for xcounter in range(seitenanzahl ):
          seitennummer = xcounter + 1
          if seitennummer%2 == 0:
             gotoPage(seitennummer)
             resultFileName = baseFileName + '_%(0)05i'% {"0":seitennummer} + "." + exportType
             # draw marks etc
             if doColorSamples == 1:
                DrawColorSamples(bleedVal,bgcol,fgcol,UnitFakt)
             if doCropMarks == 1:
                DrawCropMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks)
             if doJobText == 1:
                PrintJobName(jobname, resultFileName, bleedVal,bgcol,fgcol,UnitFakt,UnitType, seitennummer)
             if doRegMarks == 1:
                DrawRegMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks)
             # export one page
             dotheExport(exportType,resultFileName,seitennummer,bleedVal,UnitFakt)


      saveDoc()
      closeDoc()
      messagebarText(processmesg)
      openDoc(leftPageName)
      messagebarText(processmesg)

      seitenanzahl = pageCount()
      for xcounter in range(seitenanzahl ):
          seitennummer = xcounter + 1
          if seitennummer%2 > 0:
             gotoPage(seitennummer)
             resultFileName = baseFileName + '_%(0)05i'% {"0":seitennummer} + "." + exportType
             # draw marks etc
             if doColorSamples == 1:
                DrawColorSamples(bleedVal,bgcol,fgcol,UnitFakt)
             if doCropMarks == 1:
                DrawCropMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks)
             if doJobText == 1:
                PrintJobName(jobname, resultFileName, bleedVal,bgcol,fgcol,UnitFakt,UnitType, seitennummer)
             if doRegMarks == 1:
                DrawRegMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks)
             # export one page
             dotheExport(exportType,resultFileName,seitennummer,bleedVal,UnitFakt)

      saveDoc()
      closeDoc()

    # OK, it's ugly, but it ensures the tmp files deletion
    try:
        os.remove(tmpFileName)
    except OSError:
        pass
    try:
        os.remove(rightPageName)
    except OSError:
        pass
    try:
        os.remove(leftPageName)
    except OSError:
        pass

    setUnit(userUnit)
    setRedraw(True)


def dotheExport(exportType,resultFileName,seitennummer,bleedVal,UnitFakt):
    # Die Dimension der Eingabewerte fuer bleedValue ist in der jeweiligen Einheit
    if exportType == "pdf":
      pdfExport =  PDFfile()
      pdfExport.bleedt = bleedVal*UnitFakt
      pdfExport.bleedb = bleedVal*UnitFakt
      pdfExport.bleedl = bleedVal*UnitFakt
      pdfExport.bleedr = bleedVal*UnitFakt
      pdfExport.info = resultFileName
      pdfExport.pages = [seitennummer]
      pdfExport.file = resultFileName
      pdfExport.save()

   # if exportType == "ps":
   #   psExport = Printer()
   #   psExport.file = resultFileName
   #   psExport.copies = 1
   #   psExport.pages = [seitennummer]
   #   psExport.printer = "File"
   #   psExport.print()

def PrintJobName(jobname, resultFileName, bleedVal,bgcol,fgcol,UnitFakt,UnitType,seitennummer):
    # Die Dimension der Eingabewerte fuer bleedValue ist in der jeweiligen Einheit
    Pagemesg = "  Page: "
    Datemesg = "  Date: "
    if (lang == "DE"):
        Pagemesg = "  Seite: "
        Datemesg = "  Datum: "
    shortresultFileName = resultFileName[-23:] + Pagemesg + '%(0)05i'% {"0":seitennummer} + Datemesg +  date.today().strftime("%Y-%m-%d")
    pageX,pageY = getPageSize()
    textboxT = createText(bleedVal*UnitFakt+2, 1, pageX/2 - 12 - bleedVal*UnitFakt, bleedVal*UnitFakt-10)
    setTextColor(fgcol,textboxT)
    setLineWidth(0,textboxT)
    setLineColor(bgcol,textboxT)
    setFillColor(bgcol,textboxT)
    insertText(shortresultFileName, 0,textboxT )
    setFontSize(6, textboxT)
    textboxB1 = createText(bleedVal*UnitFakt+2, pageY-bleedVal*UnitFakt + 8, pageX/2 - 12 - bleedVal*UnitFakt, bleedVal*UnitFakt-9)
    setTextColor(fgcol,textboxB1)
    setLineWidth(0,textboxB1)
    setLineColor(bgcol,textboxB1)
    setFillColor(bgcol,textboxB1)
    cropmesg = ", Crop:"
    if (lang == "DE"):
        cropmesg = ", Beschnitt:"
    insertText("Total: " + '%5.2f'% (pageX/UnitFakt)  + "x" + '%5.2f'% (pageY/UnitFakt)+"["+UnitType+"]" + cropmesg + '%5.2f'% bleedVal+"["+UnitType+"]" + ", Prod.:" + '%5.2f'% (pageX/UnitFakt - 2 * bleedVal) + "x"+ '%5.2f'% (pageY/UnitFakt - 2 * bleedVal)+"["+UnitType+"]", 0,textboxB1 )
    setFontSize(6, textboxB1)
    setLineSpacing(8,textboxB1)
    textboxB2 = createText(pageX/2 + 10, pageY-bleedVal*UnitFakt + 8, pageX/2 - 12 - bleedVal*UnitFakt, bleedVal*UnitFakt-9)
    setTextColor(fgcol,textboxB2)
    setLineWidth(0,textboxB2)
    setLineColor(bgcol,textboxB2)
    setFillColor(bgcol,textboxB2)
    insertText(jobname , 0,textboxB2 )
    setFontSize(6, textboxB2)
    setLineSpacing(8,textboxB2)




def DrawColorSamples(bleedVal,bgcol,fgcol,UnitFakt):

    defineColor("bleed_export_c_100",255,  0,  0,  0)
    defineColor("bleed_export_c__80",204,  0,  0,  0)
    defineColor("bleed_export_c__40",102,  0,  0,  0)

    defineColor("bleed_export_m_100",  0,255,  0,  0)
    defineColor("bleed_export_m__80",  0,204,  0,  0)
    defineColor("bleed_export_m__40",  0,102,  0,  0)

    defineColor("bleed_export_y_100",  0,  0,255,  0)
    defineColor("bleed_export_y__80",  0,  0,204,  0)
    defineColor("bleed_export_y__40",  0,  0,102,  0)

    defineColor("bleed_export_k_100",  0,  0,  0,255)
    defineColor("bleed_export_k__80",  0,  0,  0,204)
    defineColor("bleed_export_k__40",  0,  0,  0,102)

    defineColor("bleed_export_cmy50",128,128,128,  0)

    pageX,pageY = getPageSize()
    boxw = bleedVal*UnitFakt - 10
    if boxw > 20:
      boxw = 20
    FontSize = boxw/4
    if FontSize < 2 :
      FontSize = 2
    boxdist = 5
    boxh = ((pageY - 20 - bleedVal*UnitFakt*2 - 20)  /  13) - boxdist
    if boxh > boxw:
      boxh = boxw
    upperLeftx = pageX - boxw
    upperLefty = bleedVal*UnitFakt + 5
    gruppenListe = list()
    for Farbe in ["bleed_export_c_100","bleed_export_c__80","bleed_export_c__40","bleed_export_m_100","bleed_export_m__80","bleed_export_m__40","bleed_export_y_100","bleed_export_y__80","bleed_export_y__40","bleed_export_k_100","bleed_export_k__80","bleed_export_k__40","bleed_export_cmy50"]:

       if upperLefty > pageY/2 - (FontSize * 1.5 + boxh + + 7 + 15):
         if upperLefty < pageY/2 - 15:
            upperLefty = pageY/2 + 20


       tbox = createText(upperLeftx, upperLefty, boxw, FontSize * 4)
       insertText(Farbe[len(Farbe)-5:len(Farbe)] , 0, tbox)
       setFontSize(FontSize, tbox)
       setLineSpacing(FontSize, tbox)
       setTextColor("regcol",tbox)
       setLineWidth(0, tbox)
       setLineColor(bgcol, tbox)
       setFillColor(bgcol, tbox)

       upperLefty = upperLefty + FontSize * 1.8

       cbox = createRect(upperLeftx, upperLefty, boxw, boxh)
       setLineWidth(0, cbox)
       setLineColor(Farbe, cbox)
       setFillColor(Farbe, cbox)

       upperLefty = upperLefty + boxh + 7

       gruppenListe.append(cbox)
       gruppenListe.append(tbox)


    groupObjects(gruppenListe)

def DrawCropMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks):
    # Die Dimension der Eingabewerte fuer bleedValue ist in der jeweiligen Einheit
    pageX,pageY = getPageSize()
    # line widths unit pt
    lwb = 3.0
    lwf = 0.25

    if whichMarks == "l" or whichMarks == "b":
       # top left:
       b01 = createLine(bleedVal*UnitFakt, bleedVal*UnitFakt - 9,  bleedVal*UnitFakt, 0)
       b02 = createLine(0,  bleedVal*UnitFakt, bleedVal*UnitFakt -9 , bleedVal*UnitFakt)
       setLineWidth(lwb, b01)
       setLineWidth(lwb, b02)
       setLineColor(bgcol,b01)
       setLineColor(bgcol,b02)
       f01 = createLine(bleedVal*UnitFakt, bleedVal*UnitFakt - 9,  bleedVal*UnitFakt, 0)
       f02 = createLine(0,  bleedVal*UnitFakt, bleedVal*UnitFakt -9 , bleedVal*UnitFakt)
       setLineWidth(lwf, f01)
       setLineWidth(lwf, f02)
       setLineColor(fgcol,f01)
       setLineColor(fgcol,f02)

       # bottom left:
       b05 = createLine(bleedVal*UnitFakt ,pageY-bleedVal*UnitFakt + 9 ,  bleedVal*UnitFakt ,pageY)
       b06 = createLine(0,pageY-bleedVal*UnitFakt,  bleedVal*UnitFakt -9 ,pageY-bleedVal*UnitFakt)
       setLineWidth(lwb, b05)
       setLineWidth(lwb, b06)
       setLineColor(bgcol,b05)
       setLineColor(bgcol,b06)
       f05 = createLine(bleedVal*UnitFakt ,pageY-bleedVal*UnitFakt + 9 ,  bleedVal*UnitFakt ,pageY)
       f06 = createLine(0,pageY-bleedVal*UnitFakt,  bleedVal*UnitFakt -9 ,pageY-bleedVal*UnitFakt)
       setLineWidth(lwf, f05)
       setLineWidth(lwf, f06)
       setLineColor(fgcol,f05)
       setLineColor(fgcol,f06)

    if whichMarks == "r" or whichMarks == "b":
       # top right:
       b03 = createLine(pageX - bleedVal*UnitFakt + 9, bleedVal*UnitFakt,  pageX ,bleedVal*UnitFakt)
       b04 = createLine(pageX - bleedVal*UnitFakt,0,  pageX-bleedVal*UnitFakt,bleedVal*UnitFakt - 9)
       setLineWidth(lwb, b03)
       setLineWidth(lwb, b04)
       setLineColor(bgcol,b03)
       setLineColor(bgcol,b04)
       f03 = createLine(pageX - bleedVal*UnitFakt + 9, bleedVal*UnitFakt,  pageX ,bleedVal*UnitFakt)
       f04 = createLine(pageX - bleedVal*UnitFakt,0,  pageX-bleedVal*UnitFakt,bleedVal*UnitFakt - 9)
       setLineWidth(lwf, f03)
       setLineWidth(lwf, f04)
       setLineColor(fgcol,f03)
       setLineColor(fgcol,f04)

       # bottom rigth:
       b07 = createLine(pageX-bleedVal*UnitFakt ,pageY-bleedVal*UnitFakt + 9 ,   pageX-bleedVal*UnitFakt,pageY)
       b08 = createLine(pageX,pageY-bleedVal*UnitFakt, pageX-bleedVal*UnitFakt + 9 ,pageY-bleedVal*UnitFakt)
       setLineWidth(lwb, b07)
       setLineWidth(lwb, b08)
       setLineColor(bgcol,b07)
       setLineColor(bgcol,b08)
       f07 = createLine(pageX-bleedVal*UnitFakt ,pageY-bleedVal*UnitFakt + 9 ,   pageX-bleedVal*UnitFakt,pageY)
       f08 = createLine(pageX,pageY-bleedVal*UnitFakt, pageX-bleedVal*UnitFakt + 9 ,pageY-bleedVal*UnitFakt)
       setLineWidth(lwf, f07)
       setLineWidth(lwf, f08)
       setLineColor(fgcol,f07)
       setLineColor(fgcol,f08)



def DrawRegMarks(bleedVal,bgcol,fgcol,UnitFakt,whichMarks):

    # Die Dimension der Eingabewerte fuer bleedValue ist in der jeweiligen Einheit
    pageX,pageY = getPageSize()

    if whichMarks == "l" or whichMarks == "b":
       # left mark:
       DrawOneReg(bleedVal*UnitFakt-12.5,pageY/2,bgcol,fgcol)

    if whichMarks == "r" or whichMarks == "b":
       # rigth mark:
       DrawOneReg(pageX-bleedVal*UnitFakt+12.5,pageY/2,bgcol,fgcol)

    # top mark:
    DrawOneReg(pageX/2,bleedVal*UnitFakt-12.5,bgcol,fgcol)
    # bottom mark:
    DrawOneReg(pageX/2,pageY-bleedVal*UnitFakt+12.5,bgcol,fgcol)


def DrawOneReg(centerX,centerY,bgcol,fgcol):
    # Diese Funktion muss in der Einheit Punkt aufgerufen werden
    outercircle = createEllipse(centerX-7.5,centerY-7.5 , 15, 15)
    middlecircle = createEllipse(centerX-5.5,centerY-5.5 , 11, 11)
    innercircle =  createEllipse(centerX-2.5,centerY-2.5 , 5, 5)
    lin01 = createLine(centerX-7.5, centerY,  centerX-2.5, centerY)
    lin02 = createLine(centerX+2.5, centerY,  centerX+7.5, centerY)
    lin03 = createLine(centerX, centerY-7.5,  centerX, centerY-2.5)
    lin04 = createLine(centerX, centerY+7.5,  centerX, centerY+2.5)

    lin05 = createLine(centerX-2.5, centerY,  centerX+2.5, centerY)
    lin06 = createLine(centerX, centerY-2.5,  centerX, centerY+2.5)

    # line widths in Poinzs
    lwb = 3.0
    lwf = 0.25

    setLineWidth(0,outercircle)
    setLineColor(bgcol,outercircle)
    setFillColor(bgcol,outercircle)
    setLineWidth(lwf,middlecircle)
    setLineColor(fgcol,middlecircle)
    setFillColor(bgcol,middlecircle)
    setLineWidth(lwf,innercircle)
    setLineColor(fgcol,innercircle)
    setFillColor(fgcol,innercircle)
    setLineWidth(lwf,lin01)
    setLineWidth(lwf,lin02)
    setLineWidth(lwf,lin03)
    setLineWidth(lwf,lin04)
    setLineWidth(lwf,lin05)
    setLineWidth(lwf,lin06)
    setLineColor(fgcol,lin01)
    setLineColor(fgcol,lin02)
    setLineColor(fgcol,lin03)
    setLineColor(fgcol,lin04)
    setLineColor(bgcol,lin05)
    setLineColor(bgcol,lin06)


if __name__ == '__main__':
    lang = valueDialog("Dialog Language - " + os.name, "Delete or alter this value to have dialogs in German" ,"English")
    if (lang != "English"):
        lang = "DE"
    if haveDoc():
        main()
    else:
        docerrmesg = "There must be an open document."
    if (lang == "DE"):
        docerrmesg = "Es muß ein Dokument geöffnet sein."
        messageBox("Bleed and Marks", docerrmesg, ICON_INFORMATION)
