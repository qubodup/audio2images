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

from functools import partial

from PIL import ImageColor

def desaturate(rgb, amount):
    """
        desaturate colors by amount
        amount == 0, no change
        amount == 1, grey
    """
    luminosity = sum(rgb) / 3.0
    desat = lambda color: color - amount * (color - luminosity)

    return tuple(map(int, list(map(desat, rgb))))


def color_from_value(value):
    """ given a value between 0 and 1, return an (r,g,b) tuple """
    return ImageColor.getrgb("hsl(%d,%d%%,%d%%)" % (int((1.0 - value) * 360), 80, 50))

FREESOUND2_COLOR_SCHEME = 'Freesound2'
BEASTWHOOSH_COLOR_SCHEME = 'FreesoundBeastWhoosh'
BEASTLOL_COLOR_SCHEME = 'BeastLol'
OLD_BEASTWHOOSH_COLOR_SCHEME = 'FreesoundBeastWhooshOld'
CYBERPUNK_COLOR_SCHEME = 'Cyberpunk'
RAINFOREST_COLOR_SCHEME = 'Rainforest'
CRAZYCOLORS = 'CrazyColors'
CRAZYCRAYONS_COLOR_SCHEME = 'CrazyCrayons'
CREEPYCRAYONS_COLOR_SCHEME = 'CreepyCrayons'
BLEEPBLOOP_COLOR_SCHEME = 'BleepBloop'
DEFAULT_COLOR_SCHEME_KEY = BLEEPBLOOP_COLOR_SCHEME

