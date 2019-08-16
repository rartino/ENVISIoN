# TODO make it work for other platforms

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 inviwo_bin_path ENVISIoN_path"
    echo "Example: $0 /home/user/inviwo/build/bin /home/user/ENVISIoN"
    exit 0
fi
cd $2
npm install
sed -i "s+^PATH_INVIWO_BIN.*+PATH_INVIWO_BIN='$1'+g" envisionpy/EnvisionMain.py



cd $2
sed -i "s+^PATH_TO_ENVISION.*+PATH_TO_ENVISION='$2'+g" scripts/*.py
