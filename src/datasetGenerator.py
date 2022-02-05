### Modules
from ctypes import util
import bpy
import re
import os
import sys
import warnings
from math import *
from mathutils import *
import numpy as np

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

from BoardImagesGenerator import BoardImagesGenerator

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

### Functions
def duplicateAndPlacePieceOnBoardCell(pieceToDup, board, cellName):
    """
    Duplicating and placing a piece on a given board cell
    """
    newPiece = pieceToDup.duplicate()
    newPieceMesh = newPiece.mesh

    chessBoardCell = board.getCell(cellName)

    newPieceMesh.location += chessBoardCell.matrix_world.to_translation() - newPiece.base.matrix_world.to_translation()
    
    #Randomness in the chess positions
    #Random rotation
    newPieceMesh.rotation_euler[2] = np.random.uniform(2.0*pi)
    
    #Random piece offset
    theta = np.random.uniform(2.0*pi)
    amp = ((board.cellSize - newPiece.baseDiameter)) * np.random.beta(1.0, 3.0)
    offset = amp * Vector((cos(theta), sin(theta), 0.0))
    newPieceMesh.location += Vector(offset)

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
    except Exception as e:
        warnings.warn("Exception on board '{}' : {}. The board was not instanciated".format(plateau.name, e))
        allBoardSuccessfullyInstanced = False

if not allBoardSuccessfullyInstanced:
    raise Exception("Some boards were not correctly instanciated, please check the log")

# Gathering all registered pieces types, represented by collections children to piecesTypes and containing links to the relevant pieces' meshes
print("Loading pieces types")

piecesTypes = []
for child in PIECES_TYPES_COLLECTION.children:
    if isinstance(child, bpy.types.Collection):
        piecesTypes.append(child.name)
piecesTypes.sort()

print("Found the following pieces types : {}".format(piecesTypes))

# Instancing PiecesSet, which provides an interface for accessing with individual pieces in the same set (that is, pieces that share the same style)
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
    else:
        print("Chess set '{}' has all registered pieces types".format(newBoard.sourceCollection.name))
        chessSets.append(newBoard)

if len(chessSets) == 0:
    raise Exception("No complete game set found, aborting")

## Generating scenarios
imagesGenerator = BoardImagesGenerator()
scenario = imagesGenerator.generateScenario(piecesTypes, CELLS_NAMES)
print(scenario)

for cellName in scenario:
    pieceType = scenario[cellName]
    if pieceType != None:
        duplicateAndPlacePieceOnBoardCell(chessSets[0].getPieceOfType(scenario[cellName])[0], allPlateaux[0], cellName)