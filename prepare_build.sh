#!/bin/bash

# All this mess assumes Python is in C:/Python38 and Python310 and Python313 are in PATH...

# Path psychosis
export BACKUPPATH=$PATH

# 64 bit
export PATH=`echo $BACKUPPATH | sed 's/Python310/Python38/g' | sed 's/Python313/Python38/g'`

which python
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller
pip install --upgrade soundfile Pillow
pip install numpy==1.23.5
python -m pip show pyinstaller | grep ^Version
python -m pip show numpy | grep ^Version


# 32 bit
export PATH=`echo $BACKUPPATH | sed 's/Python310/Python38-32/g' | sed 's/Python313/Python38-32/g'`

which python
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller
pip install --upgrade soundfile Pillow
pip install numpy==1.23.5
python -m pip show pyinstaller | grep ^Version
python -m pip show numpy | grep ^Version


# Path back
export PATH=$BACKUPPATH