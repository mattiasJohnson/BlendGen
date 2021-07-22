import argparse
import subprocess
import os
import sys

THIS_PATH = os.path.dirname(os.path.abspath(__file__))
PACKAGE_PATH = os.path.join(THIS_PATH, "blendgen")
# EXECUTE_PATH = os.path.realpath(__file__)


def main():
    # Create parser
    parser = argparse.ArgumentParser(description="Generate image data from blender models.")

    # Add arguments
    parser.add_argument("--file", "-f", help="Name of .blend file.")
    parser.add_argument("--folder" , help="(Optional) Custom name of render folder.")
    parser.add_argument("-n" , help="Amount of renders to generate, default is 1.", default=1)
    parser.add_argument("--n-instances", help="Number of instances of the model, default is 1.", default=1)

    # Parse arguments
    args = vars(parser.parse_args())
    
    prop_name = args["file"]
    n_renders = args["n"]
    n_instances = args["n_instances"]
    
    if args["folder"]:
        folder_name = args["folder"]
    else:
        print("ERROR: Fuckade upp att automatiskt skapa mapp, ge full sökväg")
        return
        folder_name = ""
          
    scene_path = os.path.join(THIS_PATH, "basescene.blend")
    main_blender_path = os.path.join(THIS_PATH, "main_blender.py")
    prop_path = os.path.join(THIS_PATH, "props/"+prop_name+".blend")
    
    command =f"blender --background --python {main_blender_path} -- {prop_path} {n_renders} {n_instances} {folder_name}"
    subprocess.run(command, shell=True)
    #subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    main()
