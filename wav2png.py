#!/usr/bin/env python

#
# Freesound is (c) MUSIC TECHNOLOGY GROUP, UNIVERSITAT POMPEU FABRA
#
# Freesound is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Freesound is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Freesound refers to https://github.com/MTG/freesound/graphs/contributors
#     qubodup made this 'portable' kind of
#


try:
    import argparse
    from processing import create_wave_images, AudioProcessingException
    import sys

except Exception as e:
    print("Error during import:")
    print(e)
    import traceback
    traceback.print_exc()
    with open("wav2png_import_error.txt", "w") as f:
        traceback.print_exc(file=f)
    sys.exit(1)


def progress_callback(position, width):
    percentage = (position * 100) // width
    if position % (width // 10) == 0:
        sys.stdout.write(str(percentage) + "% ")
        sys.stdout.flush()


def main(args):
    # process all files so the user can use wildcards like *.wav
    for input_file in args.files:

        output_file_w = input_file + "_w.png"
        output_file_s = input_file + "_s.jpg"

        this_args = (input_file, output_file_w, output_file_s, args.width, args.height, args.fft_size,
                     progress_callback, args.color_scheme)

        print(f"processing file {input_file}:\n\t", end="")

        try:
            create_wave_images(*this_args)
        except AudioProcessingException as e:
            print(f"Error running wav2png: {e}")
        print("")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("files", help="files to process", nargs="+")
    parser.add_argument("-w", "--width", type=int, default=500, dest="width",
                        help="image width in pixels")
    parser.add_argument("-H", "--height", type=int, default=171, dest="height",
                        help="image height in pixels")
    parser.add_argument("-f", "--fft", type=int, default=2048, dest="fft_size",
                        help="fft size, power of 2 for increased performance")
    parser.add_argument("-c", "--color_scheme", type=str, default='BleepBloop', dest="color_scheme",
                        help="name of the color scheme to use (one of: 'Freesound2' (default), 'FreesoundBeastWhoosh', "
                             "'Cyberpunk', 'Rainforest', there's more... make your own...)")

    args = parser.parse_args()
    main(args)
