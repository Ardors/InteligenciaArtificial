import numpy as np
import pygad
import pygad.nn
import pygad.gann
import os
import socket
import utils
import server_main
import struct


def init_game():
    """Initialize player inventory, equipment and other things"""
    print("####################STARTING NEW INDIVUDUAL########################")
    player = utils.Player()     #starting position = (5,5) but this will be changed in the first getInputData
    inventory = []
    inventory.append(utils.Object("FOOD", "food", 1, "a"))
    inventory.append(utils.Object("ARMOR", "ring", 1, "b"))
    inventory.append(utils.Object("WEAPON", "mace", 1, "c"))
    inventory.append(utils.Object("WEAPON", "short bow", 1, "d"))
    inventory.append(utils.Object("WEAPON", "arrows", 33, "e"))          #initialize the number of arrows to 33: define this specific value in the C code
    initialFitness = 0
    return(player, {}, initialFitness)

def play_game(model, solution):#, sol_idx):
    [player, inventory, solution_fitness] = init_game()
    PORT = 2300
    server_addr = ('localhost', PORT)
    ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print("Socket created")
    try:
        # bind the server socket and listen
        ssock.bind(server_addr)
        print("Bind done")
        ssock.listen(3)
        print("Server listening on port {:d}".format(PORT))
        launch_game()
        csock, client_address = ssock.accept()
        print("Accepted connection from {:s}".format(client_address[0]))
        [Inputs, inventory, player, dungeon] = getInputData(csock, inventory)
        print(len(Inputs))
        nbCelulasAnterior = 0
        nbCelulasCurrent = 0
        [solution_fitness, nbCelulasCurrent, nbCelulasAnterior] = computeFitness(player, inventory, dungeon, nbCelulasCurrent, nbCelulasAnterior)   #computing fitness function here to initialize nCelulasCurrent
        while gameIsOn(player):
            """predictions = pygad.nn.predict(last_layer=GANN_instance.population_networks[sol_idx],
                                        data_inputs=Inputs)"""
            predictions = pygad.kerasga.predict(model=model,
                                            solution=solution,
                                            data=Inputs)
            print(len(predictions), len(predictions[0]))
            player = processPrediction(csock, predictions[0], inventory, player)                   #player armor, weapon1 and weapon2 attributes can be modified in processPrediction
            [Inputs, inventory, player, dungeon] = getInputData(csock, inventory)
            [solution_fitness, nbCelulasCurrent, nbCelulasAnterior] = computeFitness(player, inventory, dungeon, nbCelulasCurrent, nbCelulasAnterior)
    except AttributeError as ae:
        print("Error creating the socket: {}".format(ae))
    except socket.error as se:
        print("Exception on socket: {}".format(se))
    except KeyboardInterrupt:
        ssock.close()
    finally:
        print("Closing socket")
        ssock.close()
    return solution_fitness

def launch_game():
    #launch server
    cmd_line = "gnome-terminal -x bash -c \"bin/rogue; exec bash\""
    os.system(cmd_line)

