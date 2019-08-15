
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 inviwo_bin_path"
    echo "Example: $0 /home/user/inviwo/build/bin"
    exit 0
fi
npm install
sed -i "s+^PATH_INVIWO_BIN.*+PATH_INVIWP_BIN="$1"+g" envisionpy/EnvisionMain.py
# TODO make it work for other platforms
# TODO also fix paths to envisionpy in /scripts/* files. Those have to be set manually right now