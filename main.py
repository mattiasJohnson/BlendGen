import argparse
import os
import subprocess
from datetime import datetime

THIS_PATH = os.path.dirname(os.path.abspath(__file__))
PACKAGE_PATH = os.path.join(THIS_PATH, "blendgen")
SAVED_PROP_PATH = os.path.join(THIS_PATH, "props")
EXECUTE_PATH = os.path.realpath(".")
MAIN_BLENDER_PATH = os.path.join(THIS_PATH, "main_blender.py")
SAVE_DIR_NAME = datetime.now().strftime("blendgen_%y%m%d%H%M%S")


def main():

    # Create parser
    parser = argparse.ArgumentParser(description="Generate image data from blender models.")

    # Add arguments
    parser.add_argument(
        "--prop-path",
        "-p",
        help=(
            "(Optional) Path to prop file (.blend) or path                             to directory containing props."
            " Default is BlendGen/props/"
        ),
        default=SAVED_PROP_PATH,
    )
    parser.add_argument(
        "--save-path",
        "-P",
        help=(
            "(Optional) Path to directory where to save generated directory.                             Default is"
            " directory where script was run."
        ),
        default=".",
    )
    parser.add_argument(
        "--save-name",
        "-N",
        help="(Optional) Name of generated directory.                             Default is timestamp.",
        default=SAVE_DIR_NAME,
    )
    parser.add_argument("--n-images", "-n", help="Number of images to generate. Default is 1.", default=1)
    parser.add_argument(
        "--n-instances",
        "-i",
        help="Number of instances of the model in each render.                         Maximum is 31. Default is 1.",
        default=1,
    )

    # Parse arguments
    args = vars(parser.parse_args())

    prop_path = args["prop_path"]
    save_path = args["save_path"]
    save_name = args["save_name"]
    n_images = int(args["n_images"])
    n_instances = int(args["n_instances"])

    # Make assertions on arguments
    if os.path.isdir(prop_path):
        prop_path = os.path.realpath(prop_path)
    else:
        print(f"ERROR: prop_path is not a directory: {prop_path}")

    if os.path.isdir(save_path):
        save_path = os.path.realpath(save_path)
    else:
        print(f"ERROR: save_path is not a directory: {save_path}")

    assert n_instances < 31, "n_instances maximum is 31"

    # Create save directories
    save_dir_path = os.path.join(save_path, save_name)
    renders_path = os.path.join(save_dir_path, "renders")
    labels_path = os.path.join(save_dir_path, "labels")
    os.mkdir(save_dir_path)
    os.mkdir(renders_path)
    os.mkdir(labels_path)

    # Launch Blender
    command = (
        f"blender --background --python {MAIN_BLENDER_PATH}         --"
        f" {prop_path} {save_dir_path} {n_images} {n_instances}"
    )
    subprocess.run(command, shell=True)
    # subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
