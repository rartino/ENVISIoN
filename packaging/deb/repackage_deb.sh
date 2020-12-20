#!/bin/bash
# Repackages the generated .deb package from the inviwobuild. The package is not valid by default.
# Also build and inserts envision
echo "__Repackaging .deb__"
echo "Extracting package..."
rm -r unpack/
dpkg -x Inviwo-v0.9.11.deb unpack/

echo "Restructuring package..."
# Move files to more sensible places and remove unused files.
rm -r unpack/usr/share
mkdir -p unpack/usr/share/envision/inviwo
mv unpack/usr/[^share]* unpack/usr/share/envision/inviwo
mv unpack/usr/share/envision/inviwo/bin/*.so* unpack/usr/share/envision/inviwo/lib
rm -r unpack/usr/share/envision/inviwo/bin/[^inviwo]*
rm -r unpack/usr/share/envision/inviwo/lib/cmake unpack/usr/share/envision/inviwo/lib/pkgconfig

echo "Building envision electron package..."
npm run-script build-package --prefix $1
sed -i 's/ElectronUI\/nodeInterface.py/\/usr\/share\/envision\/ENVISIoN\/resources\/app\/ElectronUI\/nodeInterface.py/g' $1/envision-linux-x64/resources/app/ElectronUI/js/pythonInterface.js

echo "Inserting envision app..."
mkdir -p unpack/usr/share/envision/ENVISIoN
cp -r $1/envision-linux-x64/* unpack/usr/share/envision/ENVISIoN
mv unpack/usr/share/envision/ENVISIoN/resources/app/scripts unpack/usr/share/envision
rm -r unpack/usr/share/envision/ENVISIoN/resources/app/[^envisionpy,^ElectronUI,^node_modules]*

echo "Inserting files..."
mkdir unpack/usr/bin
cp $1/packaging/deb/envision-inviwo unpack/usr/bin
cp $1/packaging/deb/envision unpack/usr/bin

echo "Inserting metadata..."
mkdir unpack/DEBIAN
cp $1/packaging/deb/control unpack/DEBIAN

echo "Building package..."
dpkg -b unpack .
rm -r unpack/

echo "deb package built"


