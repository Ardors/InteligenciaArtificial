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

class Player:
  def __init__(self, health, maxHealth, strength, maxStrength, armor, weapon1, weapon2, level, exp, Xpos, Ypos, alive):
    self.health = health
    self.maxHealth = maxHealth
    self.strength = strength
    self.maxStrength = maxStrength
    self.armor = armor
    self.weapon1 = weapon1
    self.weapon2 = weapon2
    self.level = level
    self.exp = exp
    self.Xpos = Xpos
    self.Ypos = Ypos
    self.alive = alive

class Object:
    def __init__(self, type, subtype, quantity, key):
        self.type = type
        self.subtype = subtype
        self.quantity = quantity
        self.key = key