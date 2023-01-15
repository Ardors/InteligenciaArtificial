""" utils.py - Definition of useful functions or classes
"""

class InventObject:
    def __init__(self, type, value1, value2):
        self.type = type
        self.value1 = value1
        self.value2 = value2

    def __str__(self):
        return f"{self.type}, {self.value1}, {self.value2} \n"



def getType(text):
    """Get the type of the new object (scroll, potion, armor, ...)"""
    OBJECTS = ["scroll", "potion", "armor", "mail", "wand", "ring"]
    for i in text:
        if i in OBJECTS:
            return i
    return "unknown"