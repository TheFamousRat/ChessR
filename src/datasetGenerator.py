import bpy
import re
from math import *
from mathutils import *

###Constants
#Plateau cells constants
cellsLetters = ["A", "B", "C", "D", "E", "F", "G", "H"]
cellsNumbers = ["1", "2", "3", "4", "5", "6", "7", "8"]
cellsCount = len(cellsLetters) * len(cellsNumbers)
cellsNames = [cellLetter + cellNumber for cellLetter in cellsLetters for cellNumber in cellsNumbers]
cellsNames.sort()

###Functions
def getPlateauCell(plateau, cellName):
    """
    Returns the empty object associated to a plateau's cell, or None if it didn't find it
    """
    if not (cellName in cellsNames):
        raise Exception("Trying to get a non-existing cell name ({})".format(cellName))
    
    childrenNames = [child.name for child in plateau.children]
    
    cellNameOccurencesIdx = [cellName in childName for childName in childrenNames]
    cellNameOccurencesNum = sum(cellNameOccurencesIdx)
    
    if cellNameOccurencesNum == 0:
        #No child has the name of the cell
        return None
    elif cellNameOccurencesNum == 1:
        #We found exactly one cell with this name
        return plateau.children[cellNameOccurencesIdx.index(True)]
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

