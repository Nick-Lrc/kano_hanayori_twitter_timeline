import os
import pickle
from collections import defaultdict

WORKING_DIR = 'media'
OUTPUT_PATH = 'exts.pkl'

def export_data(data, dst):
    with open(dst, 'wb') as f:
        pickle.dump(data, f)

if __name__ == '__main__':
    exts = defaultdict(set)
    for root, dirs, files in os.walk(WORKING_DIR):
        if files:
            for file in files:
                path = os.path.join(os.path.join(root, file))
                name, ext = os.path.splitext(file)
                ext_no_dot = ext[1:]
                exts[ext_no_dot].add(path)
    export_data(exts, OUTPUT_PATH)
    print(f'Saved extension info to {OUTPUT_PATH}')
