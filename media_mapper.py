import pickle
import json
from collections import defaultdict

def import_data(src):
    with open(src, 'rb') as f:
        return pickle.load(f)

def get_urls(tweet):
    urls = []
    seen_urls = set()
    for i, info in enumerate(tweet['urls']):
        url = info['expanded_url']
        if url not in seen_urls:
            urls.append((i, url))
            seen_urls.add(url)
    return urls

def export_data(data, dst):
    with open(dst, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)

if __name__ == '__main__':
    log = import_data('log.pickle')
    url_to_name = {}
    tid_to_media = defaultdict(dict)
    for tid, tweet in sorted(log.items()):
        urls = get_urls(tweet)
        for idx, url in urls:
            name = f'{tid}_{idx}'
            if url in url_to_name:
                name = url_to_name[url]
            else:
                url_to_name[url] = name
            tid_to_media[tid][idx] = name
    print(f'Found {len(url_to_name)} unique urls.')
    export_data(url_to_name, 'url_to_name.json')
    export_data(tid_to_media, 'tid_to_media.json')
