import numpy as np
import pygad
import pygad.nn
import pygad.gann
import os
import proc


def init_game():
    """Initialize player inventory, equipment and other things"""
    player = proc.Player(12, 12, 16, 16, 4, 1, 1, 1, 0, 5, 5, True)     #starting position = (5,5) but this will be changed in the first getInputData
    inventory = []
    inventory.append(proc.Object("FOOD", "food", 1, "a"))
    inventory.append(proc.Object("ARMOR", "ring", 1, "b"))
    inventory.append(proc.Object("WEAPON", "mace", 1, "c"))
    inventory.append(proc.Object("WEAPON", "short bow", 1, "d"))
    inventory.append(proc.Object("WEAPON", "arrows", 33, "e"))          #initialize the number of arrows to 33: define this specific value in the C code
    initialFitness = 0
    return(player, {}, initialFitness)

def play_game(model, solution):#, sol_idx):
    [player, inventory, solution_fitness] = init_game()
    launch_game()
    [Inputs, inventory, player, dungeon] = getInputData(inventory, player)
    nbCelulasAnterior = 0
    nbCelulasCurrent = 0
    [solution_fitness, nbCelulasCurrent, nbCelulasAnterior] = computeFitness(player, inventory, dungeon, nbCelulasCurrent, nbCelulasAnterior)   #computing fitness function here to initialize nCelulasCurrent
    while gameIsOn(player):
        """predictions = pygad.nn.predict(last_layer=GANN_instance.population_networks[sol_idx],
                                    data_inputs=Inputs)"""
        predictions = pygad.kerasga.predict(model=model,
                                        solution=solution,
                                        data=Inputs)
        processPrediction(predictions, inventory)
        [Inputs, inventory, player, dungeon] = getInputData(inventory, player)
        [solution_fitness, nbCelulasCurrent, nbCelulasAnterior] = computeFitness(player, inventory, dungeon, nbCelulasCurrent, nbCelulasAnterior)
    return solution_fitness

def launch_game():
    #launch server
    cmd_line = "gnome-terminal -x bash -c \"bin/rogue; exec bash\""
    os.system(cmd_line)

def getInputData(inventory, player):
    """outputs: viewedDungeon as a matrix of binary column vectors 
    representing: [floor(.) wall(- or |) tunnel(#) door(+) ennemy(any letter) collectible(any symbol) stairs(%)]"""
    [dungeon, player, inventory] = getDataFromGame(inventory)
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
    #inventory = getInventory()                                  #inventory = list of object types with fields: type(str), subtype(str), quantity(int), key(str)
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
        item+=1
        
        entradas = [player.health, player.maxHealth, player.strength, player.maxStrength, player.armor, player.weapon1, player.weapon2, player.level, player.exp, player.Xpos, player.yPos]
        for i in range(24):
            for j in range(80):
                for k in range(7):
                    entradas.append(viewedDungeon[i][j][k])
        for i in range(24):
            for j in range(21):
                entradas.append(inputInventory[i][j])
        
        return [entradas, inventory, player, dungeon]


def gameIsOn(player):
    return player.alive

def computeFitness(player, inventory, dungeon, nbCelulasCurrent, nbCelulasAnterior):
    """Calcula la fitness del individuo en function de: 
    - el nivel de la mazmorra
    - la vida del player
    - la fuerza del player
    - la experiencia del player
    - la potencia de su arma equipada
    - la potencia de su armadura
    - el numero de objetos que tiene en su inventario
    - el numero de celdillas exploradas desde el principio del juego.
    Pesos de cada elemento a ajustar de manera empirica. """
    nivelMazmorra = player.level
    vida = player.health
    fuerza = player.strength
    experiencia = player.exp
    scoreArma = player.weapon1
    scoreArmadura = player.armor
    objetos = len(inventory) - 5        #player starts with 5 objects in inventory
    counter = 0                         #contador de celdillas descubiertas
    for i in range(24):
        for j in range(80):
            if dungeon[i][j] != " ":
                counter+=1
    if nbCelulasCurrent > counter:                                      #Queremos utilizar el numero TOTAL de celulas descubiertas, no solo las del nivel actual
        nbCelulasAnterior = nbCelulasAnterior + nbCelulasCurrent
    nbCelulasCurrent = counter
    nbCelulasTotal = nbCelulasAnterior + nbCelulasCurrent
    muerto = not(player.alive)
    fitness = 3*vida + fuerza + 2*objetos + experiencia + scoreArma + scoreArmadura + nbCelulasTotal + 100*(nivelMazmorra-1) - 1000*muerto      #alomejor no hay que usar el bool de muerto sino usar una funcion divergente negativa cuando la vida se acerca de 0 (0.2*vidaMax - vidaMax/vida por ejemplo)
    return [fitness, nbCelulasCurrent, nbCelulasAnterior]

