import json
import subprocess
from subprocess import SubprocessError
import os
import traceback

WORKING_DIR = 'media'

# Exclude live streaming, channel, and other known unsupported domains.
# Exclude @Kanolive_ domains as well since @Kanolive_ has became private 
# since 05/29/2021.
EXCLUDED_DOMAINS = {
    # @Kanolive_
    'https://twitter.com/Kanolive_',
    'https://twitter.com/kano_hanayori',
    'https://twitter.com/kanolive_',
    # Live streaming
    'https://live.bilibili.com',
    'https://live.nicovideo.jp',
    # Channel
    'https://m.youtube.com/channel',
    'https://www.youtube.com/channel',
    'https://www.youtube.com/c',
    'http://space.bilibili.com',
    'https://space.bilibili.com',
    # Unsupported
    'https://bml.bilibili.com',
}

MAPPED_DOMAINS = {
    'https://youtu.be/': 'https://www.youtube.com/watch?v=',
}

SWITCH_DOWNLOADER_DOMAINS = {
    'https://www.youtube.com'
}

def import_data(src):
    with open(src, 'r') as f:
        return json.load(f)

def create_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)

def get_existing_media():
    names = set()
    for subdir_name in os.listdir(WORKING_DIR):
        names.add(subdir_name)
    return names

def remove_excluded_domains(url_to_name):
    out = {}
    for url, name in url_to_name.items():
        preserved = True
        for domain in EXCLUDED_DOMAINS:
            if url.startswith(domain):
                preserved = False
                break
        if preserved:
            out[url] = name
    return out

def map_domains(url_to_name):
    out = {}
    for url, name in url_to_name.items():
        for domain, mapping in MAPPED_DOMAINS.items():
            if url.startswith(domain):
                url = url.replace(domain, mapping)
                break
        out[url] = name
    return out

def download_media(url, name):
    downloader = 'you-get'
    for domain in SWITCH_DOWNLOADER_DOMAINS:
        if url.startswith(domain):
            downloader = 'youtube-dl'

    if downloader == 'you-get':
        subprocess.run([
            'you-get',
            '--skip-existing-file-size-check',
            url,
            '-o', os.path.join(WORKING_DIR, name)
        ])
    else:
        subprocess.run([
            'youtube-dl',
            '-i',
            '-w',
            url,
            '-o', os.path.join(os.path.join(WORKING_DIR, name), '%(title)s-%(id)s.%(ext)s')
        ])

if __name__ == '__main__':
    create_directory(WORKING_DIR)
    url_to_name = import_data('url_to_name.json')
    url_to_name = remove_excluded_domains(url_to_name)
    url_to_name = map_domains(url_to_name)
    num_urls = len(url_to_name)
    
    for i, (url, name) in enumerate(sorted(url_to_name.items())):
        print(f'{i + 1}/{num_urls} url: {url}')
        try:
            download_media(url, name)
        except SubprocessError:
            traceback.print_exc()
            print()
