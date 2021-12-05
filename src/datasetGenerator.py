import bpy
import re
import warnings
from math import *
from mathutils import *

###Constants
#Plateau cells constants
cellsLetters = ["A", "B", "C", "D", "E", "F", "G", "H"]
cellsNumbers = ["1", "2", "3", "4", "5", "6", "7", "8"]
cellsCount = len(cellsLetters) * len(cellsNumbers)
cellsNames = [cellLetter + cellNumber for cellLetter in cellsLetters for cellNumber in cellsNumbers]
cellsNames.sort()

PIECE_BASE_NAME = 'Base'

###Functions
#General
def setSelectOfObjectAndChildren(obj, selectState):
    """
    Sets a node and its hierarchy to a given selectState (True or False)
    """
    obj.select_set(selectState)
    
    for child in obj.children:
        setSelectOfObjectAndChildren(child, selectState)

def getChildrenWithNameContaning(parent, stringToSearch):
    """
    Returns all children of an objects whose names contain a user-provided string
    """
    return [child for child in parent.children if (re.search(stringToSearch, child.name) != None)]

#Scene-specific (to move to class files later probably)
def getPlateauCell(plateau, cellName):
    """
    Returns the empty object associated to a plateau's cell, or None if it didn't find it
    """
    if not (cellName in cellsNames):
        raise Exception("Trying to get a non-existing cell name ({})".format(cellName))
    
    foundCells = getChildrenWithNameContaning(plateau, cellName)
    
    if len(foundCells) == 0:
        #No child has the name of the cell
        return None
    elif len(foundCells) == 1:
        #We found exactly one cell with this name
        return foundCells[0]
    else:
        #More than one cell with this name was found
        return None

def addCellToPlateau(plateau, cellName):
    """
    Creates and positions roughly the center of a cell on a given plateau
    """
    #Finding the absolute center position of the cell
    plateauCenter = plateau.matrix_world.to_translation()
    cellSize = plateau.dimensions.x / 8.0
    upperLeftCellCenter = plateauCenter - 3.5 * Vector((cellSize, cellSize, 0.0))
    
    cellNumber = re.findall(r'\d+', cellName)[0]
    cellLetter = re.findall(r'[a-zA-Z]+', cellName)[0]
    
    cellCoords = Vector((cellsLetters.index(cellLetter), cellsNumbers.index(cellNumber), 0.0))     
    cellCenterPos = upperLeftCellCenter + cellSize * cellCoords
    
    #Creating and configuring the new cell
    newCell = bpy.data.objects.new(cellName, None)    
    
    bpy.context.scene.collection.objects.link(newCell)
    
    newCell.empty_display_size = 0.04
    newCell.empty_display_type = 'PLAIN_AXES'   
    
    newCell.parent = plateau
    
    newCell.matrix_parent_inverse = plateau.matrix_world.inverted()
    newCell.location = cellCenterPos
    
    return newCell

###Program body
#Checking whether relevant collections are here
if not 'plateaux' in bpy.data.collections:
    raise Exception("No plateau found, generation impossible")

allPlateaux = bpy.data.collections['plateaux'].objects

#Checking that all sets are annotated for their grid positions
print("Checking whether all the plateaux have a correct number of cells")

cellIncorrectlyIndicated = False

for plateau in allPlateaux:
    childrenNames = [child.name for child in plateau.children]
    
    #Checking if all cells are present among the set's children
    cellsFound = []
    for cellName in cellsNames:
        cellFound = getPlateauCell(plateau, cellName)
        
        if cellFound != None:
            cellsFound.append(cellName)
    
    cellsFound.sort()
    if cellsNames != cellsFound:
        cellIncorrectlyIndicated = True
        print("Incorrect cells found for the plateau '{}'. Deleting old cells and ".format(plateau.name))
        #A different number of cells than expected was found
        #As such, we delete all the cells and "start over"
        
        #Deleting all the found cells
        for cell in cellsFound.copy():
            bpy.data.objects.remove(cell)
        
        #Adding the cells now, approximately in their required position
        plateauCenter = plateau.matrix_world.to_translation()
        plateauDims = plateau.dimensions
        cellSize = plateauDims.x / 8.0
        upperLeftCellCenter = plateauCenter - 3.5 * Vector((cellSize, cellSize, 0.0))
        
        for cellName in cellsNames:
            addCellToPlateau(plateau, cellName)
    else:
        print("Plateau '{}' ok.".format(plateau.name))
    
if cellIncorrectlyIndicated:
    raise Exception("Some cells were missing, please correct with the newly added cells")

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
                
                chessSetsPieces[chessSet.name][pieceType] = chessCollectionItem
    
    #Checking whether the collection's found pieces have all the right pieces types
    setPiecesTypes = list(chessSetsPieces[chessSet.name].keys())
    setPiecesTypes.sort()
    
    if not (piecesTypes == setPiecesTypes):
        warnings.warn("Set '{}' doesn't have all registered pieces types, discarding".format(chessSet.name))
        chessSetsPieces.erase(chessSet.name)
    else:
        print("Chess set '{}' has all registered pieces types".format(chessSet.name))

##Testing the logic to duplicate and place a piece on a set
#mouthful.com
def duplicateAndPlacePieceOnPlateauCell(pieceToDup, plateau, cellName):
    bpy.ops.object.select_all(action='DESELECT')
    setSelectOfObjectAndChildren(pieceToDup, True)
    bpy.ops.object.duplicate()

    #Select the parent in the new selection
    duplicatedPiece = bpy.context.selected_objects[0]
    while not (duplicatedPiece.parent == None):
        if duplicatedPiece.parent in bpy.context.selected_objects:
            duplicatedPiece = duplicatedPiece.parent

    pieceBase = getChildrenWithNameContaning(duplicatedPiece, PIECE_BASE_NAME)[0]
    chessBoardCell = getChildrenWithNameContaning(plateau, cellName)[0]

    duplicatedPiece.location += chessBoardCell.matrix_world.to_translation() - pieceBase.matrix_world.to_translation()

for cellName in cellsNames:
    duplicateAndPlacePieceOnPlateauCell(bpy.data.objects['queen_w.001'], bpy.data.objects['Grid'], cellName)