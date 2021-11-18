# Copyright (C) 2014 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GNU Affero General Public License version 3.0 or later

from __future__ import print_function

import argparse
import glob
import inspect
import os
import sys

from .wxf_format import iterate_wxf_tokens
from .compose import compose_svg, cm_to_pixel


_DEFAULT_WIDTH_CM = 7.0

_PIECE_SCALE_MIN = 0.0
_PIECE_SCALE_MAX = 1.2


def _get_self_dir():
    return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def _get_themes_home_dir():
    self_dir = _get_self_dir()
    if os.path.exists(os.path.join(self_dir, '..', '.git')):
        return os.path.join(self_dir, '..', 'themes')
    else:
        return os.path.join('/usr/share/xiangqi-setup/themes')


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


def _theme_name(text):
    if '/' in text:
        raise ValueError('Theme name cannot contain slashes')
    return text

_theme_name.__name__ = 'theme name'  # used by arparse error message


def main():
    themes_home_dir = _get_themes_home_dir()
    board_themes_home_dir = os.path.join(themes_home_dir, 'board')
    pieces_themes_home_dir = os.path.join(themes_home_dir, 'pieces')

    board_theme_choices = []
    pieces_theme_choices = []
    for directory, target_list in (
            (board_themes_home_dir, board_theme_choices),
            (pieces_themes_home_dir, pieces_theme_choices),
            ):
        target_list += [os.path.basename(e) for e in glob.glob(os.path.join(directory, '*'))]

    epilog_chunks = []
    for category, source_list, blank_line_after in (
            ('available board themes', board_theme_choices, True),
            ('available pieces themes', pieces_theme_choices, False),
            ):
        epilog_chunks.append('%s:' % category)
        for name in sorted(source_list, key=lambda x: x.lower()):
            epilog_chunks.append('  %s' % name)
        if blank_line_after:
            epilog_chunks.append('')

    parser = argparse.ArgumentParser(
            epilog='\n'.join(epilog_chunks),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            )
    parser.add_argument('--board', dest='board_theme_dir', metavar='THEME', type=_theme_name, default='clean_alpha')
    parser.add_argument('--pieces', dest='pieces_theme_dir', metavar='THEME', type=_theme_name, default='retro_simple')
    parser.add_argument('--width-px', dest='width_pixel', metavar='PIXEL', type=float)
    parser.add_argument('--width-cm', dest='width_centimeter', metavar='CENTIMETER', type=float)
    parser.add_argument('--dpi', dest='resolution_dpi', metavar='FLOAT', type=float, default=90.0)
    parser.add_argument('--scale-pieces', dest='piece_scale', metavar='FACTOR', type=float, default=0.9)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('input_file', metavar='INPUT_FILE')
    parser.add_argument('output_file', metavar='OUTPUT_FILE')
    options = parser.parse_args()

    # Turn theme names into paths
    options.board_theme_dir = os.path.join(board_themes_home_dir, options.board_theme_dir)
    options.pieces_theme_dir = os.path.join(pieces_themes_home_dir, options.pieces_theme_dir)

    check(options)
    run(options)
