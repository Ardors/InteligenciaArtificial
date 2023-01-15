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
    OBJECTS = ["scroll", "potion", "armor", "mail", "wand", "staff", "food", "slime-mold", "bow", "darts", "arrows", "daggers", "shurikens", "mace", "long", "two-handed"]
    for i in text:
        if i in OBJECTS:
            return i
    return "unknown"

class Player:
  def __init__(self, health=12, maxHealth=12, strength=16, maxStrength=16, armor=3, weapon1=7, weapon2=7, level=1, exp=0, Xpos=5, Ypos=5, alive=True, celulasExploradas=1):
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
    self.celulasExploradas = celulasExploradas

class Object:
    def __init__(self, type, subtype, quantity=1, key="f"):
        self.type = type
        self.subtype = subtype
        self.quantity = quantity
        self.key = key