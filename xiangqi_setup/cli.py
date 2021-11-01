# Copyright (C) 2014 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GNU Affero General Public License version 3.0 or later

from __future__ import print_function

import argparse
import os
import sys

from .wxf_format import iterate_wxf_tokens
from .compose import compose_svg, cm_to_pixel


_DEFAULT_WIDTH_CM = 7.0

_PIECE_SCALE_MIN = 0.0
_PIECE_SCALE_MAX = 1.2


def check(options):
    if _PIECE_SCALE_MIN < options.piece_scale <= _PIECE_SCALE_MAX:
        pass
    else:
        print('ERROR: Piece scale must be larger than %.1f and greater or equal %.1f .' \
                % (_PIECE_SCALE_MIN, _PIECE_SCALE_MAX), file=sys.stderr)
        sys.exit(1)

    if options.width_centimeter is not None:
        options.width_pixel = cm_to_pixel(options.width_centimeter, options.resolution_dpi)
    delattr(options, 'width_centimeter')
    if options.width_pixel is None:
        options.width_pixel = cm_to_pixel(_DEFAULT_WIDTH_CM, options.resolution_dpi)


def run(options):
    pieces_to_put = list(iterate_wxf_tokens(options.input_file))
    compose_svg(pieces_to_put, options)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--board', dest='board_theme_dir', metavar='DIRECTORY', default=os.path.join('themes', 'board', 'clean_alpha'))
    parser.add_argument('--pieces', dest='pieces_theme_dir', metavar='DIRECTORY', default=os.path.join('themes', 'pieces', 'retro_simple'))
    parser.add_argument('--width-px', dest='width_pixel', metavar='PIXEL', type=float)
    parser.add_argument('--width-cm', dest='width_centimeter', metavar='CENTIMETER', type=float)
    parser.add_argument('--dpi', dest='resolution_dpi', metavar='FLOAT', type=float, default=90.0)
    parser.add_argument('--scale-pieces', dest='piece_scale', metavar='FACTOR', type=float, default=0.9)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('input_file', metavar='INPUT_FILE')
    parser.add_argument('output_file', metavar='OUTPUT_FILE')
    options = parser.parse_args()
    check(options)
    run(options)
