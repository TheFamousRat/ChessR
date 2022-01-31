import bpy
import re
import numpy as np

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

def lookAtFromPos(targetPos, lookPos, upVector):
    """
    Returns the transform to apply to an object so that it looks towards targetPos, from a given position lookPos and with a given up vector upVector
    :param nparray targetPos: Position to which to look
    :param nparray lookPos: Position from which to look
    :param nparray upVector: The world up vector
    """
    zAxis = targetPos - lookPos
    zAxis = zAxis / np.linalg.norm(zAxis)

    yAxis = np.cross(zAxis, np.array(upVector))
    yAxis = yAxis / np.linalg.norm(yAxis)

    xAxis = np.cross(zAxis, yAxis)
    xAxis = xAxis / np.linalg.norm(xAxis)

    transform = np.concatenate([yAxis, -xAxis, -zAxis, camPos]).reshape((4, 3)).T
    transform = np.concatenate([transform, np.array([[0.0, 0.0, 0.0, 1.0]])])
    
    return transform.T

def checkForNonEmptyCollection(collectionName):
    """
    Checks whether a collection with a given name exists and has more than 0 objects
    """
    return (False if (not collectionName in bpy.data.collections) else (len(bpy.data.collections[collectionName].all_objects) > 0))

def getNonEmptyCollection(collectionName):
    if checkForNonEmptyCollection(collectionName):
        return bpy.data.collections[collectionName]
    else:
        raise Exception("No non-empty collection named '{}' found.".format(collectionName))