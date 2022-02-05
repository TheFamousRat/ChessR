import numpy as np

class BoardImagesGenerator:
    """
    Class focusing on randomly generating and rendering plausible images of Board game scenarios
    """
    def __init__(self) -> None:
        self.imagesWidth = 640 #Width and height of output images
        self.imagesHeight = 640 
        self.emptyCellProb = 0.5 #Probability of a cell being empty when generating a scenario

    def generateScenario(self, piecesTypes, cellsNames):
        """
        Generates a random scenario for the board, that is assigns every cell to a randomly selected piece or to nothing
        """
        # Possible outputs for each cell : a piece type, or None
        piecesTypesWithNone = piecesTypes + [None]
        # Weights associated with the possible outputs
        weights = ([(1.0 - self.emptyCellProb)/len(piecesTypes)] * len(piecesTypes)) + [self.emptyCellProb]
        # Picking random values, and associating them with their cell to create a scenario
        pickedCells = np.random.choice(piecesTypesWithNone, len(cellsNames), p=weights)
        cellsOccupancy = {cellsNames[i] : pickedCells[i] for i in range(len(cellsNames))}

        return cellsOccupancy