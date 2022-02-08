from email.mime import base
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import json

T_WIDTH = 416
T_HEIGHT = 416

basedir = "."
inputFolder = os.path.join(basedir, "data")
outputfolder = os.path.join(basedir, "test")
print(inputFolder)

def getSegmentsIntersection(a1, a2, b1, b2):
    """
    Computes the intersection of two segments : returns the intersection point if it exists, and None otherwise
    """
    a = a2 - a1
    b = b2 - b1
    o = a1 - b1
    aLenSq = np.dot(a, a)
    aDotB = np.dot(a, b)
    denom = (aLenSq * np.dot(b, b)) - aDotB**2.0

    if denom == 0.0:
        # The segment are parallel, no unique intersection exists
        return None

    u = ((aLenSq * np.dot(b, o)) - (aDotB * np.dot(a, o))) / denom

    if u < 0.0 or u > 1.0:
        # The potential intersection point is not situated on the segment, aborting
        return None

    t = np.dot(a, u * b - o) / aLenSq
    aPoint = a1 + t * a
    bPoint = b1 + u * b

    return aPoint if (np.linalg.norm(np.round(aPoint - bPoint), 5) == 0.0) else None

def getUnprojectedGameBoardFromImg(img_, boardCornersRel, growthFactor = 0.0):
    # Growing the board zone to get a better look at the pieces
    O = getSegmentsIntersection(boardCornersRel[0], boardCornersRel[3], boardCornersRel[1], boardCornersRel[2])
    for i in range(4):
        boardCornersRel[i] = growthFactor * (boardCornersRel[i] - O) + boardCornersRel[i]

    cornersAbs = np.round(boardCornersRel * (np.array(img.shape)[0:2] - np.array([1.0, 1.0])))

    outCoords = np.array([
        [T_HEIGHT-1, 0.0],
        [T_HEIGHT-1, T_WIDTH-1],
        [0.0, 0.0],
        [0.0, T_WIDTH-1],
    ])

    inCoords = np.float32(cornersAbs)
    outCoords = np.float32(outCoords)
    M = cv2.getPerspectiveTransform(inCoords, outCoords)

    return cv2.warpPerspective(img_, M, (T_WIDTH, T_HEIGHT),flags=cv2.INTER_LINEAR)

from progress.bar import Bar

numIts = 1938
bar = Bar("Treating image #", max = numIts)
for dataNum in range(numIts):
    imgPath = os.path.join(inputFolder, "{}.jpg".format(dataNum))
    annotationsPath = os.path.join(inputFolder, "{}.json".format(dataNum))

    annotations = json.load(open(annotationsPath, "r"))

    img = cv2.imread(imgPath)

    # Getting the annotated board corners
    cornersRel = np.array(annotations["corners"])
    # Adapting them to the coordinate space in cv2
    cornersRel = np.column_stack((cornersRel[:,0], 1.0 - cornersRel[:,1]))

    out = getUnprojectedGameBoardFromImg(img, cornersRel, 0.1)
    cv2.imwrite(os.path.join(outputfolder, "{}_unwrapped.jpg".format(dataNum)),  out)
    #plt.imshow(out)
    #plt.show()
    bar.next()