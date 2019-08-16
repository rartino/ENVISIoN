
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 inviwo_bin_path"
    echo "Example: $0 /home/user/inviwo/build/bin"
    exit 0
fi
# cd $2
npm install
sed -i "s+^PATH_INVIWO_BIN.*+PATH_INVIWO_BIN='$1'+g" envisionpy/EnvisionMain.py
# TODO make it work for other platforms
# TODO also make script fix paths to envisionpy in /scripts/* files. Those have to be set manually right now