"""This script resolves paths of media present in Tweets.

Adds an additional 'media' attribute to Tweets with media URLs.
Format:
{
    'media': [
        {
            'local': [
                {
                    'type': str('Media type, either video or image.'),
                    'path': str('Local path to the media.'),
                    'thumbnail': str('Local path to the video. This attributes only exist if the media is a video.')
                }
            ],
            'remote': str('Remote URL of this media.')
        }
    ]
}

The default
- Raw Tweets file locates at '../data/texts/tweets_raw.json'.
- Reference/URLs file locates at '../data/texts/urls.json'.
- Media config file locates at 'configs/media.json'.
- Input media data directory locates at '../data/media'.
- Output texts directory locates at '../data/texts'. (To save path resolved Tweets.)

For the final HTML file, the default media data directory is 'data/media'.
Note that this path may be different to the input media data directory above.
The final HTML file by default locates at the project root directory.

Example usage:
    python path_resolver.py \
        -i "path/to/the/raw/tweets/file" \
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

from utils import color, html, io, string, video # pylint: disable=import-error


# Output files
TWEETS_OUTPUT_FILENAME = 'tweets.json'


def get_media_paths(
        src: str, dst: str, video_settings: dict, image_settings: dict) -> list:
    """Resolves paths to media.

    Omits images whose dimensions are smaller than the ones in the settings.
    Finds paths to thumbails for video files as well. Media are sorted by their
    modification time.

    Parameters
    ----------
    src: str
        Parent directory of media.
    dst: str
        Destination directory of media relative in the final HTML.
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
                'thumbnail': str('Local path to the video. This attributes only exist if the media is a video.')
            }
        ]
    """
    video_extensions = set(video_settings['extensions'])
    image_extensions = set(image_settings['extensions'])

    videos = {}
    images = {}
    for file in os.listdir(src):
        extension = io.get_extension(file)
        path = io.join_paths(src, file)

        if extension in video_extensions:
            videos[io.get_filename(file)] = path
        elif (extension in image_extensions and 
                not io.has_suffix(file, video_settings['thumbnail']['suffix'])):
            width, height = Image.open(path).size
            if (width >= image_settings['min_width'] and 
                    height >= image_settings['min_height']):
                images[io.get_filename(file)] = path
        
    paths = get_video_paths(videos, images, video_settings['thumbnail'])
    paths.update(get_image_paths(images))

    new_parent = os.path.join(dst, os.path.basename(src))
    paths_sorted = []
    for _, path in sorted(paths.items()):
        path_html = {
            'type': path['type'],
            'path': html.normalize_path(os.path.join(new_parent, path['path'])),
        }
        if path['type'] == 'video':
            path_html['thumbnail'] = html.normalize_path(
                os.path.join(new_parent, path['thumbnail']))
        paths_sorted.append(path_html)
    return paths_sorted


def get_image_paths(images: dict) -> dict:
    """Resolves paths to images.

    Parameters
    ----------
    images: dict
        Maps image filenames (no extension) to local image paths.
    
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
    for _, image_path in images.items():
        modification_time = os.path.getmtime(image_path)
        paths[modification_time] = {
            'type': 'image',
            'path': os.path.basename(image_path),
        }
    return paths


def get_video_paths(
        videos: dict, images: dict, thumbnail_settings: dict) -> dict:
    """Resolves paths to videos and their thumbnails.
    
    For each video, youtube-dl downloads a thumbnail having the same name (you-get
    does not). To make thumbnails easily recognizable, all of them should have a 
    common suffix. If a thumbnail does not exist, FFmpeg will extract a frame
    from the video as a thumbnail.

    Parameters
    ----------
    videos: dict
        Maps video filenames (no extension) to local video paths.
    images: dict
        Maps image filenames (no extension) to local image paths.
    thumbnail_settings: dict
        Includes the thumbnail cutoff ratio in video files along with common 
        suffix and extension of thumbnails.
        Format:
        {
            'cutoff': float('Cutoff ratio of video files to extract thumbnails. e.g. 0.1 means getting thumbnails at the 10% position of videos.'),
            'suffix': str('Common thumbnail suffix. e.g. _thumb'),
            'extension': str('Common thumbnail extension. e.g. .png')
        }

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
    for video_name, video_path in videos.items():
        thumbnail_path = None

        for image_name, image_path in images.items():
            if image_name == video_name:
                thumbnail_path = io.add_suffix(
                    image_path, thumbnail_settings['suffix'])
                shutil.move(image_path, thumbnail_path)
                break

        if thumbnail_path:
            del images[video_name]
        else:
            thumbnail_path = io.add_suffix(
                io.replace_extension(video_path, thumbnail_settings['extension']),
                thumbnail_settings['suffix'])
            try:
                video.create_thumbnail(
                    video_path, thumbnail_path, thumbnail_settings['cutoff'])
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


def _get_options() -> dict:
    parser = argparse.ArgumentParser(
        description='Maps URLs in Tweets to local paths if possible.')
    parser.add_argument(
        '-i', '--input', default='../data/texts/tweets_raw.json', type=str, 
        help='Path to the raw Tweets file.')
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
    return parser.parse_args()


if __name__ == '__main__':
    options = _get_options()
    io.make_directory(options.output)
    tweets = io.load_json(options.input)
    urls = io.load_json(options.references)
    settings = io.load_json(options.settings)
    video_settings = settings['video']
    image_settings = settings['image']

    print(color.get_info(f'Media paths of {len(tweets)} Tweets to resolve.'))
    for i, (tid, tweet) in enumerate(tweets.items()):
        text = tweet['text']
        if 'urls' not in text:
            continue

        print(
            f'({i + 1}/{len(tweets)}) Resolving media paths of Tweet #{tid}...')
        # Removes duplicated URLs within the same Tweet
        seen_urls = set()
        for url in text['urls']:
            expanded_url = url['expanded_url']
            if (expanded_url in urls) and (expanded_url not in seen_urls):
                local_directory = io.join_paths(
                    options.media, urls[expanded_url])

                if os.path.isdir(local_directory):
                    local_paths = get_media_paths(
                        local_directory, options.export, video_settings,
                        image_settings)
                    if 'media' not in tweet:
                        tweet['media'] = []

                    tweet['media'].append({
                        'remote': expanded_url,
                        'local': local_paths,
                    })
                seen_urls.add(expanded_url)

    tweets_path = io.join_paths(options.output, TWEETS_OUTPUT_FILENAME)
    if os.path.isfile(tweets_path):
        archive_path = io.archive_file(tweets_path)
        print(f"Archived '{tweets_path}' to '{archive_path}'.")
    io.dump_json(tweets, tweets_path)
    print(f"Saved {len(tweets)} path-resolved Tweets to '{tweets_path}'.")
    print()
    
    print(color.get_ok('Done.'))
