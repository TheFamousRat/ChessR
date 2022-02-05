from ctypes import util
from math import pi
import warnings
import bpy
import re
import numpy as np
from mathutils import *

import utils

class Board:
    CENTER_OBJ_NAME = "Center"
    BASE_OBJ_NAME = "Base"

    def delete(self, deleteAddedPieces):
        if deleteAddedPieces:
            for cellName in self.cellsPieces:
                self.cellsPieces[cellName].delete()
            self.cellsPieces = {}
        utils.deleteObjAndHierarchy(self.mesh)

    def setCellPiece(self, cellName, piece):
        """
        Assigns a piece to a given cell
        """
        self.cellsPieces[cellName] = piece

    def setBasePosAt(self, newPos):
        """
        Moves the board and its children so that the base is at a given position (in world coords)
        """
        baseObj = self.getBaseObj()

        self.mesh.matrix_world.translation += newPos - baseObj.matrix_world.translation

    def getCellObj(self, cellName):
        """
        Returns the empty object associated to a plateau's cell, or None if it didn't find it
        """
        if not (cellName in self.cellsNames):
            raise Exception("Trying to get a non-existing cell name ({})".format(cellName))
        
        foundChild = utils.getChildWithNameContaining(self.mesh, cellName)

        if foundChild == None:
            raise Exception("Trying to get non-instanciated cell {} on board {}".format(cellName, self.mesh.name))

        return foundChild

    def getCenterObj(self):
        """
        Returns the user-defined center of the board, and raises an error if it doesn't exist
        """
        foundChild = utils.getChildWithNameContaining(self.mesh, Board.CENTER_OBJ_NAME)

        if foundChild == None:
            raise Exception("No center found for board '{}', please create and position a child object with the name '{}' appropriately".format(self.mesh.name, Board.CENTER_OBJ_NAME))
        
        return foundChild

    def getBaseObj(self):
        """
        Returns the user-defined base of the board, and raises an error if it doesn't exist
        """
        foundChild = utils.getChildWithNameContaining(self.mesh, Board.BASE_OBJ_NAME)

        if foundChild == None:
            raise Exception("No base found for board '{}', please create and position a child object with the name '{}' appropriately".format(self.mesh.name, Board.BASE_OBJ_NAME))
        
        return foundChild

    def generateNewCell(self, cellName):
        """
        Creates a cell center object and positions it approximately on the Board
        Useful when dealing with a new unannotated Board to place the cells' locations without manually creating them
        """
        # Finding the absolute center position of the board
        plateauCenter = self.getCenterObj().matrix_world.to_location()
        
        # Delimiting the dimensions of a cell
        boardDims = (len(self.cellsLetters), len(self.cellsNumbers))
        cellSize = Vector((self.mesh.dimensions.x / boardDims[0], self.mesh.dimensions.y / boardDims[1], 0.0))
        upperLeftCellCenter = plateauCenter - Vector((cellSize.x * ((boardDims[0]/2.0) - 0.5), cellSize.y * ((boardDims[1]/2.0) - 0.5), 0.0))
        
        # Determining the characteristics of the cell
        cellNumber = re.findall(r'\d+', cellName)[0]
        cellLetter = re.findall(r'[a-zA-Z]+', cellName)[0]
        
        # Determining the real world coords of the cell's center
        cellCoords = Vector((self.cellsLetters.index(cellLetter), self.cellsNumbers.index(cellNumber), 0.0))     
        cellCenterPos = upperLeftCellCenter + Vector((cellSize.x * cellCoords.x, cellSize.y * cellCoords.y, 0.0))
        
        # Creating and configuring the new cell
        newCell = bpy.data.objects.new(cellName, None)    
        
        bpy.context.scene.collection.objects.link(newCell)
        
        newCell.empty_display_size = 0.04
        newCell.empty_display_type = 'PLAIN_AXES'   
        
        newCell.parent = self.mesh
        
        newCell.matrix_parent_inverse = self.mesh.matrix_world.inverted()
        newCell.location = cellCenterPos
        
        return newCell

    def regenerateCells(self):
        #Deleting all the found cells
        for cellName in self.cellsLetters:
            for cell in utils.getChildrenWithNameContaning(self.mesh, cellName):
                bpy.data.objects.remove(cell)
        
        #Adding the cells now, approximately in their required position
        for cellName in self.cellsNames:
            self.generateNewCell(cellName)

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

        self.getBaseObj()
        self.getCenterObj()

        try:
            # Checking if all cells are present among the set's children
            for cellName in self.cellsNames:
                self.getCellObj(cellName)
        except Exception as e:
            print("Incomplete cells annotions found for board '{}'.".format(self.mesh.name))
            #A different number of cells than expected was found
            #As such, we delete all the cells and "start over"
            
            self.regenerateCells()

            raise Exception("Missing cells detected for board '{}'." +
            "Old cells have been deleted and new have regenerated, but their position will likely have to be checked by hand")
        
        self.cellsPieces = {}

        #Getting the size of a cell. Only supports square cells for the time being.
        cellA1 = self.getCellObj("A1")
        cellB2 = self.getCellObj("B2")
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
    def delete(self):
        utils.deleteObjAndHierarchy(self.mesh)

    def getBase(self):
        return utils.getChildWithNameContaining(self.mesh, "Base")

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

    def getStoredPiecesTypes(self):
        """
        Returns the unique types of the pieces contained in the set
        """
        return list(set(self.pieces.keys()))

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