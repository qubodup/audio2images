# audio2images.py
import runpy
import sys
import os

# Set arguments to pass through
sys.argv = ["wav2png.py"] + sys.argv[1:]

# Get correct path whether running source or bundled
if hasattr(sys, "_MEIPASS"):
    script_path = os.path.join(sys._MEIPASS, "wav2png.py")
else:
    script_path = os.path.abspath("wav2png.py")

# Run the script
runpy.run_path(script_path, run_name="__main__")
