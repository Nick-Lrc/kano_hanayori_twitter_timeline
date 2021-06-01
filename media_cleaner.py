import json
import os
import shutil
import pickle

WORKING_DIR = 'media'
BACKUP_DIR = 'backup'

MIN_IMG_WIDTH = 200

# @Kanolive_ became private.
PRESERVED_DOMAINS = {
    'https://twitter.com/Kanolive_',
    'https://twitter.com/kano_hanayori',
    'https://twitter.com/kanolive_'
}

MOVING_EXTENSIONS = {
    '.mp4',
    '.webm',
    '.mkv',
    '.xml'
}

def import_pickle(src):
    with open(src, 'rb') as f:
        return pickle.load(f)

def import_json(src):
    with open(src, 'r') as f:
        return json.load(f)

def create_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)

def is_domain_preserved(url):
    for domain in PRESERVED_DOMAINS:
        if url.startswith(domain):
            return True
    return False

def get_media_to_move(src):
    media = set()
    for file in os.listdir(src):
        name, ext = os.path.splitext(file)
        if ext in MOVING_EXTENSIONS:
            media.add((src, file))
    return media

def get_images_to_move(imgs):
    imgs_to_move = set()
    for size in imgs:
        if size[0] < MIN_IMG_WIDTH:
            for dirname, filename in imgs[size]:
                dir_path = os.path.join(WORKING_DIR, dirname)
                if os.path.exists(os.path.join(dir_path, filename)):
                    imgs_to_move.add((dir_path, filename))
    return imgs_to_move

def is_directory_empty(path):
    return len(os.listdir(path)) == 0

if __name__ == '__main__':
    create_directory(BACKUP_DIR)
    url_to_name = import_json('url_to_name.json')
    imgs = import_pickle('img_sizes.pickle')
    media_to_move = get_images_to_move(imgs)

    for url, name in url_to_name.items():
        if not is_domain_preserved(url):
            src = os.path.join(WORKING_DIR, name)
            if os.path.exists(src):
                media_to_move.update(get_media_to_move(src))
    print(f'{len(media_to_move)} media to move')
    print()

    num_media = len(media_to_move)
    for i, (old_dir, file) in enumerate(media_to_move):
        new_dir = old_dir.replace(WORKING_DIR, BACKUP_DIR)
        create_directory(new_dir)
        old_path = os.path.join(old_dir, file)
        new_path = os.path.join(new_dir, file)
        shutil.move(old_path, new_path)
        
        if (i + 1) % 10 == 0:
            print(f'Moved {i + 1}/{num_media} media.')
    print(f'Moved {num_media}/{num_media} media.')
    print()

    count = 0
    for subdir in os.listdir(WORKING_DIR):
        path = os.path.join(WORKING_DIR, subdir)
        if is_directory_empty(path):
            shutil.rmtree(path)
            count += 1
    print(f'Removed {count} empty directories.')
