import re

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