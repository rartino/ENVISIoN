if [ "$#" -ne 2 ]; then
    echo "Usage: $0 envision_path inviwo_build_path"
    echo "Example: $0 /home/user/ENVISIoN /home/user/inviwo/build"
    exit 0
fi

cd "$2"
mkdir unpack unpack/DEBIAN
# dpkg -b oldpack/ unpack/

echo "Extracting -deb package..."
dpkg -x Inviwo-v0.9.10.deb unpack/
dpkg -e Inviwo-v0.9.10.deb unpack/DEBIAN

# Repackage inviwo

cd unpack
mkdir opt opt/envision 
mkdir opt/envision/inviwo opt/envision/inviwo/bin opt/envision/inviwo/data
# mkdir opt/envision/inviwo/data

shopt -s extglob

# mv usr/bin/*~inviwo* opt/envision/inviwo/lib/
echo "Moving inviwo .so files..."
mv usr/lib opt/envision/inviwo/
mv usr/bin/!(inviwo*) opt/envision/inviwo/lib/
mv usr/bin/inviwo* opt/envision/inviwo/bin/

mv usr/data opt/envision/inviwo/data
mv usr/include opt/envision/inviwo/data
mv usr/modules opt/envision/inviwo/data
mv usr/licenses opt/envision/inviwo/data
mv usr/local opt/envision/inviwo/data
mv usr/tests opt/envision/inviwo/data

# TODO remove unneccicary files

# Add qt libs
echo "Copying qt library..."
mkdir opt/envision/qt 
cp -r /opt/qt512/5.12.2/gcc_64/lib opt/envision/qt
cp -r /opt/qt512/5.12.2/gcc_64/plugins opt/envision/qt

# Add envision to package
# mkdir opt/envision/envision
echo "Building envision electron app..."
cd opt/envision/
electron-packager $1

echo "Fixing and cleaning up envision files..."
cd envision-linux-x64/resources/app/
# This relative path will not work anymore
sed -i 's/ElectronUI\/nodeInterface.py/\/opt\/envision\/envision-linux-x64\/resources\/app\/ElectronUI\/nodeInterface.py/g' ElectronUI/js/pythonInterface.js
sed -i "s+^PATH_INVIWO_BIN.*+PATH_INVIWO_BIN='/opt/envision/inviwo/bin'+g" envisionpy/EnvisionMain.py
sed -i "s+true+false+g" ElectronUI/config.json
# sed -i 
rm -r inviwo/
rm -r docs/


# Add start script executables to bin
echo "Copying start scripts..."
cd $2/unpack
cp $1/packaging/envision-inviwo usr/bin/
cp $1/packaging/envision usr/bin/

# Update deb package info
rm DEBIAN/control
cp $1/packaging/control DEBIAN/

# Create package
echo "Building package (can take a few minutes)..."
cd $2
mkdir envision_package
dpkg -b unpack/ envision_package/



