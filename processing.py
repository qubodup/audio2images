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
    import math
    import os
    import sys
    import re
    import subprocess
    import numpy
    import soundfile as sf
    from PIL import Image, ImageDraw
    from color_schemes import COLOR_SCHEMES, DEFAULT_COLOR_SCHEME_KEY

except Exception as e:
    print("processing.py import error:", e)
    import traceback
    traceback.print_exc()
    with open("processing_import_error.txt", "w") as f:
        traceback.print_exc(file=f)
    import sys
    sys.exit(1)


class AudioProcessingException(Exception):
    pass

def get_max_level(filename):
    max_value = 0
    buffer_size = 4096

    with sf.SoundFile(filename, 'r') as audio_file:
        n_samples_left = len(audio_file)

        while n_samples_left > 0:
            to_read = min(buffer_size, n_samples_left)
            samples = audio_file.read(to_read, dtype='float32')

            if audio_file.channels > 1:
                samples = samples[:, 0]

            max_value = max(max_value, numpy.abs(samples).max())
            n_samples_left -= to_read

    return max_value

class AudioProcessor:
    """
    The audio processor processes chunks of audio an calculates the spectrac centroid and the peak
    samples in that chunk of audio.
    """

    def __init__(self, input_filename, fft_size, window_function=numpy.hanning):
        max_level = get_max_level(input_filename)
        self.audio_file = sf.SoundFile(input_filename, 'r')
        self.nframes = len(self.audio_file)
        self.samplerate = self.audio_file.samplerate
        self.fft_size = fft_size
        self.window = window_function(self.fft_size)
        self.spectrum_range = None
        self.lower = 100
        self.higher = 22050
        self.lower_log = math.log10(self.lower)
        self.higher_log = math.log10(self.higher)
        self.clip = lambda val, low, high: min(high, max(low, val))

        # figure out what the maximum value is for an FFT doing the FFT of a DC signal
        fft = numpy.fft.rfft(numpy.ones(fft_size) * self.window)
        max_fft = (numpy.abs(fft)).max()
        # set the scale to normalized audio and normalized FFT
        self.scale = (1.0 / max_level) / max_fft if max_level > 0 else 1

    def read(self, start, size, resize_if_less=False):
        """ read size samples starting at start, if resize_if_less is True and less than size
        samples are read, resize the array to size and fill with zeros """

        # number of zeros to add to start and end of the buffer
        add_to_start = 0
        add_to_end = 0

        if start < 0:
            # the first FFT window starts centered around zero
            if size + start <= 0:
                return numpy.zeros(size) if resize_if_less else numpy.array([])
            else:
                self.audio_file.seek(0)

                add_to_start = -start  # remember: start is negative!
                to_read = size + start

                if to_read > self.nframes:
                    add_to_end = to_read - self.nframes
                    to_read = self.nframes
        else:
            self.audio_file.seek(start)

            to_read = size
            if start + to_read >= self.nframes:
                to_read = self.nframes - start
                add_to_end = size - to_read

        try:
            samples = self.audio_file.read(to_read, dtype='float32')
        except RuntimeError:
            # this can happen for wave files with broken headers...
            return numpy.zeros(size) if resize_if_less else numpy.zeros(2)

        # convert to mono by selecting left channel only
        if self.audio_file.channels > 1:
            samples = samples[:, 0]

        if resize_if_less and (add_to_start > 0 or add_to_end > 0):
            if add_to_start > 0:
                samples = numpy.concatenate((numpy.zeros(add_to_start), samples), axis=0)

            if add_to_end > 0:
                samples = numpy.resize(samples, size)
                samples[size - add_to_end:] = 0

        return samples

    def spectral_centroid(self, seek_point, spec_range=110.0):
        """ starting at seek_point read fft_size samples, and calculate the spectral centroid """

        samples = self.read(seek_point - self.fft_size // 2, self.fft_size, True)

        samples *= self.window
        fft = numpy.fft.rfft(samples)
        spectrum = self.scale * numpy.abs(fft)  # normalized abs(FFT) between 0 and 1
        length = numpy.float64(spectrum.shape[0])

        # scale the db spectrum from [- spec_range db ... 0 db] > [0..1]
        db_spectrum = ((20 * (numpy.log10(spectrum + 1e-60))).clip(-spec_range, 0.0) + spec_range)
        db_spectrum = db_spectrum / spec_range

        energy = spectrum.sum()
        spectral_centroid = 0

        if energy > 1e-60:
            # calculate the spectral centroid

            if self.spectrum_range is None:
                self.spectrum_range = numpy.arange(length)

            spectral_centroid = ((spectrum * self.spectrum_range).sum() / (
                        energy * (length - 1))) * self.samplerate * 0.5

            # clip > log10 > scale between 0 and 1
            spectral_centroid = (math.log10(self.clip(spectral_centroid, self.lower, self.higher)) - self.lower_log) / (
                        self.higher_log - self.lower_log)

        return spectral_centroid, db_spectrum

    def peaks(self, start_seek, end_seek):
        """ read all samples between start_seek and end_seek, then find the minimum and maximum peak
        in that range. Returns that pair in the order they were found. So if min was found first,
        it returns (min, max) else the other way around. """

        # larger blocksizes are faster but take more mem...
        # Aha, Watson, a clue, a tradeoff!
        block_size = 4096

        max_index = -1
        max_value = -1
        min_index = -1
        min_value = 1

        if start_seek < 0:
            start_seek = 0

        if end_seek > self.nframes:
            end_seek = self.nframes

        if end_seek <= start_seek:
            samples = self.read(start_seek, 1)
            return samples[0], samples[0]

        if block_size > end_seek - start_seek:
            block_size = end_seek - start_seek

        for i in range(start_seek, end_seek, block_size):
            samples = self.read(i, block_size)

            local_max_index = numpy.argmax(samples)
            local_max_value = samples[local_max_index]

            if local_max_value > max_value:
                max_value = local_max_value
                max_index = local_max_index

            local_min_index = numpy.argmin(samples)
            local_min_value = samples[local_min_index]

            if local_min_value < min_value:
                min_value = local_min_value
                min_index = local_min_index

        return (min_value, max_value) if min_index < max_index else (max_value, min_value)


def interpolate_colors(colors, flat=False, num_colors=256):
    """ given a list of colors, create a larger list of colors interpolating
    the first one. If flatten is True, a list of numbers will be returned. If
    False, a list of (r,g,b) tuples. num_colors is the number of colors wanted
    in the final list """

    palette = []

    for i in range(num_colors):
        index = (i * (len(colors) - 1)) / (num_colors - 1.0)
        index_int = int(index)
        alpha = index - float(index_int)

        if alpha > 0:
            r = (1.0 - alpha) * colors[index_int][0] + alpha * colors[index_int + 1][0]
            g = (1.0 - alpha) * colors[index_int][1] + alpha * colors[index_int + 1][1]
            b = (1.0 - alpha) * colors[index_int][2] + alpha * colors[index_int + 1][2]
        else:
            r = (1.0 - alpha) * colors[index_int][0]
            g = (1.0 - alpha) * colors[index_int][1]
            b = (1.0 - alpha) * colors[index_int][2]

        if flat:
            palette.extend((int(r), int(g), int(b)))
        else:
            palette.append((int(r), int(g), int(b)))

    return palette


class WaveformImage:
    """
    Given peaks and spectral centroids from the AudioProcessor, this class will construct
    a wavefile image which can be saved as PNG.
    """

    def __init__(self, image_width, image_height, color_scheme):
        if image_height % 2 == 0:
            print("WARNING: Height is not uneven, images look much better at uneven height")

        if isinstance(color_scheme, dict):
            self.color_scheme_to_use = color_scheme
        else:
            self.color_scheme_to_use = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES[DEFAULT_COLOR_SCHEME_KEY])
        
        self.transparent_background = self.color_scheme_to_use.get('wave_transparent_background', False)
        if self.transparent_background:
            self.image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
        else:
            background_color = self.color_scheme_to_use['wave_colors'][0]  # Only used if transparent_background is False
            self.image = Image.new("RGB", (image_width, image_height),  background_color)

        self.image_width = image_width
        self.image_height = image_height

        self.draw = ImageDraw.Draw(self.image)
        self.previous_x, self.previous_y = None, None

        colors = self.color_scheme_to_use['wave_colors'][1:]
        self.color_lookup = interpolate_colors(colors)
        self.pix = self.image.load()

    def draw_peaks(self, x, peaks, spectral_centroid):
        """ draw 2 peaks at x using the spectral_centroid for color """

        y1 = self.image_height * 0.5 - peaks[0] * (self.image_height - 4) * 0.5
        y2 = self.image_height * 0.5 - peaks[1] * (self.image_height - 4) * 0.5

        line_color = self.color_lookup[int(spectral_centroid * 255.0)]

        if self.previous_y is not None:
            self.draw.line([self.previous_x, self.previous_y, x, y1, x, y2], line_color)
        else:
            self.draw.line([x, y1, x, y2], line_color)

        self.previous_x, self.previous_y = x, y2

        self.draw_anti_aliased_pixels(x, y1, y2, line_color)

    def draw_anti_aliased_pixels(self, x, y1, y2, color):
        """ vertical anti-aliasing at y1 and y2 """
        
        y_max = max(y1, y2)
        y_max_int = int(y_max)
        alpha = y_max - y_max_int

        if 0.0 < alpha < 1.0 and y_max_int + 1 < self.image_height:
            if not self.transparent_background:
                current_pix = self.pix[x, y_max_int + 1]
                r = int((1 - alpha) * current_pix[0] + alpha * color[0])
                g = int((1 - alpha) * current_pix[1] + alpha * color[1])
                b = int((1 - alpha) * current_pix[2] + alpha * color[2])
                self.pix[x, y_max_int + 1] = (r, g, b)
            else:
                # If using transparent background, don't do anti-aliasing
                self.pix[x, y_max_int + 1] = (color[0], color[1], color[2], 255)
                

        y_min = min(y1, y2)
        y_min_int = int(y_min)
        alpha = 1.0 - (y_min - y_min_int)

        if 0.0 < alpha < 1.0 and y_min_int - 1 >= 0:
            if not self.transparent_background:
                current_pix = self.pix[x, y_max_int + 1]
                r = int((1 - alpha) * current_pix[0] + alpha * color[0])
                g = int((1 - alpha) * current_pix[1] + alpha * color[1])
                b = int((1 - alpha) * current_pix[2] + alpha * color[2])
                self.pix[x, y_min_int - 1] = (r, g, b)
            else:
                # If using transparent background, don't do anti-aliasing
                self.pix[x, y_max_int + 1] = (color[0], color[1], color[2], 255)

    def save(self, filename):
        # draw a zero "zero" line
        a = self.color_scheme_to_use.get('wave_zero_line_alpha', 0)
        if a:
            for x in range(self.image_width):
                center = self.image_height // 2
                self.pix[x, center] = tuple([p + a for p in self.pix[x, center]])

        self.image.save(filename)


