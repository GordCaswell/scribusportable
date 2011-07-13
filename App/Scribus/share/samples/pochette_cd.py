#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This script creates a CD Pochette - a paper pocket for CD/DVD disc """

import sys

try:
    from scribus import *
except ImportError:
    print "This script only runs from within Scribus."
    sys.exit(1)

margins = (0, 0, 0, 0)
paper = (210, 297)

def main():
    if newDocument(paper, margins, 1, 1, 1, NOFACINGPAGES, FIRSTPAGELEFT,1):
        setUnit(1)
        newPage(-1)
        gotoPage(1)
        createLayer("normal")
        setActiveLayer("normal")
        a = createText(98.5, 20, 100, 10)
        setText("CD pochette - front page", a)
        setFontSize(11, a)
        setTextAlignment(1, a)
        b = createText(28.5, 45, 120, 120)
        setFillColor("None", b)
        c = createText(148.5, 45, 120, 120)
        setFillColor("None", c)
        createLayer("bords_perdus")
        setActiveLayer("bords_perdus")
        img1 = createImage(24.35, 41.25 , 124.20, 127.95,)
        img2 = createImage(148.55, 41.25 , 124.20, 127.95,)
        createLayer("coupe")
        setActiveLayer("coupe")
        t1 = createLine(28.5, 38, 28.5, 43)
        setLineWidth(0.1, t1)
        t2 = createLine(148.5, 38, 148.5, 43)
        setLineWidth(0.1, t2)
        t3 = createLine(268.5, 38, 268.5, 43)
        setLineWidth(0.1, t3)
        t4 = createLine(28.5, 172, 28.5, 167)
        setLineWidth(0.1, t4)
        t5 = createLine(148.5, 172, 148.5, 167)
        setLineWidth(0.1, t5)
        t6 = createLine(268.5, 172, 268.5, 167)
        setLineWidth(0.1, t6)
        t7 = createLine(21.5, 45, 26.5, 45)
        setLineWidth(0.1, t7)
        t8 = createLine(21.5, 165, 26.5, 165)
        setLineWidth(0.1, t8)
        t9 = createLine(270.5, 45, 275.5, 45)
        setLineWidth(0.1, t9)
        t10 = createLine(270.5, 165, 275.5, 165)
        setLineWidth(0.1, t10)
        gotoPage(2)
        setActiveLayer("normal")
        a2 = createText(98.5, 20, 100, 10)
        setText("CD pochette - back page", a2)
        setFontSize(11, a2)
        setTextAlignment(1, a2)
        a2t = createText(204, 44, 78, 9)
        setText("Mode d'emploi :", a2t)
        setFontSize(13, a2t)
        setTextAlignment(1, a2t)
        a21 = createText(204, 54, 78, 87)
        setText("Usage. TODO: tranlslate it from french", a21)
        setFontSize(11, a21)
        setTextAlignment(0, a21)
        b2 = createText(28.5, 162.10, 117, 6)
        setText("Texte sur la tranche", b2)
        setFontSize(9, b2)
        setTextAlignment(1, b2)
        rotateObjectAbs(90, b2)
        setFillColor("None", b2)
        c2 = createText(34.5, 45, 137.5, 117)
        setFillColor("None", c2)
        d2 = createText(28.5, 162.10, 117, 6)
        setText("Texte sur la tranche", d2)
        setFontSize(9, d2)
        setTextAlignment(1, d2)
        rotateObjectAbs(90, d2)
        setFillColor("None", d2)
        moveObject(143.5, 0, d2)
        setActiveLayer("bords_perdus")
        img3 = createImage(24.35, 41.25 , 157.50, 126.50,)
        setActiveLayer("coupe")
        t21 = createLine(28.5, 38, 28.5, 43)
        setLineWidth(0.1, t21)
        t22 = createLine(34.5, 38, 34.5, 43)
        setLineWidth(0.1, t22)
        t23 = createLine(172, 38, 172, 43)
        setLineWidth(0.1, t23)
        t24 = createLine(178, 38, 178, 43)
        setLineWidth(0.1, t24)
        t25 = createLine(28.5, 164.5, 28.5, 169.5)
        setLineWidth(0.1, t25)
        t26 = createLine(34.5, 164, 34.5, 169.5)
        setLineWidth(0.1, t26)
        t27 = createLine(172, 164, 172, 169.5)
        setLineWidth(0.1, t27)
        t28 = createLine(178, 164, 178, 169.5)
        setLineWidth(0.1, t28)
        t29 = createLine(22.5, 45, 27.5, 45)
        setLineWidth(0.1, t29)
        t30 = createLine(22.5, 162, 27.5, 162)
        setLineWidth(0.1, t30)
        t31 = createLine(179.5, 45, 184.5, 45)
        setLineWidth(0.1, t31)
        t32 = createLine(179.5, 162, 184.5, 162)
        setLineWidth(0.1, t32)
        saveDocAs("pochette_CD.sla")

if __name__ == '__main__':
    main()
