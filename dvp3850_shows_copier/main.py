#!/bin/env python3

import argparse
import os
import random
import shutil
import sys
from itertools import zip_longest, cycle
from pathlib import Path
from typing import Optional

from pymediainfo import MediaInfo

from .cache import Cache
from .config import get_config


def determine_compatibility(video_file: Path,
                            verbose: bool = True):
    """Determines if the video at the provided path is compatible
    with the Philips DVP3850 player.

    Args:
        video_file: Video file to check.
    
    Returns:
        `True` if compatible, `False` otherwise.
    """

    media_info = MediaInfo.parse(video_file)
    
    video_compatible = False
    audio_compatible = False
    for info_track in media_info.tracks:
        try:
            if info_track.track_type == 'Video' and not video_compatible:
                if (
                    ((info_track.codec_id or '').lower() in ['xvid', 'divx'] or
                    (info_track.codec_id_hint or '').lower() in ['xvid', 'divx']) and
                    (1.3 <= float(info_track.display_aspect_ratio) < 1.34)):
                        video_compatible = True
            elif info_track.track_type == 'Audio' and not audio_compatible:
                if ((info_track.codec_id or '').lower()  in ['a_ac3', 'mp3'] or
                    (info_track.codec_id_hint or '').lower() in ['a_ac3', 'mp3']):
                        audio_compatible = True
        except AttributeError:
            continue

    return video_compatible and audio_compatible


def run_copier(shows, base_path, target_path, count, cache, random_=True,
               uniformous=None, verbose=True):

    # TODO: Implement other features.
    # For now, whatever options you pass in, it will always do the following:
    #   - Randomize.
    #   - Pick equal amounts from every series.

    def _build_show_iter(show):
        show_path = base_path / show
        if '/Season ' in show and int(show[-1]) in range(10):
            show_list = list(show_path.rglob('*'))
        else:
            show_list = list(show_path.rglob('*Season */*'))

        random.shuffle(show_list)
        return show_list

    copied = 0
    shows_iter = cycle(
        zip_longest(*(_build_show_iter(show) for show in shows),
                    fillvalue=None))

    for round_ in shows_iter:
        for video_file in round_:
            if not video_file or video_file.is_dir():
                continue

            if verbose:
                print(f'{video_file.relative_to(base_path)}... ', end='')


            try:
                # TODO: Implement `in` contains check.
                is_compatible = cache[video_file]
                from_cache = True
            except Exception:
                is_compatible = determine_compatibility(video_file, cache)
                from_cache = False
            finally:
                if verbose:
                    print(('yes' if is_compatible else 'no') +
                          (' (from cache)' if from_cache else ''), end='')

            # TODO: This is a horrible way to manage `Extras` folders and such
            # within the `Season *` dirs. Improve it.
            try:
                cache[video_file] = is_compatible
            except ValueError:
                print(f'skipped: {video_file}')
                continue

            cache.write()

            if is_compatible:
                target = target_path / video_file.relative_to(base_path).parent.parent
                os.makedirs(target, exist_ok=True)
                shutil.copy(video_file, target, follow_symlinks=True)
                copied += 1

                if verbose:
                    print(f'; copied to {target}', end='')
            print()

            if copied >= count:
                if verbose:
                    print()
                    print('done.')
                return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='dvp3850-shows-copier')

    # TODO: Use type `ShowEnum`.
    parser.add_argument('show',
                        nargs='+',
                        type=str,
                        help='shows to include in copy task. optionally, you '
                             'can restrict to a given season, using the '
                             'notation `Friends/Season 01`',
                        metavar='SHOW')
    parser.add_argument('-N', '--count',
                        type=int,
                        required=True,
                        help='amount of episodes to copy')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        default=True,
                        help='use verbose output')
    parser.add_argument('-r', '--random',
                        action='store_true',
                        help='make random selection of episodes')
    parser.add_argument('-u', '--uniformous',
                        action='store_true',
                        help='pick equally many episodes from each show')
    args = parser.parse_args()

    config = get_config()
    base_path = config['general'].getpath('base path')
    target_path = config['general'].getpath('target base path')
    cache = Cache(config['general'].getpath('cache file'), base_path)

    run_copier(args.show, base_path, target_path, args.count, cache,
               random_=args.random, uniformous=args.uniformous,
               verbose=args.verbose)