def getInputData(csock, inventory):
    """outputs: viewedDungeon as a matrix of binary column vectors 
    representing: [floor(.) wall(- or |) tunnel(#) door(+) ennemy(any letter) collectible(any symbol) stairs(%)]"""
    [dungeon, player, inventory] = server_main.processDataFromGame(csock, inventory)
    print("data processed! \n")
    viewedDungeon = np.zeros((24,80,7))
    for i in range(24):
        for j in range(80):
            if dungeon[i][j] == b"a":                                    #floor
                viewedDungeon[i][j] = [1, 0, 0, 0, 0, 0, 0]
            elif (dungeon[i][j] == b")") or (dungeon[i][j] == b"1"):      #walls
                viewedDungeon[i][j] = [0, 1, 0, 0, 0, 0, 0]
            elif (dungeon[i][j] == b"&"):                                #tunnels
                viewedDungeon[i][j] = [0, 0, 1, 0, 0, 0, 0]
            elif (dungeon[i][j] == b"A"):                                #doors
                viewedDungeon[i][j] = [0, 0, 0, 1, 0, 0, 0]
            elif dungeon[i][j] in [b"c", b"$", b"B", b"C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]:      #ennemies
                viewedDungeon[i][j] = [0, 0, 0, 0, 1, 0, 0]
            elif dungeon[i][j] in ["*", b"b", "]", "!", "?", "=", "/", ":"]:     #collectibles
                viewedDungeon[i][j] = [0, 0, 0, 0, 0, 1, 0]
            elif dungeon[i][j] == b"e":                                  #stairs
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
            Subtypes = ["food", "slime-mold"]                        #I don't think fruits are displayed like this but whathever
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
        
    entradas = [player.health, player.maxHealth, player.strength, player.maxStrength, player.armor, player.weapon1, player.weapon2, player.level, player.exp, player.Xpos, player.Ypos]
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

def processPrediction(csock, predictions, inventory, player):
    action = np.argmax(predictions)#np.where(np.isclose(predictions, 1.0)) #predictions.index(1.0)
    print("action: ", action)
    if action == 0:
        server_main.sendToGame(csock, "y", "", "")
    elif action == 1:
        server_main.sendToGame(csock, "k", "", "")
    elif action == 2:
        server_main.sendToGame(csock, "u", "", "")
    elif action == 3:
        server_main.sendToGame(csock, "h", "", "")
    elif action == 4:
        server_main.sendToGame(csock, ".", "", "")
    elif action == 5:
        server_main.sendToGame(csock, "l", "", "")
    elif action == 6:
        server_main.sendToGame(csock, "b", "", "")
    elif action == 7:
        server_main.sendToGame(csock, "j", "", "")
    elif action == 8:
        server_main.sendToGame(csock, "n", "", "")
    elif action == 9:
        server_main.sendToGame(csock, "<", "", "")
    elif action == 10:
        server_main.sendToGame(csock, ">", "", "")
    elif action == 11:
        for object in inventory: 
            if object.type == "FOOD":
                if object.quantity == 1:
                    inventory.remove(object)
                server_main.sendToGame(csock, "e", object.key, "")         #Eating the first edible item
                break
            else:
                server_main.sendToGame(csock, ".", "", "")                 #In case the agent wants to eat and has no food, it rests
    elif action == 12:
        for object in inventory: 
            if object.type == "POTION":
                if object.quantity == 1:
                    inventory.remove(object)
                server_main.sendToGame(csock, "q", object.key, "")         #drinking the first potion in inventory
                break
            else:
                server_main.sendToGame(csock, ".", "", "")                #Idem, we handle the case where it tries to quaff but has no potion in inventory
    elif action == 13:
        for object in inventory: 
            if object.type == "SCROLL":
                if object.quantity == 1:
                    inventory.remove(object)
                server_main.sendToGame(csock, "r", object.key, "")
                break
            else:
                server_main.sendToGame(csock, ".", "", "") 
    elif action in range(14,22):
        for object in inventory: 
            if object.type == "WAND":
                if action == 14:                        #we send the zapping action then the direction then we indicate the item we want to zap with
                    server_main.sendToGame(csock, "z", "y", object.key)                
                elif action == 15:
                    server_main.sendToGame(csock, "z", "k", object.key)
                elif action == 16:
                    server_main.sendToGame(csock, "z", "u", object.key)
                elif action == 17:
                    server_main.sendToGame(csock, "z", "h", object.key)
                elif action == 18:
                    server_main.sendToGame(csock, "z", "l", object.key)
                elif action == 19:
                    server_main.sendToGame(csock, "z", "b", object.key)
                elif action == 20:
                    server_main.sendToGame(csock, "z", "j", object.key)
                elif action == 21:
                    server_main.sendToGame(csock, "z", "n", object.key)
                break
        server_main.sendToGame(csock, ".", "", "") 
    elif action == 22:
        if player.armor == 0:
            server_main.sendToGame(csock, ".", "", "")          #if the agent tries to do a prohibited move il passes its turn
        else:
            player.armor = 0
            server_main.sendToGame(csock, "T", "", "")                         #remove armor
    elif action == 23:
        Subtypes = ["placeholder1", "placeholder2", "leather", "ring", "scale", "chain", "banded", "splint", "plate"]
        armorPower = 0                              #I put placeholder1 and placeholder2 so that leather armor has 2 armorPower
        for object in inventory:                    #searching for the best armor to equip in the inventory. 
            if object.type == "ARMOR":
                if armorPower < Subtypes.index(object.subtype):
                    armorPower = Subtypes.index(object.subtype)
                    armorToEquip = object
        if (armorPower>0) and (player.armor!=0):                #checking that at least one armor was found in the inventory, and can't equip something if already equipped with something
            player.armor = armorPower
            server_main.sendToGame(csock, "W", armorToEquip.key, "")
        else:
            server_main.sendToGame(csock, ".", "", "")                    #resting if no armor in inventory
    elif action == 24:
        Subtypes = ["placeholder1", "placeholder2", "bow", "darts", "arrows", "daggers", "shurikens", "mace", "long", "two-handed"]
        weaponPower = 0                             #I put placeholder1 and placeholder2 so that bow has 2 weaponPower
        for object in inventory:                    #searching for the best weapon to equip in the inventory. 
            if object.type == "WEAPON":
                if weaponPower < Subtypes.index(object.subtype):
                    weaponPower = Subtypes.index(object.subtype)
                    weaponToEquip = object
        if (weaponPower>0) and (weaponPower!=player.weapon1):                #checking that at least one weapon was found in the inventory and can't equip same weapon as already equipped
            player.weapon1 = weaponPower
            player.weapon2 = weaponPower
            server_main.sendToGame(csock, "w", weaponToEquip.key, "")
        else:
            server_main.sendToGame(csock, ".", "", "")                    #in case of no ther weapon, resting
    return player

                
    
