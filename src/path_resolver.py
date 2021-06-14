"""This script resolves paths of media present in Tweets.

Each media will have a path object containing both the local and the remote paths.
Format:
{
    'type': str('Media type, either video or image.'),
    'path': str('Local path to the media.'),
    'url': str('Remote URL of this media.'),
    'thumbnail': str('Local path to the video thumbnail. For video files only.')
}

For the user info file, this script overwrites the 'profile_image_url' and the
'profile_banner_url' with a path object.
Change Example:
    'profile_image_url': str('URL of the avatar.') -> obj('Path object of the avatar')

For the Tweets file, this script adds a list of path objects under a new attribute
named 'media'.
Change Example:
    'media': [
        obj('Path object of a media file.')
    ]

The default
- Raw Tweets file locates at '../data/texts/tweets_raw.json'.
- Raw user file locates at '../data/texts/user_raw.json'.
- Reference/URLs file locates at '../data/texts/urls.json'.
- Media config file locates at 'configs/media.json'.
- Input media data directory locates at '../data/media'.
- Output texts directory locates at '../data/texts'. (To save path resolved 
  user info and Tweets.)

For the final HTML file, the default media data directory is 'data/media'.
Note that this path may be different to the input media data directory above.
The final HTML file by default locates at the project root directory.

Example usage:
    python path_resolver.py \
        -i "path/to/the/raw/tweets/file" \
        -u "path/to/the/raw/user/file" \
        -r "path/to/the/reference/urls/file" \
        -s "path/to/the/media/config/file" \
        -m "path/to/the/input/media/directory" \
        -o "path/to/the/output/texts/directory" \
        -x "path/to/the/media/directory/relative/to/the/html/file"
"""

from __future__ import annotations
import argparse
from datetime import datetime
import os
from PIL import Image
import shutil

from utils import color, html, io, shell, video # pylint: disable=import-error


# Output files
TWEETS_OUTPUT_FILENAME = 'tweets.json'
USER_OUTPUT_FILENAME = 'user.json'


def get_tweets_media_paths(
        src: str, dst: str, url: str, video_settings: dict,
        image_settings: dict, keep_thumbnails: bool) -> list:
    """Resolves paths to Tweets media.

    Omits images whose dimensions are smaller than the ones in the settings.
    Finds paths to thumbails for video files as well. Media are sorted by their
    modification time.

    Parameters
    ----------
    src: str
        Parent directory of the media.
    dst: str
        Destination directory of media relative in the final HTML.
    url: str
        Remote URL of the media.
    video_settings: dict
        Includes thumbnail settings and acceptable video extensions.
        Format:
        {
            'thumbnail': {
                'cutoff': float('Cutoff ratio of video files to extract thumbnails. e.g. 0.1 means getting thumbnails at the 10% position of videos.'),
                'suffix': str('Common thumbnail suffix. e.g. _thumb'),
                'extensions': str('Common thumbnail extension. e.g. .png')
            },
            'extensions': [
                str('An acceptable video extension. e.g. .mp4')
            ]
        }
    image_settings: dict
        Includes acceptable image dimensions and acceptable image extensions.
        Format:
        {
            'min_width': int('Minimal acceptable image width.'),
            'min_height': int('Minimal acceptable image height.'),
            'extensions': [
                str('An acceptable image extension. e.g. .png')
            ]
        }
    keep_thumbnails: bool
        Whether or not to keep existing thumbnails.

    Returns
    -------
    list
        Media paths used in the final HTML. Media are sorted by their 
        modification time since the order may affect reading. e.g. Manga series. 
        Format:
        [
            {
                'type': str('Media type, either video or image.'),
                'path': str('Local path to the media.'),
                'url': str('Remote URL of the media'),
                'thumbnail': str('Local path to the video thumbnail. For video files only.')
            }
        ]
    """
    video_extensions = set(video_settings['extensions'])
    image_extensions = set(image_settings['extensions'])

    videos = []
    images = []
    for file in os.listdir(src):
        extension = io.get_extension(file)
        path = io.join_paths(src, file)

        if extension in video_extensions:
            videos.append(path)
        elif (extension in image_extensions and 
                not io.has_suffix(file, video_settings['thumbnail']['suffix'])):
            width, height = Image.open(path).size
            if (width >= image_settings['min_width'] and 
                    height >= image_settings['min_height']):
                images.append(path)
        
    paths = get_video_paths(videos, video_settings['thumbnail'], keep_thumbnails)
    paths.update(get_image_paths(images))
    new_parent = os.path.join(dst, os.path.basename(src))
    return sort_media_paths(new_parent, url, paths)


