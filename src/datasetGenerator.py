import bpy
import re
import os
import sys
import warnings
from math import *
from mathutils import *
import numpy as np

basedir = bpy.path.abspath("//")
##Local libraries (re-)loading
#Loading user-defined modules (subject to frequent changes and needed reloading)
pathsToAdd = [os.path.join(basedir, "src/")]

for pathToAdd in pathsToAdd:
    sys.path.append(pathToAdd)

import Board
import utils

import importlib
importlib.reload(Board)
importlib.reload(utils)

for pathToAdd in pathsToAdd:
    sys.path.remove(pathToAdd)

import gc
gc.collect()

###Constants
#Plateau cells constants
cellsLetters = ["A", "B", "C", "D", "E", "F", "G", "H"]
cellsNumbers = ["1", "2", "3", "4", "5", "6", "7", "8"]
cellsCount = len(cellsLetters) * len(cellsNumbers)
cellsNames = [cellLetter + cellNumber for cellLetter in cellsLetters for cellNumber in cellsNumbers]
cellsNames.sort()

PIECE_BASE_NAME = 'Base'

###Functions

###Program body
#Checking whether relevant collections are here
if not 'plateaux' in bpy.data.collections:
    raise Exception("No plateau found, generation impossible")

#Checking that all sets are annotated for their grid positions
print("Checking whether all the plateaux have a correct number of cells")

allPlateaux = []
allBoardSuccessfullyInstanced = True
for plateau in bpy.data.collections['plateaux'].objects:
    try:
        newBoard = Board.Board(plateau, cellsNames)
        allPlateaux.append(newBoard)
    except Exception as e:
        warnings.warn("Exception on board '{}' : {}. The board was not instanciated".format(plateau.name, e))
        allBoardSuccessfullyInstanced = False

if not allBoardSuccessfullyInstanced:
    raise Exception("Some boards were not correctly instanciated, please check the log")


#Pieces types
piecesTypes = []
for child in bpy.data.collections['piecesTypes'].children:
    if child.name in bpy.data.collections:
        piecesTypes.append(child.name)
piecesTypes.sort()

print("Found the following pieces types : {}".format(piecesTypes))

#Create for each collection listed as a pieces set a PiecesSet instance grouping all the pieces of the set, by type
chessSets = []

for chessSet in bpy.data.collections['Chess sets'].children:
    #Checking if the set is a collection (that might then contain pieces), otherwise skipping it
    if not chessSet.name in bpy.data.collections:
        continue

    newBoard = Board.PiecesSet(chessSet, bpy.data.collections['piecesTypes'])
    
    setPiecesTypes = list(newBoard.pieces)
    setPiecesTypes.sort()

    if setPiecesTypes != piecesTypes:
        warnings.warn("Set '{}' doesn't have all registered pieces types, discarding".format(newBoard.sourceCollection.name))
    else:
        print("Chess set '{}' has all registered pieces types".format(newBoard.sourceCollection.name))
        chessSets.append(newBoard)

##Testing the logic to duplicate and place a piece on a set
#mouthful.com
def duplicateAndPlacePieceOnBoardCell(pieceToDup, board, cellName):
    newPiece = pieceToDup.copy()
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

for cellName in cellsNames:
    duplicateAndPlacePieceOnBoardCell(chessSets[0].getPieceOfType("bishop_b")[0], allPlateaux[0], cellName)

#Baseline :
#3.3Go Base
#4.5Go Render
#Linked
#4.2Go Base
#5.5Go render
#Non-linked
#4.2Go Base
#5.5Go Render