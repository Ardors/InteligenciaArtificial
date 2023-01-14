import numpy as np
import pygad
import pygad.nn
import pygad.gann


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