def get_profile_image_path(
        src: str, dst: str, url: str, image_settings: dict) -> dict:
    """Resolve path to a profile image.

    A profile image may be an avatar or banner image.

    Parameters
    ----------
    src: str
        Parent directory of media.
    dst: str
        Destination directory of media relative in the final HTML.
    url: str
        Remote URL of the image.
    image_settings: dict
        Includes acceptable image dimensions and acceptable image extensions.
        Format:
        {
            'min_width': int('Minimal acceptable image width.'),
            'min_height': int('Minimal acceptable image height.'),
            'extensions': [
                str('An acceptable image extension. e.g. .png')
            ]
        }
    
    Returns
    -------
    dict
        Path to the latest profile image used in the final HTML.
        Format:
        {
            'type': 'image',
            'path': str('Local path to the profile image.'),
            'url': str('Remote URL of the media')
        }
    """
    image_extensions = set(image_settings['extensions'])
    images = []
    for file in os.listdir(src):
        extension = io.get_extension(file)
        path = io.join_paths(src, file)
        if extension in image_extensions:
            images.append(path)

    paths = get_image_paths(images)
    new_parent = os.path.join(dst, os.path.basename(src))
    return sort_media_paths(new_parent, url, paths)[-1]


def get_image_paths(images: list) -> dict:
    """Resolves paths to images.

    Parameters
    ----------
    images: list
        Local paths to image files.
    
    Returns
    -------
    dict
        Mapping from modification time to local filenames of images.
        Format:
        {
            'type': 'image',
            'path': str('Local video filename.')
        }
    """
    paths = {}
    for image_path in images:
        modification_time = os.path.getmtime(image_path)
        paths[modification_time] = {
            'type': 'image',
            'path': os.path.basename(image_path),
        }
    return paths


def get_video_paths(
        videos: list, thumbnail_settings: dict, keep_thumbnails: bool) -> dict:
    """Resolves paths to videos and their thumbnails.
    
    Converts MKVs to MP4s so the video file to ensure browser support. To make 
    thumbnails easily recognizable, all of them should have a common suffix. If 
    a thumbnail does not exist, FFmpeg will extract a frame from the video as a 
    thumbnail.

    Parameters
    ----------
    videos: list
        Local paths to video files.
    thumbnail_settings: dict
        Includes the thumbnail cutoff ratio in video files, thumbnail filename 
        suffix and export format.
        Format:
        {
            'cutoff': float('Cutoff ratio of video files to extract thumbnails. e.g. 0.1 means getting thumbnails at the 10% position of videos.'),
            'suffix': str('Common thumbnail suffix. e.g. _thumb'),
            'extension': str('Common thumbnail extension. e.g. .png')
        }
    keep_thumbnails: bool
        Whether or not to keep existing thumbnails.

    Returns
    -------
    dict
        Mapping from modification time to local filenames of video files and thumbnails.
        Format:
        {
            'type': 'video',
            'path': str('Local video filename.'),
            'thumbnail': str('Local thumbnail filename.')
        }
    """
    paths = {}
    for video_path in videos:
        # TODO: Checks for other video formats.
        if io.has_extension(video_path, '.mkv'):
            print(f"MKV detected. Converting '{video_path}' to MP4...")
            try:
                new_video_path = video.mkv_to_mp4(video_path)
                os.remove(video_path)
                print(
                    f"Saved converted MP4 to '{new_video_path}'. "
                    'Original MKV removed.')
                video_path = new_video_path
            except ChildProcessError as err:
                print(color.get_error(str(err)))
        
        thumbnail_path = io.add_suffix(
            io.replace_extension(video_path, thumbnail_settings['extension']),
            thumbnail_settings['suffix'])
        
        if keep_thumbnails and os.path.isfile(thumbnail_path):
            print(f"Uses existing thumbnail '{thumbnail_path}'.")
        else:
            print(f"Creating a thumbnail of '{video_path}'...")
            try:
                video.create_thumbnail(
                    video_path, thumbnail_path, thumbnail_settings['cutoff'])
                print(f"Saved the thumbnail to '{thumbnail_path}'.")
            except ChildProcessError as err:
                print(color.get_error(str(err)))
                continue
                
        modification_time = os.path.getmtime(video_path)
        paths[modification_time] = {
            'type': 'video',
            'path': os.path.basename(video_path),
            'thumbnail': os.path.basename(thumbnail_path),
        }
    return paths


def sort_media_paths(dst: str, url: str, paths: dict) -> list:
    """Sorts media paths by the modification time of each media file.
    
    Parameters
    ----------
    dst: str
        Parent directory of the media files.
    url: str
        Remote URLs of the media files.
    paths: dict
        Mapping from modification time to local filenames of media.
        Format:
        {
            'type': str('Media type, either video or image.'),
            'path': str('Local video filename.')
            'thumbnail': str('Local thumbnail filename. For video files only.')
        }
    
    Returns
    -------
    list
        Media paths sorted by the modification time of the media files. Each
        path starts with the parent directory.
        Format:
        [
            {
                'type': str('Media type, either video or image.'),
                'path': str('Local path to the media.'),
                'url': str('Remote URL of the media'),
                'thumbnail': str('Local path to the video thumbnail. For video files only.')
            }
        ]
    """
    paths_sorted = []
    for _, path in sorted(paths.items()):
        path_html = {
            'type': path['type'],
            'path': html.normalize_path(os.path.join(dst, path['path'])),
            'url': url,
        }
        if path['type'] == 'video':
            path_html['thumbnail'] = html.normalize_path(
                os.path.join(dst, path['thumbnail']))
        paths_sorted.append(path_html)
    return paths_sorted


