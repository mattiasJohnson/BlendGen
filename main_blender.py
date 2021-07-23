import sys
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if not THIS_DIR in sys.path:
    sys.path.append(THIS_DIR)

import blendgen


def main():
    # Get all arguments after --
    argv = sys.argv[sys.argv.index("--") + 1:]
    prop_path = argv[0]
    save_path = argv[1]
    n_images = int(argv[2])
    n_instances = int(argv[3])
    
    prop_paths = load_prop_paths(prop_path)
    
    blendgen.generate(prop_paths, save_path, n_images, n_instances)
    

def load_prop_paths(prop_dir_path):
    prop_paths = {}
    for filename in os.listdir(prop_dir_path):
        if filename.endswith(".blend"):
            filepath = os.path.join(prop_dir_path, filename)
            prop_name = filename[:-6]
            prop_paths[prop_name] = filepath
    
    return prop_paths


if __name__ == "__main__":
    main()
