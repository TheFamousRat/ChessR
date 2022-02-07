import bpy
import bpy_extras
import numpy as np
from mathutils import *
import utils
import globals as glob
    

class BoardConfigurationGenerator:
    """
    Class focusing on randomly generating and applying plausible rendering situations of Board game configurations
    """
    FOCAL_LENGTH_RANGE = (30.0, 50.0)
    MAX_CAM_ANGLE_FROM_UPWARDS = np.pi * (20.0 / 180.0)

    def __init__(self) -> None:
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
        ## Positioning the camera roughly over the board's center
        theta = np.random.uniform(low=0.0, high=self.MAX_CAM_ANGLE_FROM_UPWARDS) 
        phi = np.random.uniform(low=0.0, high=2.0*np.pi)
        r = 1.0

        boardCenterObj = board.getCenterObj()
        boardCenter = np.array(boardCenterObj.matrix_world.to_translation())
        cam.matrix_world = utils.lookAtFromPos(boardCenter, boardCenter + utils.getSphericalCoordinates(r, theta, phi))

        ## Adding a bit of motion blur
        # Adding previous keys in previous frames to simulate past camera movement
        theta = np.random.uniform(0.0, np.pi)
        phi = np.random.uniform(0.0, 2.0 * np.pi)
        radius = 0.2 * np.random.beta(a=1, b=10)
        radialMoveVec = utils.getSphericalCoordinates(radius, theta, phi)

        # Clearing previous animations
        bpy.context.view_layer.objects.active = cam
        bpy.context.active_object.animation_data_clear()

        # Adding movement in past frames
        framesRange = range(0, 10)
        for i in framesRange:
            cam.keyframe_insert("location", frame=glob.RENDER_FRAME-i)
            cam.location += Vector(radialMoveVec)

    def shuffleCameraConfig(self, cam):
        cam.data.lens = np.random.uniform(low=self.FOCAL_LENGTH_RANGE[0], high=self.FOCAL_LENGTH_RANGE[1])

    def generateRandomRenderConfiguration(self, board, piecesSet, cam):
        ## Creating and applying a random configuration to the scene
        config = self.generateRandomPiecesPlacement(piecesSet.getStoredPiecesTypes(), board.cellsNames)
        self.applyConfigurationToBoard(config, board, piecesSet)

        self.shuffleCameraConfig(cam)
        self.positionCameraAroundBoardCenter(board, cam)

        ## Making the annotations for the currently used configuration
        annotations = {}

        annotations["config"] = config

        cornerObjs = [board.getCornerObj(cornerId) for cornerId in range(4)]
        cornerScreenPos = [bpy_extras.object_utils.world_to_camera_view(cam.users_scene[0], cam, ob.matrix_world.to_translation()) for ob in cornerObjs]
        annotations["corners"] = [(pos[0], pos[1]) for pos in cornerScreenPos]

        return annotations