def _get_options() -> dict:
    parser = argparse.ArgumentParser(
        description='Maps URLs in Tweets to local paths if possible.')
    parser.add_argument(
        '-i', '--input', default='../data/texts/tweets_raw.json', type=str, 
        help='Path to the raw Tweets file.')
    parser.add_argument(
        '-u', '--user', default='../data/texts/user_raw.json', type=str, 
        help='Path to the raw user info file.')
    parser.add_argument(
        '-r', '--references', default='../data/texts/urls.json', type=str, 
        help='Path to the path reference/URLs file.')
    parser.add_argument(
        '-s', '--settings', default='configs/media.json', type=str, 
        help='Path to the media config file.')
    parser.add_argument(
        '-m', '--media', default='../data/media', type=str, 
        help='Path to the media directory.')
    parser.add_argument(
        '-o', '--output', default='../data/texts', type=str, 
        help='Path to the texts output directory.')
    # Note: This path may be different from the media directory.
    parser.add_argument(
        '-x', '--export', default='data/media', type=str, 
        help='Path to the media directory relative to the final HTML file.'
             'The HTML file by default locates at the project root directory.')
    parser.add_argument(
        '--keep-thumbnails', action='store_true', default=False, 
        help='Keeps existing thumbnails.')
    return parser.parse_args()


if __name__ == '__main__':
    options = _get_options()
    io.make_directory(options.output)
    tweets = io.load_json(options.input)
    urls = io.load_json(options.references)
    user = io.load_json(options.user)
    settings = io.load_json(options.settings)
    video_settings = settings['video']
    image_settings = settings['image']

    # Stage 1: Resolves paths to the avatar and the profile banner images.
    print(color.get_info(
        f"Resolving paths to profile images of {user['username']}..."))
    profile_image_url = user['profile_image_url']
    local_directory = io.join_paths(options.media, urls[profile_image_url])
    user['profile_image_url'] = get_profile_image_path(
        local_directory, options.export, profile_image_url, image_settings)

    if 'profile_banner_url' in user:
        profile_banner_url = user['profile_banner_url']
        local_directory = io.join_paths(options.media, urls[profile_banner_url])
        user['profile_banner_url'] = get_profile_image_path(
            local_directory, options.export, profile_banner_url, image_settings)
    else:
        print(color.get_warning(f'WARNING: Profile banner URL not found.'))
    
    user_path = io.join_paths(options.output, USER_OUTPUT_FILENAME)
    if os.path.isfile(user_path):
        archive_path = io.archive_file(user_path)
        print(f"Archived '{user_path}' to '{archive_path}'.")
    io.dump_json(user, user_path)
    print(f"Saved path-resolved user info to '{user_path}'.")
    print()

    # Stage 2: Resolves paths to images and video files attached to Tweets.
    print(color.get_info(f'Media paths of {len(tweets)} Tweets to resolve.'))
    for i, (tid, tweet) in enumerate(tweets.items()):
        text = tweet['text']
        if 'urls' not in text:
            continue

        print(color.get_highlight(
            f'({i + 1}/{len(tweets)}) Resolving media paths of Tweet #{tid}...'))
        # Removes duplicated URLs within the same Tweet
        seen_urls = set()
        for url in text['urls']:
            expanded_url = url['expanded_url']
            if (expanded_url in urls) and (expanded_url not in seen_urls):
                local_directory = io.join_paths(
                    options.media, urls[expanded_url])
                
                if os.path.isdir(local_directory):
                    local_paths = get_tweets_media_paths(
                        local_directory, options.export, expanded_url,
                        video_settings, image_settings, options.keep_thumbnails)
                    if local_paths:
                        if 'media' not in tweet:
                            tweet['media'] = []
                        tweet['media'].extend(local_paths)
                seen_urls.add(expanded_url)

    tweets_path = io.join_paths(options.output, TWEETS_OUTPUT_FILENAME)
    if os.path.isfile(tweets_path):
        archive_path = io.archive_file(tweets_path)
        print(f"Archived '{tweets_path}' to '{archive_path}'.")
    io.dump_json(tweets, tweets_path)
    print(f"Saved {len(tweets)} path-resolved Tweets to '{tweets_path}'.")
    print()
    
    print(color.get_ok('Done.'))
