import os
import pickle
from collections import defaultdict

WORKING_DIR = 'media'
OUTPUT_PATH = 'exts.pickle'

def export_data(data, dst):
    with open(dst, 'wb') as f:
        pickle.dump(data, f)

if __name__ == '__main__':
    exts = defaultdict(set)
    for root, dirs, files in os.walk(WORKING_DIR):
        if files:
            for file in files:
                name, ext = os.path.splitext(file)
                ext_no_dot = ext[1:]
                subdir = os.path.split(root)[1]
                exts[ext_no_dot].add((subdir, file))
    export_data(exts, OUTPUT_PATH)
    print(f'Saved extension info to {OUTPUT_PATH}')
