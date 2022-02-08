import warnings
import bpy
import re
import numpy as np

"""
Library collecting general utils in math or Blender API that are used frequently throughout the code but aren't tied to a specific task
"""

def setSelectOfObjectAndChildren(obj, selectState):
    """
    Sets a node and its hierarchy to a given selectState (True or False)
    """
    obj.select_set(selectState)
    
    for child in obj.children:
        setSelectOfObjectAndChildren(child, selectState)

def setNewParent(obj, newParent, keep_transform=False):
    bpy.ops.object.select_all(action='DESELECT')

    obj.select_set(True)
    newParent.select_set(True)
    bpy.context.view_layer.objects.active = newParent

    bpy.ops.object.parent_set(keep_transform=keep_transform)

def getChildrenWithNameContaning(parent, stringToSearch):
    """
    Returns all children of an objects whose names contain a user-provided string
    """
    return [child for child in parent.children if (re.search(stringToSearch, child.name) != None)]

def getChildWithNameContaining(parent, stringToSearch):
    """
    Returns a child whose name contains a given string, and None if no such child exist/more than one exists
    """
    foundChildren = getChildrenWithNameContaning(parent, stringToSearch)
        
    if len(foundChildren) == 0:
        #No child has the name
        #warnings.warn("No child of '{}' with name containing '{}' found.".format(parent.name, stringToSearch))
        return None
    elif len(foundChildren) == 1:
        #We found exactly one child with this name
        return foundChildren[0]
    else:
        #More than one child with this name was found
        #warnings.warn("More than one child of '{}' with name containing '{}' found.".format(parent.name, stringToSearch))
        return None

def selectObjAndHierarchy(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)

def deleteObjAndHierarchy(obj):
    bpy.ops.object.select_all(action='DESELECT')
    selectObjAndHierarchy(obj)
    bpy.ops.object.delete()

def duplicateObjectAndHierarchy(obj, linked=False):
    # Selecting only the object and its hiearchy, and duplicating it
    bpy.ops.object.select_all(action='DESELECT')
    selectObjAndHierarchy(obj)
    bpy.ops.object.duplicate(linked=True)

    # Returning the duplicate root object, that is the one sharing the same data as the original root object
    dupObj = None
    dupObjsData = [ob.data for ob in bpy.context.selected_objects]
    if not obj.data in dupObjsData:
        raise Exception("For some reason, no duplicate object carries the original data. Check if objects were properly selected or if the duplication was set to 'Linked'.")

    dupObj = bpy.context.selected_objects[dupObjsData.index(obj.data)]

    # If the user specified for the duplicate not to be linked, we make its properties local
    if not linked:
        bpy.ops.object.make_single_user(object=True, obdata=True, material=True, animation=True, obdata_animation=True)

    return dupObj

def getSphericalCoordinates(radius : float, theta : float, phi : float):
    return radius * np.array([np.cos(phi) * np.sin(theta), np.sin(phi) * np.sin(theta), np.cos(theta)])

def lookAtFromPos(targetPos, lookPos, upVector = np.array([0.0, 0.0, 1.0])):
    """
    Returns the transform to apply to an object so that it looks towards targetPos, from a given position lookPos and with a given up vector upVector
    :param nparray targetPos: Position to which to look
    :param nparray lookPos: Position from which to look
    :param nparray upVector: The world up vector
    """
    zAxis = targetPos - lookPos
    zAxis = zAxis / np.linalg.norm(zAxis)

    yAxis = None
    usedUpVec = np.array(upVector)
    if abs(np.dot(zAxis, usedUpVec)) == 1.0:
        #If the zAxis and up vector share the same direction, we find an arbitrary yAxis orthogonal to zAxis
        yAxis = np.array([zAxis[1], -zAxis[0], 0.0]) if (zAxis[1] != 0.0 or zAxis[0] != 0.0) else np.array([zAxis[2], 0.0, -zAxis[0]])
    else:
        yAxis = np.cross(zAxis, usedUpVec)
        yAxis = yAxis / np.linalg.norm(yAxis)

    xAxis = np.cross(zAxis, yAxis)
    xAxis = xAxis / np.linalg.norm(xAxis)

    transform = np.concatenate([yAxis, -xAxis, -zAxis, lookPos]).reshape((4, 3)).T
    transform = np.concatenate([transform, np.array([[0.0, 0.0, 0.0, 1.0]])])
    
    return transform.T