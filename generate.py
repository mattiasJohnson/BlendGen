import argparse
from os import strerror
import subprocess

if __name__ == "__main__":

    # Create parser
    parser = argparse.ArgumentParser(description="Generate image data from blender models.")

    # Add arguments
    parser.add_argument("--file", "-f", help="Name of .blend file.")
    parser.add_argument("-n" , help="(Optional) Amount of renders to generate, default is 1.", default=1)
    parser.add_argument("--folder" , help="(Optional) Custom name of render folder.")

    # Parse arguments
    args = vars(parser.parse_args())
    
    prop_name = args["file"]
    n_renders = args["n"]
    
    if args["folder"]:
        folder_name = args["folder"]
    else:
        folder_name = ""
    
    command =f"blender bin/basescene.blend --background --python bin/blender.py -- {prop_name} {n_renders} {folder_name}"
    subprocess.run(command, shell=True)
    #subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

