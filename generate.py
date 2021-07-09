import argparse
import subprocess

if __name__ == "__main__":

    # Create parser
    parser = argparse.ArgumentParser(description="Generate image data from blender models.")

    # Add arguments
    parser.add_argument("--file", "-f", help="Relative filepath to .blend file")

    # Parse arguments
    args = vars(parser.parse_args())

    ## Fix modelpath
    modelpath = "props/" + args["file"]
    if modelpath[-6:] != ".blend":
        modelpath = modelpath + ".blend"

    subprocess.run(f"blender bin/basescene.blend --background --python bin/blender.py -- {modelpath}" , shell=True)

