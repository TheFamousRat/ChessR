import numpy as np
from mathutils import *
import utils
    

class BoardConfigurationGenerator:
    """
    Class focusing on randomly generating and applying plausible rendering situations of Board game configurations
    """
    def __init__(self) -> None:
        self.imagesWidth = 640 #Width and height of output images
        self.imagesHeight = 640 
        self.emptyCellProb = 0.5 #Probability of a cell being empty when generating a configuration
        self.lastAppliedConfig = None

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

    def generateRandomPiecesPlacement(self, piecesTypes, cellsNames):
        """
        Generates a random configuration for the board, that is assigning every cell to a randomly selected piece or to nothing
        """
        # Possible outputs for each cell : a piece type, or None
        piecesTypesWithNone = piecesTypes + [None]
        # Weights associated with the possible outputs
        weights = ([(1.0 - self.emptyCellProb)/len(piecesTypes)] * len(piecesTypes)) + [self.emptyCellProb]
        # Picking random values, and associating them with their cell to create a configuration
        pickedCells = np.random.choice(piecesTypesWithNone, len(cellsNames), p=weights)
        piecesPlacement = {cellsNames[i] : pickedCells[i] for i in range(len(cellsNames))}

        return piecesPlacement

    def applyConfigurationToBoard(self, configuration, board, piecesSet):
        """
        Applies a given configuration to a board with a specific game set, by placing all the pieces specified by the configuration on their appropriate cells
        """
        for cellName in configuration:
            pieceType = configuration[cellName]
            if pieceType != None:
                self.duplicateAndPlacePieceOnBoardCell(piecesSet.getPieceOfType(configuration[cellName])[0], board, cellName)

        self.lastAppliedConfig = configuration
    
    def positionCameraAroundBoardCenter(self, board, cam):
        """
        Randomly positions the camera at an overlooking again of the board, focused on its center (roughly)
        """
        theta = np.random.uniform(low=0.0, high=0.7) 
        phi = np.random.uniform(low=0.0, high=2.0*np.pi)
        r = 1.0

        boardCenterObj = board.getCenterObj()
        boardCenter = np.array(boardCenterObj.matrix_world.to_translation())
        cam.matrix_world = utils.lookAtFromPos(boardCenter, boardCenter + utils.getSphericalCoordinates(r, theta, phi))

    def outputLastRenderAnnotations(self, filepath):
        """
        Outputs to a JSON file the annotations of the last generated configuration
        """
        pass

    def generateRandomRenderConfiguration(self, board, piecesSet, cam):
        config = self.generateRandomPiecesPlacement(piecesSet.getStoredPiecesTypes(), board.cellsNames)
        self.applyConfigurationToBoard(config, board, piecesSet)
        self.positionCameraAroundBoardCenter(board, cam)

