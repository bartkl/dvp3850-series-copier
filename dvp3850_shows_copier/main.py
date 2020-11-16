#!/bin/env python3

import sys
from pathlib import Path

from pymediainfo import MediaInfo

from .cache import Cache
from .config import get_config


Config = get_config()


def determine_compatibility(video_file: Path) -> bool:
    """Determines if the video at the provided path is compatible
    with the Philips DVP3850 player.

    If the video file is present in the cache, its compatibility
    will be read from there. Otherwise, it will be determined and
    then written to the cache.

    Args:
        video_file: Video file to check.
    
    Returns:
        `True` if compatible, `False` otherwise.
    """

    cache = Cache(Config['general']['cache file'], Config['library']['base path'])

    try:
        return cache[video_file.parent][video_file.name]
    except KeyError:
        pass

    cache.setdefault(str(video_file.parent), {})[str(video_file.name)] = True
    # print(cache)
    cache.write()
    exit()

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


def check_all(cache: bool = True, verbose: bool = True):
    if cache:
        cache_file = open(CACHE_FILE, 'w')

    for i, video_file in enumerate(sorted(FILES)):
        if video_file.is_dir():
            continue
        
        if verbose:
            print(f'{video_file}... ', end='')

        is_compatible = determine_compatibility(video_file)
        if is_compatible:
            print('yes')
            cache_file.write(f'{video_file}\tyes\n')
        else:
            print('no')
            cache_file.write(f'{video_file}\tno\n')

        if i == 5:
            break

    cache_file.close()


if __name__ == '__main__':
    shows = map(Path, sys.argv[1:])

    copied = 0
    for video_file in shows:
        if video_file.is_dir():
            continue
        print(f'{video_file}...', end='')
        is_compatible = determine_compatibility(video_file)
        print(is_compatible)
