from PIL import Image
from collections import defaultdict
import pickle
import os

WORKING_DIR = 'media'
EXPORT_PATH = 'img_sizes.pickle'

IMAGE_FORMATS = {
    'jpg',
    'png'
}

def import_data(src):
    with open(src, 'rb') as f:
        return pickle.load(f)

def export_data(data, dst):
    with open(dst, 'wb') as f:
        pickle.dump(data, f)

if __name__ == '__main__':
    exts = import_data('exts.pickle')
    sizes = defaultdict(set)
    for ext in IMAGE_FORMATS:
        print(f'Type: {ext}')
        imgs = exts[ext]
        num_imgs = len(imgs)

        for i, (dirname, filename) in enumerate(imgs):
            path = os.path.join(WORKING_DIR, os.path.join(dirname, filename))
            size = Image.open(path).size
            sizes[size].add((dirname, filename))
            
            if (i + 1) % 100 == 0:
                print(f'  Processed {i + 1}/{num_imgs} images.')
        print(f'  Processed {num_imgs}/{num_imgs} images.')
        print()
    export_data(sizes, EXPORT_PATH)
    print(f'Saved image size info to {EXPORT_PATH}')
    