def processPrediction(predictions, inventory):
    action = predictions.index(1.0)
    if action == 0:
        sendToGame("y", "")
    elif action == 1:
        sendToGame("k", "")
    elif action == 2:
        sendToGame("u", "")
    elif action == 3:
        sendToGame("h", "")
    elif action == 4:
        sendToGame(".", "")
    elif action == 5:
        sendToGame("l", "")
    elif action == 6:
        sendToGame("b", "")
    elif action == 7:
        sendToGame("j", "")
    elif action == 8:
        sendToGame("n", "")
    elif action == 9:
        sendToGame("<", "")
    elif action == 10:
        sendToGame(">", "")
    elif action == 11:
        for object in inventory: 
            if object.type == "FOOD":
                sendToGame("e", object.key)         #Eating the first edible item
                break
            else:
                sendToGame("e", "a")                #In case the agent wants to eat and has no food, it tries to eat object a
    elif action == 12:
        for object in inventory: 
            if object.type == "POTION":
                sendToGame("q", object.key)         #drinking the first potion in inventory
                break
            else:
                sendToGame("q", "a")                #Idem, we handle the case where it tries to quaff but has no potion in inventory
    elif action == 13:
        for object in inventory: 
            if object.type == "SCROLL":
                sendToGame("r", object.key)
                break
            else:
                sendToGame("r", "a") 
    elif action in range(14,22):
        for object in inventory: 
            if object.type == "WAND":
                sendToGame("z", object.key)         #we send the zapping action and the wand to use
                if action == 14:
                    sendToGame("y", "")             #The game then prompts inwhich direction we wantto use the wand
                elif action == 15:
                    sendToGame("k", "")
                elif action == 16:
                    sendToGame("u", "")
                elif action == 17:
                    sendToGame("h", "")
                elif action == 18:
                    sendToGame("l", "")
                elif action == 19:
                    sendToGame("b", "")
                elif action == 20:
                    sendToGame("j", "")
                elif action == 21:
                    sendToGame("n", "")
                break
            else:
                sendToGame("z", "a") 
    elif action == 22:
        sendToGame("T", "")                         #remove armor
    elif action == 23:
        Subtypes = ["leather", "ring", "scale", "chain", "banded", "splint", "plate"]
        armorPower = 0
        for object in inventory:                    #searching for the best armor to equip in the inventory. 
            if object.type == "ARMOR":
                if armorPower < Subtypes.index(object.subtype):
                    armorPower = Subtypes.index(object.subtype)
                    armorToEquip = object
        if armorPower>0:                            #checking that at least one armor was found in the inventory
            sendToGame("W", armorToEquip.key)
        else:
            sendToGame("W", "a")                    #trying to equip the firts item if no armor in inventory
    elif action == 24:
        Subtypes = ["short bow", "darts", "arrows", "daggers", "shurikens", "mace", "long sword", "two-handed sword"]
        weaponPower = 0
        for object in inventory:                    #searching for the best armor to equip in the inventory. 
            if object.type == "ARMOR":
                if weaponPower < Subtypes.index(object.subtype):
                    weaponPower = Subtypes.index(object.subtype)
                    armorToEquip = object
        if weaponPower>0:                            #checking that at least one armor was found in the inventory
            sendToGame("w", armorToEquip.key)
        else:
            sendToGame("w", "c")                    #in case of no ther weapon, try to equip the c) object (should never happen as the player will never drop his mace in the c key)

                
    
