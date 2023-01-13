import numpy as np
import pygad
import pygad.nn
import pygad.gann
import subprocess
import os


def init_game():
    """Initialize player inventory, equipment and other things"""
    initialFitness = 0
    return({}, {}, initialFitness)

def play_game(GANN_instance, solution, sol_idx):
    [player, inventory, solution_fitness] = init_game()
    launch_game()
    [Inputs, inventory, player] = getInputData()
    while gameIsOn(player):
        predictions = pygad.nn.predict(last_layer=GANN_instance.population_networks[sol_idx],
                                    data_inputs=Inputs)
        sendPredictionToGame(predictions)
        [Inputs, inventory, player] = getInputData()
        solution_fitness = updateFitness(solution_fitness, Inputs)
    return solution_fitness

def launch_game():
    #launch server
    cmd_line = "gnome-terminal -x bash -c \"bin/rogue; exec bash\""
    os.system(cmd_line)

def getInputData():
    """outputs: viewedDungeon as a matrix of binary column vectors 
    representing: [floor(.) wall(- or |) tunnel(#) door(+) ennemy(any letter) collectible(any symbol) stairs(%)]"""
    dungeon, player = getDataFromGame()
    viewedDungeon = np.zeros((24,80,7))
    for i in range(24):
        for j in range(80):
            if dungeon[i][j] == ".":
                viewedDungeon[i][j] = [1, 0, 0, 0, 0, 0, 0]
            elif (dungeon[i][j] == "-") or (dungeon[i][j] == "|"):
                viewedDungeon[i][j] = [0, 1, 0, 0, 0, 0, 0]
            elif (dungeon[i][j] == "#"):
                viewedDungeon[i][j] = [0, 0, 1, 0, 0, 0, 0]
            elif (dungeon[i][j] == "+"):
                viewedDungeon[i][j] = [0, 0, 0, 1, 0, 0, 0]
            elif dungeon[i][j] in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]:
                viewedDungeon[i][j] = [0, 0, 0, 0, 1, 0, 0]
            elif dungeon[i][j] in ["*", ")", "]", "!", "?", "=", "/", ":"]:
                viewedDungeon[i][j] = [0, 0, 0, 0, 0, 1, 0]
            elif dungeon[i][j] == "%":
                viewedDungeon[i][j] = [0, 0, 0, 0, 0, 0, 1]
            else:
                viewedDungeon[i][j] = [0, 0, 0, 0, 0, 0, 0]
    inventory = getInventory()                                  #inventory = list of object types with fields: type(str), subtype(str), quantity(int)
    inputInventory = np.zeros((24,21))                          #24 slots in inventory and 20 = 6(objects types) + 14(object subtypes) + 1(quantity)
    item = 0
    for object in inventory: 
        if object.type == "ARMOR":
            inputInventory[item][0] = 1                         #[1,0,0,0,0,0]
            Subtypes = ["leather", "ring", "scale", "chain", "banded", "splint", "plate"]
            subtypeIndex = Subtypes.index(object.subtype)
            inputInventory[item][6 + subtypeIndex] = 1          #[0,0,1,0,0,0,0,0,0,0,0,0,0] in case of scale mail for example (there are 13 different subtypes)
            inputInventory[item][-1] = object.quantity          #expected to be 1 in case of armor
        elif object.type == "WEAPON":
            inputInventory[item][1] = 1                         #[0,1,0,0,0,0]
            Subtypes = ["short bow", "darts", "arrows", "daggers", "shurikens", "mace", "long sword", "two-handed sword"]
            subtypeIndex = Subtypes.index(object.subtype)
            inputInventory[item][6 + subtypeIndex] = 1
            inputInventory[item][-1] = object.quantity          #expected to be 1 in case of weapon
        elif object.type == "SCROLL":
            inputInventory[item][2] = 1                         #[0,0,1,0,0,0]
            Subtypes = ["blech", "foo", "barf", "rech", "bar", "quo", "bloto", "woh", "caca", "blorp", "erp", "festr"]  #program may crash if subtype is not in this list
            subtypeIndex = Subtypes.index(object.subtype)
            inputInventory[item][6 + subtypeIndex] = 1
            inputInventory[item][-1] = object.quantity
        elif object.type == "POTION":
            inputInventory[item][3] = 1                         #[0,0,0,1,0,0]
            Subtypes = ["blue", "red", "green", "grey", "brown", "clear", "pink", "white", "purple", "black", "yellow", "plaid", "burgundy", "beige"]
            subtypeIndex = Subtypes.index(object.subtype)
            inputInventory[item][6 + subtypeIndex] = 1
            inputInventory[item][-1] = object.quantity
        elif object.type == "FOOD":
            inputInventory[item][4] = 1                         #[0,0,0,0,1,0]
            Subtypes = ["food", "fruit"]                        #I don't think fruits are displayed like this but whathever
            subtypeIndex = Subtypes.index(object.subtype)
            inputInventory[item][6 + subtypeIndex] = 1
            inputInventory[item][-1] = object.quantity
        elif object.type == "WAND":
            inputInventory[item][5] = 1                         #[0,0,0,0,0,1]
            Subtypes = ["steel", "bronze", "gold", "silver", "copper", "nickel", "cobalt", "tin", "iron", "magnesium"]
            subtypeIndex = Subtypes.index(object.subtype)
            inputInventory[item][6 + subtypeIndex] = 1
            inputInventory[item][-1] = object.quantity
        item = item + 1
        
        entradas = [player.health, player.maxHealth, player.strength, player.maxStrength, player.armor, player.weapon1, player.weapon2, player.level, player.exp, player.Xpos, player.yPos]
        for i in range(25):
            for j in range(81):
                for k in range(7):
                    entradas.append(viewedDungeon[i][j][k])
        for i in range(24):
            for j in range(21):
                entradas.append(inputInventory[i][j])
        
        return [entradas, inventory, player]


def gameIsOn(player):
    return player.alive