class SpectrogramImage:
    """
    Given spectra from the AudioProcessor, this class will construct a wavefile image which
    can be saved as PNG.
    """

    def __init__(self, image_width, image_height, fft_size, color_scheme):
        self.image_width = image_width
        self.image_height = image_height
        self.fft_size = fft_size

        self.image = Image.new("RGB", (image_height, image_width))
        if isinstance(color_scheme, dict):
            spectrogram_colors = color_scheme['spec_colors']
        else:
            spectrogram_colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES[DEFAULT_COLOR_SCHEME_KEY])['spec_colors']
        self.palette = interpolate_colors(spectrogram_colors)

        # generate the lookup which translates y-coordinate to fft-bin
        self.y_to_bin = []
        f_min = 100.0
        f_max = 22050.0
        y_min = math.log10(f_min)
        y_max = math.log10(f_max)
        for y in range(self.image_height):
            freq = math.pow(10.0, y_min + y / (image_height - 1.0) * (y_max - y_min))
            bin = freq / 22050.0 * (self.fft_size // 2 + 1)

            if bin < self.fft_size // 2:
                alpha = bin - int(bin)

                self.y_to_bin.append((int(bin), alpha * 255))

        # this is a bit strange, but using image.load()[x,y] = ... is
        # a lot slower than using image.putadata and then rotating the image
        # so we store all the pixels in an array and then create the image when saving
        self.pixels = []

    def draw_spectrum(self, x, spectrum):
        # for all frequencies, draw the pixels
        for (index, alpha) in self.y_to_bin:
            self.pixels.append(self.palette[int((255.0 - alpha) * spectrum[index] + alpha * spectrum[index + 1])])

        # if the FFT is too small to fill up the image, fill with black to the top
        for y in range(len(self.y_to_bin), self.image_height):
            self.pixels.append(self.palette[0])

    def save(self, filename, quality=80):
        self.image.putdata(self.pixels)
        self.image.transpose(Image.ROTATE_90).save(filename, quality=quality)


def create_wave_images(input_filename, output_filename_w, output_filename_s, image_width, image_height, fft_size,
                       progress_callback=None, color_scheme=None, use_transparent_background=False):
    """
    Utility function for creating both wavefile and spectrum images from an audio input file.
    :param input_filename: input audio filename (must be PCM)
    :param output_filename_w: output filename for waveform image (must end in .png)
    :param output_filename_s: output filename for spectrogram image (must end in .jpg)
    :param image_width: width of both spectrogram and waveform images
    :param image_height: height of both spectrogram and waveform images
    :param fft_size: size of the FFT computed for the spectrogram image
    :param progress_callback: function to iteratively call while images are being created. Will be called every 1%,
                                with parameters (current_position, width)
    :param color_scheme: color scheme to use for the generated images (defaults to Freesound2 color scheme)
    """
    processor = AudioProcessor(input_filename, fft_size, numpy.hanning)
    samples_per_pixel = processor.nframes / float(image_width)

    waveform = WaveformImage(image_width, image_height, color_scheme)
    spectrogram = SpectrogramImage(image_width, image_height, fft_size, color_scheme)

    for x in range(image_width):

        if progress_callback and x % (image_width // 100) == 0:
            progress_callback(x, image_width)

        seek_point = int(x * samples_per_pixel)
        next_seek_point = int((x + 1) * samples_per_pixel)

        (spectral_centroid, db_spectrum) = processor.spectral_centroid(seek_point)
        peaks = processor.peaks(seek_point, next_seek_point)

        waveform.draw_peaks(x, peaks, spectral_centroid)
        spectrogram.draw_spectrum(x, db_spectrum)

    if progress_callback:
        progress_callback(image_width, image_width)

    waveform.save(output_filename_w)
    spectrogram.save(output_filename_s)


class NoSpaceLeftException(Exception):
    pass
