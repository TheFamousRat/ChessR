"""
File to store various program-wide constants
"""

import os
import bpy
import imghdr

def checkForNonEmptyCollection(collectionName):
    """
    Checks whether a collection with a given name exists and has more than 0 objects
    """
    return (False if (not collectionName in bpy.data.collections) else (len(bpy.data.collections[collectionName].all_objects) > 0))

def getNonEmptyCollection(collectionName):
    if checkForNonEmptyCollection(collectionName):
        return bpy.data.collections[collectionName]
    else:
        raise Exception("No non-empty collection named '{}' found.".format(collectionName))

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

# Gathering the relevant collection, raising an exception if they don't exist
PLATEAUX_COLLECTION = getNonEmptyCollection('plateaux')
PIECES_TYPES_COLLECTION = getNonEmptyCollection('piecesTypes')
GAME_SETS_COLLECTION = getNonEmptyCollection('Pieces sets')

EMPTIES_COLLECTION_NAME = 'empties'
if not EMPTIES_COLLECTION_NAME in bpy.data.collections:
    bpy.data.collections.new(EMPTIES_COLLECTION_NAME)
EMPTIES_COLLECTION = bpy.data.collections['empties']