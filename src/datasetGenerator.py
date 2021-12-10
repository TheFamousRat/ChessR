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

#For each pieces set, get the objects representing a piece type and checking their integrity
chessSetsPieces = {}

for chessSet in bpy.data.collections['Chess sets'].children:
    chessSetsPieces[chessSet.name] = {}
    #Checking if the collection child is also a collection
    if chessSet.name in bpy.data.collections:
        #Looking for items in the collection that are registered as chess pieces
        for chessCollectionItem in chessSet.objects:
            #Checking if the item is also present in collections containing pieces of a certain type
            pieceTypeCollection = list(set(chessCollectionItem.users_collection) & set(bpy.data.collections['piecesTypes'].children))
            
            if (len(pieceTypeCollection) > 1):
                raise Exception("Piece '{}' belongs to more than one chess type, check if it belongs to more than one chess type collection".format(chessCollectionItem))
            elif len(pieceTypeCollection) == 1:
                pieceType = pieceTypeCollection[0].name
                #Checking that the found piece type in not already represented in the set
                if pieceType in chessSetsPieces[chessSet.name]:
                    raise Exception("Piece type '{}' represented more than once in the set '{}'".format(pieceType, chessSet.name))
                
                piece = Board.Piece(chessCollectionItem)
                chessSetsPieces[chessSet.name][pieceType] = piece
    
    #Checking whether the collection's found pieces have all the right pieces types
    setPiecesTypes = list(chessSetsPieces[chessSet.name].keys())
    setPiecesTypes.sort()
    
    if not (piecesTypes == setPiecesTypes):
        warnings.warn("Set '{}' doesn't have all registered pieces types, discarding".format(chessSet.name))
        chessSetsPieces.erase(chessSet.name)
    else:
        print("Chess set '{}' has all registered pieces types".format(chessSet.name))

raise Exception("Shite")

##Testing the logic to duplicate and place a piece on a set
#mouthful.com
def duplicateAndPlacePieceOnBoardCell(pieceToDup, board, cellName):
    bpy.ops.object.select_all(action='DESELECT')
    utils.setSelectOfObjectAndChildren(pieceToDup, True)
    bpy.ops.object.duplicate(linked=True)

    #Select the parent in the new selection
    duplicatedPiece = bpy.context.selected_objects[0]
    while not (duplicatedPiece.parent == None):
        if duplicatedPiece.parent in bpy.context.selected_objects:
            duplicatedPiece = duplicatedPiece.parent

    pieceBase = utils.getChildrenWithNameContaning(duplicatedPiece, PIECE_BASE_NAME)[0]
    chessBoardCell = utils.getChildrenWithNameContaning(board.mesh, cellName)[0]

    duplicatedPiece.location += chessBoardCell.matrix_world.to_translation() - pieceBase.matrix_world.to_translation()
    
    #Randomness in the chess positions
    #Random rotation
    duplicatedPiece.rotation_euler[2] = np.random.uniform(2.0*pi)
    
    #Random piece offset
    theta = np.random.uniform(2.0*pi)
    amp = (board.cellSize/2.0) * np.random.beta(1.0, 3.0)
    offset = amp * Vector((cos(theta), sin(theta), 0.0))
    duplicatedPiece.location += Vector(offset)

for cellName in cellsNames:
    duplicateAndPlacePieceOnBoardCell(bpy.data.objects['pawn_w'], allPlateaux[0], cellName)
    
#Baseline :
#3.3Go Base
#4.5Go Render
#Linked
#4.2Go Base
#5.5Go render
#Non-linked
#4.2Go Base
#5.5Go Render