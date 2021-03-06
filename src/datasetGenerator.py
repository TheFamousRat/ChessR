### Modules
import bpy
import os
import sys
import warnings
from math import *
from mathutils import *
import numpy as np
from progress.bar import Bar

basedir = bpy.path.abspath("//")
## Local libraries (re-)loading
# Loading user-defined modules (subject to frequent changes and needed reloading)
pathsToAdd = [os.path.join(basedir, "src/")]

for pathToAdd in pathsToAdd:
    sys.path.append(pathToAdd)

import utils
import globals
import Board
import BoardImagesGenerator

import importlib
importlib.reload(utils)
importlib.reload(globals)
importlib.reload(Board)
importlib.reload(BoardImagesGenerator)

from BoardImagesGenerator import BoardConfigurationGenerator, RenderIdGenerator
from globals import *

for pathToAdd in pathsToAdd:
    sys.path.remove(pathToAdd)

import gc
gc.collect()

### Constants

#
cam = bpy.context.scene.camera


### Functions

### Program body

# Removing empties from all collections except the main one
empties = [ob for ob in bpy.data.objects if ob.type == 'EMPTY']
for empty in empties:
    collecsToRemove = []
    for collec in empty.users_collection:
        if collec != EMPTIES_COLLECTION:
            collecsToRemove.append(collec)
            
    for collec in collecsToRemove:
        collec.objects.unlink(empty)
    
    if not EMPTIES_COLLECTION in empty.users_collection:
        EMPTIES_COLLECTION.objects.link(empty)

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
    print(setPiecesTypes)
    setPiecesTypes.sort()

    if setPiecesTypes != PIECES_TYPES:
        warnings.warn("Set '{}' doesn't have all registered pieces types, discarding".format(newBoard.sourceCollection.name))
        allSetsSuccessfullyInstanced = False
    else:
        print("Chess set '{}' has all registered pieces types".format(newBoard.sourceCollection.name))
        chessSets.append(newBoard)

if not allSetsSuccessfullyInstanced:
    raise Exception("Some pieces sets were not correctly instanciated, please check the log.")

## Generating scenarios
print("Rendering...")
imagesToRenderCount = 1
imagesGenerator = BoardConfigurationGenerator()
plateauPos = Vector((-10,10,0))

import time 

bar = Bar("Rendered image : ", max=imagesToRenderCount)

start = time.time()
for imageIdx in range(imagesToRenderCount):
    # Setting board pos
    usedBoard = np.random.choice(allPlateaux)
    usedSet = np.random.choice(chessSets)

    newPlateau = usedBoard.duplicate()
    newPlateau.setBasePosAt(plateauPos)
    newPlateau.mesh.rotation_euler[2] = np.random.uniform(2.0*np.pi)

    # Setting pieces randomly
    imagesGenerator.generateRandomRenderConfiguration(newPlateau, usedSet, cam)
    imagesGenerator.renderAndStoreBoardAndAnnotations(newPlateau, cam)
    
    # Cleaning created data
    print("Removing created data...")
    newPlateau.delete(True)
    bar.next()

end = time.time()
print(float(end - start) / float(imagesToRenderCount))

print("Done.")
