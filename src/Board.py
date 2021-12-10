import bpy
import re
import numpy as np
from mathutils import *

import utils

class Board:
    def getCell(self, cellName):
        """
        Returns the empty object associated to a plateau's cell, or None if it didn't find it
        """
        if not (cellName in self.cellsNames):
            raise Exception("Trying to get a non-existing cell name ({})".format(cellName))
        
        foundCells = utils.getChildrenWithNameContaning(self.mesh, cellName)
        
        if len(foundCells) == 0:
            #No child has the name of the cell
            return None
        elif len(foundCells) == 1:
            #We found exactly one cell with this name
            return foundCells[0]
        else:
            #More than one cell with this name was found
            return None

    def addCell(self, cellName):
        """
        Creates and positions roughly the center of a cell on a given plateau
        """
        #Finding the absolute center position of the cell
        plateauCenter = self.mesh.matrix_world.to_translation()
        cellSize = self.mesh.dimensions.x / 8.0
        upperLeftCellCenter = plateauCenter - 3.5 * Vector((cellSize, cellSize, 0.0))
        
        cellNumber = re.findall(r'\d+', cellName)[0]
        cellLetter = re.findall(r'[a-zA-Z]+', cellName)[0]
        
        cellCoords = Vector((self.cellsLetters.index(cellLetter), self.cellsNumbers.index(cellNumber), 0.0))     
        cellCenterPos = upperLeftCellCenter + cellSize * cellCoords
        
        #Creating and configuring the new cell
        newCell = bpy.data.objects.new(cellName, None)    
        
        bpy.context.scene.collection.objects.link(newCell)
        
        newCell.empty_display_size = 0.04
        newCell.empty_display_type = 'PLAIN_AXES'   
        
        newCell.parent = self.mesh
        
        newCell.matrix_parent_inverse = self.mesh.matrix_world.inverted()
        newCell.location = cellCenterPos
        
        return newCell

    def __init__(self, sourceMesh_, cellsNames_) -> None:
        """
        Creates a Board object from an appropriate Blender mesh

        :param mesh sourceMesh_: A Blender mesh with a board structure
        :param list cellsNames_: A list of names representing all the cells that the Board should have
        """
        #Getting basic board information
        self.cellsNames = cellsNames_
        self.mesh = sourceMesh_

        #Deducing the letters and numbers of rows and columns on the board
        self.cellsLetters = list(set([re.search(r'[a-zA-Z]+', cellName).group(0) for cellName in self.cellsNames]))
        self.cellsNumbers = list(set([re.search(r'\d+', cellName).group(0) for cellName in self.cellsNames]))
        self.cellsLetters.sort()
        self.cellsNumbers.sort()

        childrenNames = [child.name for child in self.mesh.children]
    
        #Checking if all cells are present among the set's children
        cellsFound = [cellName for cellName in self.cellsNames if (self.getCell(cellName) != None)]
        
        cellsFound.sort()
        if self.cellsNames != cellsFound:
            print("Incorrect cells found for the board '{}'. Deleting old cells and adding new placeholders.".format(self.mesh.name))
            #A different number of cells than expected was found
            #As such, we delete all the cells and "start over"
            
            #Deleting all the found cells
            for cellName in self.cellsLetters:
                for cell in utils.getChildrenWithNameContaning(self.mesh, cellName):
                    bpy.data.objects.remove(cell)
            
            #Adding the cells now, approximately in their required position
            for cellName in self.cellsNames:
                self.addCell(cellName)

            raise Exception("Board initialization incomplete due to inadequate cells structure.")

        #Getting the size of a cell
        #For now supporting only square cells
        cellA1 = self.getCell("A1")
        cellB2 = self.getCell("B2")
        self.cellSize = np.linalg.norm(np.array(cellA1.matrix_world.to_translation() - cellB2.matrix_world.to_translation())) / np.sqrt(2.0)

        print("Board '{}' ok.".format(self.mesh.name))

class Piece:
    """
    Class representing a board game piece
    """
    def getBase(self):
        foundCells = utils.getChildrenWithNameContaning(self.mesh, "Base")
        
        if len(foundCells) == 0:
            #No child has the name of the cell
            return None
        elif len(foundCells) == 1:
            #We found exactly one cell with this name
            return foundCells[0]
        else:
            #More than one cell with this name was found
            return None

    def __init__(self, sourceMesh_) -> None:
        """
        Creating a Piece instance from a given adequately prepared mesh
        """
        self.mesh = sourceMesh_

        self.base = self.getBase()
        if self.base == None:
            raise Exception("No base found for piece '{}'".format(self.mesh.name))
        
        if not (self.base.type == 'EMPTY'):
            raise Exception("Inadequate type for base of piece '{}' : must be an Empty".format(self.mesh.name))

        self.baseDiameter = np.array(self.base.empty_display_size * self.base.matrix_world.to_scale())
        self.baseDiameter[2] = 0.0
        self.baseDiameter = 2.0 * max(self.baseDiameter)
        print(self.baseDiameter)


class PiecesSet:
    pass