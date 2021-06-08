import pickle
import json
import os

WORKING_DIR = os.path.join('..', 'kano_hanayori_twitter')
DATA_DIR = os.path.join(WORKING_DIR, 'data')
MEDIA_DIR = os.path.join(DATA_DIR, 'media')
THUMBNAIL_SUFFIX = '_thumb'
EXPORT_PATH = os.path.join(DATA_DIR, 'raw', 'tweets.pickle')

IMAGE_FORMATS = {
    '.jpg',
    '.png'
}

VIDEO_FORMATS = {
    '.mp4',
    '.webm',
    '.mkv'
}

def import_pickle(src):
    with open(src, 'rb') as f:
        return pickle.load(f)

def import_json(src):
    with open(src, 'r') as f:
        return json.load(f)

def export_pickle(data, dst):
    with open(dst, 'wb') as f:
        pickle.dump(data, f)

def is_thumbnail(filename):
    return filename.endswith(THUMBNAIL_SUFFIX)

def get_local_media_path(thumbnail_path):
    media_name = thumbnail_path.rpartition(THUMBNAIL_SUFFIX)[0]
    for ext in VIDEO_FORMATS:
        media_path = f'{media_name}{ext}'
        if os.path.exists(media_path):
            return media_path
    return None

def resolve_media_paths(tid, tweet, url_to_name):
    media = []
    seen_media = set()
    for idx, media_info in enumerate(tweet['urls']):
        url = media_info['expanded_url']
        name = url_to_name[url]
        dirname = os.path.join(MEDIA_DIR, name)
        if not os.path.exists(dirname):
            continue

        for file in os.listdir(dirname):
            name, ext = os.path.splitext(file)
            if ext in IMAGE_FORMATS:
                img_path = os.path.join(dirname, file)
                if img_path not in seen_media:
                    media_path = local_path_to_html_path(img_path)
                    if is_thumbnail(name):
                        local_path = get_local_media_path(img_path)
                        if local_path:
                            media_path = local_path_to_html_path(local_path)
                        else:
                            media_path = url
                    media.append((local_path_to_html_path(img_path), media_path))
                    seen_media.add(img_path)
    return media

def local_path_to_html_path(local_path):
    return '/'.join(local_path.split(os.sep)[2:])

if __name__ == '__main__':
    log = import_pickle('log.pickle')
    url_to_name = import_json('url_to_name.json')

    num_tweets = len(log)
    for i, (tid, tweet) in enumerate(sorted(log.items())):
        log[tid]['media'] = resolve_media_paths(tid, tweet, url_to_name)
        if (i + 1) % 100 == 0:
            print(f'Resolved media paths of {i + 1}/{num_tweets} tweets')
    print(f'Resolved media paths of {num_tweets}/{num_tweets} tweets')

    export_pickle(log, EXPORT_PATH)
    print(f'Saved tweet log to {EXPORT_PATH}.')
