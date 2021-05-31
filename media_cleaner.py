import json
import os
import shutil

WORKING_DIR = 'media'
BACKUP_DIR = 'backup'

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

def import_data(src):
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

if __name__ == '__main__':
    create_directory(BACKUP_DIR)

    url_to_name = import_data('url_to_name.json')
    media_to_move = set()
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
