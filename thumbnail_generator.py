import subprocess
import os
import pickle
from datetime import datetime

VIDEO_EXTENSIONS = {
    'mp4',
    'webm',
    'mkv'
}
TIMESTAMP_FORMAT = '%H:%M:%S.%f'
THUMBNAIL_START_RATIO = 0.15
BASE_TIME = datetime.strptime('00:00:00.00', TIMESTAMP_FORMAT)
WORKING_DIR = 'media'

def import_data(src):
    with open(src, 'rb') as f:
        return pickle.load(f)

def get_video_duration(path):
    out = subprocess.run(['ffmpeg', '-i', path], capture_output=True, encoding='utf-8')
    err_msg = out.stderr.split('\n')
    for line in err_msg:
        line = line.strip()
        if line.startswith('Duration'):
            # e.g. Duration: 00:01:13.70, start: 0.000000, bitrate: 839 kb/s
            timestamp = line.split(', ')[0].split(': ')[1]
            return datetime.strptime(timestamp, TIMESTAMP_FORMAT) - BASE_TIME
    raise LookupError('Missing duration')

def get_thumbnail_start(duration):
    # datetime gives microseconds in 6 digits. FFmpeg only need 2 digits.
    return (duration * THUMBNAIL_START_RATIO + BASE_TIME).strftime(TIMESTAMP_FORMAT)[:-4]    

def export_thumbnail(src):
    get_video_duration(src)
    duration = get_video_duration(src)
    start = get_thumbnail_start(duration)

    name, ext = os.path.splitext(src)
    subprocess.run([
        'ffmpeg',
        '-hide_banner',
        '-loglevel', 'error',
        '-y',
        '-ss', start,
        '-i', src,
        '-vframes', '1',
        '-an',
        f'{name}_thumb.png'
    ])

if __name__ == '__main__':
    exts = import_data('exts.pkl')
    for ext in VIDEO_EXTENSIONS:
        videos = exts[ext]
        print(f'Type: {ext}')
        for i, (dirname, filename) in enumerate(videos):
            path = os.path.join(WORKING_DIR, os.path.join(dirname, filename))
            export_thumbnail(path)
            if i % 10 == 0 and i > 0:
                print(f'  Processed {i}/{len(videos)} videos.')
        print(f'  Processed {len(videos)}/{len(videos)} videos.')
        print()
