#!/bin/bash
set -e

ZIP_EXE="/c/Program Files/7-Zip/7z.exe"

build() {

	rm -rf dist build

  local PYTHON_EXE=$1
  local VENV_DIR=$2
  local DIST_DIR=$3
  local ZIP_NAME=$4

  echo "Creating virtual environment ($VENV_DIR)..."
  "$PYTHON_EXE" -m venv "$VENV_DIR"

  if [[ ! -f "$VENV_DIR/Scripts/activate" ]]; then
    echo "Activation script not found in $VENV_DIR. Exiting."
    exit 1
  fi

  echo "Activating virtual environment ($VENV_DIR)..."
  source "$VENV_DIR/Scripts/activate"

  if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Failed to activate virtual environment $VENV_DIR. Exiting."
    exit 1
  fi

  echo "Virtual environment activated: $VIRTUAL_ENV"

  echo "Installing requirements..."
  pip install -r requirements.txt

  echo "Running PyInstaller..."
  pyinstaller --clean --onedir --icon=icon.ico --name=audio2images audio2images.py \
    --hidden-import=sys \
    --hidden-import=runpy \
    --hidden-import=os \
    --hidden-import=traceback \
    --hidden-import=functools \
    --hidden-import=math \
    --hidden-import=re \
    --hidden-import=subprocess \
    --hidden-import=argparse \
    --hidden-import=numpy \
    --hidden-import=soundfile \
    --hidden-import=PIL \
    --hidden-import=PIL.Image \
    --hidden-import=PIL.ImageDraw \
    --add-data "color_schemes.py;." \
    --add-data "processing.py;." \
    --add-data "LICENSE.txt;." \
    --add-data "wav2png.py;." 

  echo "Copying extra files..."
  cp TestSound.ogg "dist/audio2images"

  echo "Renaming output folder..."
  mv dist/audio2images dist/"$DIST_DIR"

  echo "Creating zip archive..."
  cd dist/
	[ -f "../$ZIP_NAME.zip" ] && rm "../$ZIP_NAME.zip"
  "$ZIP_EXE" a -tzip ../"$ZIP_NAME.zip" "$DIST_DIR" -mx=2
  cd ..

  echo "Deactivating virtual environment ($VENV_DIR)..."
  deactivate
}


# Path psychosis
export BACKUPPATH=$PATH

echo $PATH | grep --color Python

# 64 bit
export PATH=`echo $BACKUPPATH | sed 's/Python310/Python38/g' | sed 's/Python313/Python38/g'`

echo $PATH | grep --color -oP '.{0,10}Python.{0,10}'

echo "Building 64-bit version..."
build "/c/Python38/python.exe" "venv64" "audio2images-win64" "audio2images-win64"

# 32 bit
export PATH=`echo $BACKUPPATH | sed 's/Python310/Python38-32/g' | sed 's/Python313/Python38-32/g'`

echo $PATH | grep --color -oP '.{0,10}Python.{0,10}'

echo "Building 32-bit version..."
build "/c/Python38-32/python.exe" "venv32" "audio2images-win32" "audio2images-win32"

# Path back
export PATH=$BACKUPPATH

echo $PATH | grep --color -oP '.{0,10}Python.{0,10}'

echo "Builds complete."