COLOR_SCHEMES = {

    BLEEPBLOOP_COLOR_SCHEME: {
        'wave_colors': [
        (20, 20, 36),
        (0, 145, 255),
        (10, 255, 129),
        (212, 255, 0),
        (255, 0, 90)
        ],
        'spec_colors': [
        (20, 20, 16),
        (0, 28, 25),
        (0, 37, 66),
        (0, 77, 153),
        (19, 201, 192),
        (0, 200, 100),
        (255, 204, 0),
        (255, 136, 0),
        (255, 0, 90),
        (255, 17, 0)
        ],
        'wave_transparent_background': True,
        'wave_zero_line_alpha': 12,
    },
    CREEPYCRAYONS_COLOR_SCHEME: {
        'wave_colors': [
        (0, 220, 80),
        (100, 150, 200),
        (200, 100, 50),
        (255, 0, 100),
        (0, 100, 200)
        ],
        'spec_colors': [
        (255, 0, 0),
        (255, 128, 0),
        (255, 255, 0),
        (128, 255, 0),
        (0, 255, 128),
        (0, 255, 255),
        (0, 128, 255),
        (0, 0, 255),
        (128, 0, 255),
        (255, 0, 255)
        ],
        'wave_transparent_background': True,
        'wave_zero_line_alpha': 12,
    },
    CRAZYCRAYONS_COLOR_SCHEME: {
        'wave_colors': [
        (0, 220, 80),
        (100, 150, 200),
        (0, 0, 0),
        (200, 100, 50),
        (255, 204, 204),
        (255, 0, 100),
        (228, 254, 32),
        (0, 0, 0),
        (0, 100, 200)
        ],
        'spec_colors': [
        (255, 0, 0),
        (255, 128, 0),
        (0, 0, 0),
        (6, 254, 147),
        (128, 255, 0),
        (0, 255, 128),
        (0, 0, 0),
        (0, 255, 255),
        (0, 128, 255),
        (0, 8, 117),
        (0, 0, 0),
        (128, 0, 255),
        (255, 0, 255)
        ],
        'wave_transparent_background': True,
        'wave_zero_line_alpha': 15,
    },
    CRAZYCOLORS: {
        'wave_colors': [
        (20, 20, 36),
        (28, 36, 20),
        (28, 236, 20),
        (28, 36, 220),
        (220, 24, 4)
        ],
        'spec_colors': [
        (18, 18, 202),
        (111, 111, 11),
        (111, 5, 11),
        (211, 111, 221),
        (212, 255, 0)
        ],
        'wave_transparent_background': True,
        'wave_zero_line_alpha': 25,
    },
    FREESOUND2_COLOR_SCHEME: {
        'wave_colors': [
            (0, 0, 0),    # Background color
            (50, 0, 200),    # Low spectral centroid
            (0, 220, 80),
            (255, 224, 0),
            (255, 70, 0),    # High spectral centroid
        ],
        'spec_colors': [
            (0, 0, 0),    # Background color
            (58 // 4, 68 // 4, 65 // 4),
            (80 // 2, 100 // 2, 153 // 2),
            (90, 180, 100),
            (224, 224, 44),
            (255, 60, 30),
            (255, 255, 255)
        ],
        'wave_zero_line_alpha': 25,
    },
    OLD_BEASTWHOOSH_COLOR_SCHEME: {
        'wave_colors': [
            (255, 255, 255),    # Background color
            (29, 159, 181),    # 1D9FB5, Low spectral centroid
            (28, 174, 72),    # 1CAE48
            (255, 158, 53),    # FF9E35
            (255, 53, 70),    # FF3546, High spectral centroid
        ],
        'spec_colors': [
            (0, 0, 0),    # Background color/Low spectral energy
            (29, 159, 181),    # 1D9FB5
            (28, 174, 72),    # 1CAE48
            (255, 158, 53),    # FF9E35
            (255, 53, 70),    # FF3546, High spectral energy
        ]
    },
    BEASTWHOOSH_COLOR_SCHEME: {
        'wave_colors': [
            (20, 20, 36),    # Background color (not really used as we use transparent mode)
            (29, 159, 181),    # Low spectral centroid
            (0, 220, 80),
            (255, 200, 58),
            (255, 0, 70),    # High spectral centroid
        ],
        'spec_colors': [
            (20, 20, 36),    # Low spectral energy
            (0, 18, 25),
            (0, 37, 56),
            (11, 95, 118),
            (29, 159, 181),
            (0, 220, 80),
            (255, 200, 58),
            (255, 125, 0),
            (255, 0, 70),
            (255, 0, 20),    # High spectral energy
        ],
        'wave_transparent_background': True,
        'wave_zero_line_alpha': 12,
    },
    BEASTLOL_COLOR_SCHEME: {
        'wave_colors': [
            (20, 20, 36),    # Background color (not really used as we use transparent mode)
            (29, 159, 201),    # Low spectral centroid
            (20, 240, 80),
            (255, 200, 78),
            (255, 0, 90),    # High spectral centroid
        ],
        'spec_colors': [
            (20, 20, 16),    # Low spectral energy
            (0, 28, 25),
            (0, 37, 66),
            (31, 75, 118),
            (39, 189, 181),
            (0, 200, 100),
            (255, 220, 78),
            (255, 145, 20),
            (255, 0, 90),
            (235, 0, 20),    # High spectral energy
        ],
        'wave_transparent_background': True,
        'wave_zero_line_alpha': 12,
    },
    CYBERPUNK_COLOR_SCHEME: {
        'wave_colors': [(0, 0, 0)] + [color_from_value(value / 29.0) for value in range(0, 30)],
        'spec_colors': [(0, 0, 0)] + [color_from_value(value / 29.0) for value in range(0, 30)],
    },
    RAINFOREST_COLOR_SCHEME: {
        'wave_colors': [(213, 217, 221)] +
                       list(map(partial(desaturate, amount=0.7), [
                           (50, 0, 200),
                           (0, 220, 80),
                           (255, 224, 0),
                       ])),
        'spec_colors': [(213, 217, 221)] +
                       list(map(partial(desaturate, amount=0.7), [
                           (50, 0, 200),
                           (0, 220, 80),
                           (255, 224, 0),
                       ])),
    }
}
