### Modules
from ctypes import util
import bpy
import re
import os
import sys
import json
import warnings
from math import *
from mathutils import *
import numpy as np
import bpy_extras

basedir = bpy.path.abspath("//")
## Local libraries (re-)loading
# Loading user-defined modules (subject to frequent changes and needed reloading)
pathsToAdd = [os.path.join(basedir, "src/")]

for pathToAdd in pathsToAdd:
    sys.path.append(pathToAdd)

import utils
import Board
import BoardImagesGenerator

import importlib
importlib.reload(utils)
importlib.reload(Board)
importlib.reload(BoardImagesGenerator)

from BoardImagesGenerator import BoardConfigurationGenerator

for pathToAdd in pathsToAdd:
    sys.path.remove(pathToAdd)

import gc
gc.collect()

### Constants
# Plateau cells constants
CELLS_LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H"]
CELLS_NUMBERS = ["1", "2", "3", "4", "5", "6", "7", "8"]
cellsCount = len(CELLS_LETTERS) * len(CELLS_NUMBERS)
CELLS_NAMES = [cellLetter + cellNumber for cellLetter in CELLS_LETTERS for cellNumber in CELLS_NUMBERS]
CELLS_NAMES.sort()

# Name of the reference at the foot of the piece, giving its diameter and center position
PIECE_BASE_NAME = 'Base'

# Gathering the relevant collection, raising an exception if they don't exist
PLATEAUX_COLLECTION = utils.getNonEmptyCollection('plateaux')
PIECES_TYPES_COLLECTION = utils.getNonEmptyCollection('piecesTypes')
GAME_SETS_COLLECTION = utils.getNonEmptyCollection('Chess sets')

# 
OUTPUT_FOLDER = os.path.join(basedir, "out")
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

#
cam = bpy.context.scene.camera
WORKING_FRAME = 1 #The frame at which the render is done. Used for motion blurring

### Functions
#...



cam = bpy.context.scene.camera


### Program body
## Loading necessary data (plateaux, sets, pieces types etc.)
# Loading plateaux
print("Instanciating boards")

allPlateaux = []
allBoardSuccessfullyInstanced = True
for plateau in PLATEAUX_COLLECTION.objects:
    try:
        newBoard = Board.Board(plateau, CELLS_NAMES)
        allPlateaux.append(newBoard)
        print("Instanciated board '{}' successfully".format(plateau.name))
    except Exception as e:
        warnings.warn("Exception on board '{}' :\n ''{}''\nThe board was not instanciated".format(plateau.name, e))
        allBoardSuccessfullyInstanced = False

if not allBoardSuccessfullyInstanced:
    raise Exception("Some boards were not correctly instanciated, please check the log.")

# Gathering all registered pieces types, represented by collections children to piecesTypes and containing links to the relevant pieces' meshes
print("Loading pieces types")

piecesTypes = []
for child in PIECES_TYPES_COLLECTION.children:
    if isinstance(child, bpy.types.Collection):
        piecesTypes.append(child.name)
piecesTypes.sort()

print("Found the following pieces types : {}".format(piecesTypes))

# Instancing PiecesSet, which provides an interface for accessing with individual pieces in the same set (that is, pieces that share the same style)
print("Instanciating pieces sets")
allSetsSuccessfullyInstanced = True

chessSets = []
for chessSet in GAME_SETS_COLLECTION.children:
    #Checking if the set is a collection (that might then contain pieces), otherwise skipping it
    if not isinstance(chessSet, bpy.types.Collection):
        continue

    newBoard = Board.PiecesSet(chessSet, PIECES_TYPES_COLLECTION)
    
    setPiecesTypes = list(newBoard.pieces)
    setPiecesTypes.sort()

    if setPiecesTypes != piecesTypes:
        warnings.warn("Set '{}' doesn't have all registered pieces types, discarding".format(newBoard.sourceCollection.name))
        allSetsSuccessfullyInstanced = False
    else:
        print("Chess set '{}' has all registered pieces types".format(newBoard.sourceCollection.name))
        chessSets.append(newBoard)

if not allSetsSuccessfullyInstanced:
    raise Exception("Some pieces sets were not correctly instanciated, please check the log.")

## Generating scenarios
print("Rendering...")
imagesToRenderCount = 10
imagesGenerator = BoardConfigurationGenerator()
plateauPos = Vector((0,2,0))

for imageIdx in range(imagesToRenderCount):
    print("Rendering image number {}...".format(imageIdx))
    # Setting board pos
    usedBoard = np.random.choice(allPlateaux)
    usedSet = np.random.choice(chessSets)

    newPlateau = usedBoard.duplicate()
    newPlateau.setBasePosAt(plateauPos)
    newPlateau.mesh.rotation_euler[2] = np.random.uniform(2.0*np.pi)

    # Setting pieces randomly
    annotations = imagesGenerator.generateRandomRenderConfiguration(newPlateau, usedSet, cam, WORKING_FRAME)

    # Cheeky rendering
    renderedImagePath = os.path.join(OUTPUT_FOLDER, "{}.jpg".format(imageIdx))
    bpy.context.scene.render.filepath = renderedImagePath
    
    bpy.context.scene.frame_set(WORKING_FRAME)
    bpy.ops.render.render(write_still=True)#'INVOKE_DEFAULT')
    
    # Dumping the annotations data
    annotationsPath = os.path.join(OUTPUT_FOLDER, "{}.json".format(imageIdx))
    json.dump(annotations, open(annotationsPath, "w"))

    # Cleaning created data
    print("Removing created data...")
    newPlateau.delete(True)

print("Done.")
