import numpy as np
from mathutils import *
import utils

class BoardImagesGenerator:
    """
    Class focusing on randomly generating and rendering plausible images of Board game configurations
    """
    def __init__(self) -> None:
        self.imagesWidth = 640 #Width and height of output images
        self.imagesHeight = 640 
        self.emptyCellProb = 0.5 #Probability of a cell being empty when generating a configuration

    def generateRandomConfiguration(self, piecesTypes, cellsNames):
        """
        Generates a random configuration for the board, that is assigns every cell to a randomly selected piece or to nothing
        """
        # Possible outputs for each cell : a piece type, or None
        piecesTypesWithNone = piecesTypes + [None]
        # Weights associated with the possible outputs
        weights = ([(1.0 - self.emptyCellProb)/len(piecesTypes)] * len(piecesTypes)) + [self.emptyCellProb]
        # Picking random values, and associating them with their cell to create a configuration
        pickedCells = np.random.choice(piecesTypesWithNone, len(cellsNames), p=weights)
        cellsOccupancy = {cellsNames[i] : pickedCells[i] for i in range(len(cellsNames))}

        return cellsOccupancy
    
    def duplicateAndPlacePieceOnBoardCell(self, pieceToDup, board, cellName):
        """
        Duplicating and placing a piece on a given board cell.
        """
        # Duplicating the piece and placing it on the appropriate cell center
        newPiece = pieceToDup.duplicate()
        newPieceMesh = newPiece.mesh

        chessBoardCell = board.getCellObj(cellName)

        newPieceMesh.location += chessBoardCell.matrix_world.to_translation() - newPiece.base.matrix_world.to_translation()
        
        ## Randomness in the chess positions
        # Random rotation
        newPieceMesh.rotation_euler[2] = np.random.uniform(2.0*np.pi)
        
        # Random piece offset
        theta = np.random.uniform(2.0*np.pi)
        amp = ((board.cellSize - newPiece.baseDiameter)) * np.random.beta(1.0, 3.0)
        offset = amp * Vector((np.cos(theta), np.sin(theta), 0.0))
        newPieceMesh.location += Vector(offset)

        board.setCellPiece(cellName, newPiece)

    def applyConfigurationToBoard(self, configuration, board, piecesSet):
        """
        Applies a given configuration to a board with a specific game set, by placing all the pieces specified by the configuration on their appropriate cells
        """
        for cellName in configuration:
            pieceType = configuration[cellName]
            if pieceType != None:
                self.duplicateAndPlacePieceOnBoardCell(piecesSet.getPieceOfType(configuration[cellName])[0], board, cellName)

        return configuration

    def applyRandomConfigurationToBoard(self, board, piecesSet):
        """
        Same as 'applyConfigurationToBoard', only uses a random configuration generated beforehand
        """
        return self.applyConfigurationToBoard(self.generateRandomConfiguration(piecesSet.getStoredPiecesTypes(), board.cellsNames), board, piecesSet)