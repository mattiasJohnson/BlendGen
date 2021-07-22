import sys
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if not THIS_DIR in sys.path:
    sys.path.append(THIS_DIR)

import blendgen


if __name__ == "__main__":
    # Get all arguments after --
    argv = sys.argv[sys.argv.index("--") + 1:]
    prop_name = argv[0]
    n_images = int(argv[1])
    n_instances = int(argv[2])
    folder_name = argv[3] if len(argv) >=4 else None
    
    blendgen.generate(prop_name, n_images, n_instances, folder_name)