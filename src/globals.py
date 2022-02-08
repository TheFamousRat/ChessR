"""
File to store various program-wide constants
"""

import os
import bpy
import imghdr

## Constants paths
basedir = bpy.path.abspath("//")

# Output folder
OUTPUT_FOLDER = os.path.join(basedir, "out")
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

RENDER_FRAME = 1 #The frame at which the render is done. Used for motion blurring

# HDRIs
HDRI_FOLDER = "/home/thefamousrat/Documents/Blender/Resources/HDRI"
hdriInFolderList = [filename for filename in os.listdir(HDRI_FOLDER) if not (imghdr.what(os.path.join(HDRI_FOLDER, filename)) == None)]

# Adding the HDRI to the loaded images
for hdri in hdriInFolderList:
    bpy.data.images.load(os.path.join(HDRI_FOLDER, hdri), check_existing = True)

hdrisLoaded = [bpy.data.images[hdri] for hdri in hdriInFolderList]