import argparse
import subprocess

if __name__ == "__main__":

    # Create parser
    parser = argparse.ArgumentParser(description="Generate image data from blender models.")

    # Add arguments
    parser.add_argument("--file", "-f", help="Name of .blend file.")
    parser.add_argument("-n" , help="Amount of renders to generate, default is 1.", default=1)
    parser.add_argument("--folder" , help="(Optional) Custom name of render folder.")
    parser.add_argument("--n-instances", help="Number of instances of the model, default is 1.", default=1)

    # Parse arguments
    args = vars(parser.parse_args())
    
    prop_name = args["file"]
    n_renders = args["n"]
    n_instances = args["n_instances"]
    
    if args["folder"]:
        folder_name = args["folder"]
    else:
        folder_name = ""
    
    command =f"blender blendgen/basescene.blend --background --python blendgen/blender.py -- {prop_name} {n_renders} {n_instances} {folder_name}"
    subprocess.run(command, shell=True)
    #subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
