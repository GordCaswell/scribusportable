Some preliminary notes:

(This will all be obsolete once CMake is used.)


The file configure.MacOSX contains the call to ./configure that *I* use to create a MacOSX application bundle for Scribus. Recently another user has used
this instructions to compile Scribus on an Intel-Mac.

If you use fink, install libart, libjpeg, libtiff, libpng, lcms and freetype219.
Make sure that freetype-config and pkg-config pick up the right libraries 
(freetype under /usrX11R6 is unusable).
Don't forget to set QTDIR and include $QTDIR/bin in your PATH.

To compile Scribus:

  source configure.MacOSX
  make
  make_install
  ./install_MacOSX.sh 


The last command does automatically what is explained in the following section:

Scribus.app contains some files for the OSX application bundle infrastructure:

Contents/Info.plist	application properties
Contents/Resources	application icons
Contents/MacOS		application binary

Currently you have to copy the Info.plist and the icon files to the install location yourself
and create a sysmlink in MacOS:

bash$ cd Contents/MacOS
bash$ ln -s ../bin/scribus Scribus




