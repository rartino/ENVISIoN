#!/bin/bash
shopt -s extglob


echo "__Repackaging .tar__"
echo "Extracting package..."
rm -r unpack-tar/
mkdir unpack-tar/
tar -xzf Inviwo-v0.9.11.tar.gz -C unpack-tar --strip-components 1

echo "Restructuring package..."
rm -r unpack-tar/share unpack-tar/include
mkdir unpack-tar/inviwo
mv unpack-tar/[^inviwo]* unpack-tar/inviwo # move all files into /inviwo sub-dir
mv unpack-tar/inviwo/bin/*.so* unpack-tar/inviwo/lib # move .so files
rm -r unpack-tar/inviwo/bin/[^inviwo]*
rm -r unpack-tar/inviwo/lib/cmake unpack-tar/inviwo/lib/pkgconfig

echo "Building envision electron package..."
npm run-script build-package --prefix $1

echo "Inserting envision app..."
mkdir unpack-tar/ENVISIoN
cp -r $1/envision-linux-x64/* unpack-tar/ENVISIoN
mv unpack-tar/ENVISIoN/resources/app/scripts unpack-tar/
rm -r unpack-tar/ENVISIoN/resources/app/[^envisionpy,^ElectronUI,^node_modules]*

echo "Inserting files..."
mkdir unpack-tar/bin
cp -r $1/packaging/tar/bin unpack-tar/

echo "Compressing directory..."
cd unpack-tar/
tar -czf ../envision_2.1.0_amd64.tar.gz *
cd ..
rm -r unpack-tar/
echo "tar package built."