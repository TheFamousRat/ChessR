from ctypes import util
from math import pi
import warnings
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
    
    def duplicate(self):
        """
        Duplicates the mesh from which the Board object was extracted, and returns a Board created from this duplicated mesh
        """
        dupMesh = utils.duplicateObjectAndHierarchy(self.mesh, True)

        return Board(dupMesh, self.cellsNames)

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

        :param mesh sourceMesh_: A Blender mesh with a piece structure
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
    
    def duplicate(self):
        """
        Duplicates the mesh from which the Piece object was extracted, and returns a Piece created from this duplicated mesh
        """
        dupMesh = utils.duplicateObjectAndHierarchy(self.mesh, linked=True)

        return Piece(dupMesh)

class PiecesSet:
    def getPieceOfType(self, pieceType):
        """
        Returns the object corresponding to a piece, looked for by its type
        """
        if not pieceType in self.pieces:
            raise Exception("Looking for piece type '{}', non-existent in current set".format(pieceType))

        return self.pieces[pieceType]

    def __init__(self, sourceCollection_, piecesTypesCollection) -> None:
        """
        Creating a set of pieces

        :param collection sourceCollection_: Source collection containing the pieces of the set
        :param collection piecesTypesCollection: Collection under which are the collections grouping the pieces by types
        """
        self.sourceCollection = sourceCollection_

        self.pieces = {}

        #Looking for items in the collection that are registered as chess pieces
        for collectionItem in self.sourceCollection.objects:
            #Checking if the item is also present in collections containing pieces of a certain type
            pieceTypeCollection = list(set(collectionItem.users_collection) & set(piecesTypesCollection.children))
            
            if (len(pieceTypeCollection) > 1):
                raise Exception("Piece '{}' belongs to more than one chess type, check if it belongs to more than one chess type collection".format(collectionItem))
            elif len(pieceTypeCollection) == 1:
                pieceType = pieceTypeCollection[0].name
                
                try:
                    piece = Piece(collectionItem)

                    if not (pieceType in self.pieces):
                        self.pieces[pieceType] = []

                    self.pieces[pieceType].append(piece)
                except Exception as e:
                    warnings.warn("Could not instanciate the piece '{}' : {}".format(collectionItem.name, e))