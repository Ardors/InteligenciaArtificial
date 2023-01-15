#!/usr/bin/env python3

""" server.py - Echo server for sending/receiving C-like structs via socket
References:
- Ctypes: https://docs.python.org/3/library/ctypes.html
- Sockets: https://docs.python.org/3/library/socket.html
"""

import socket
import sys
import random
from ctypes import *
import time
import utils
import numpy as np


""" This class defines a C-like struct """
class Payload(Structure):
    _fields_ = [("gold", c_uint32),
                ("current_health", c_uint32),
                ("max_health", c_uint32),
                ("current_exp", c_uint32),
                ("exp_level", c_uint32),
                ("current_strength", c_uint32),
                ("max_strength", c_uint32),
                ("pos_x", c_uint8),
                ("pos_y", c_uint8),
                ("dungeon_level", c_uint16),
                ("map", c_uint16 * 80 * 24),
                ("need_ack", c_int),
                ("alive", c_uint32),
                ("pickUp_message", (c_char*230))]



def processDataFromGame(ssock, inventory):
    dungeon = np.zeros((24,80))
    player = utils.Player()
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x'] 
    csock, client_address = ssock.accept()
    print("Accepted connection from {:s}".format(client_address[0]))

    buff = csock.recv(8192)
    while buff:
        #print("\nReceived {:d} bytes".format(len(buff)))
        payload_in = Payload.from_buffer_copy(buff)
        """print("Data read: gold={:d}, current health={:d}, max health={:d}, current exp={:d}, current level={:d}, current strength={:d}, max strength={:d}, pos_x={:d}, pos_y={:d}, dungeon_level={:d}".format(
        payload_in.gold,
        payload_in.current_health,
        payload_in.max_health,
        payload_in.current_exp,
        payload_in.exp_level,
        payload_in.current_strength,
        payload_in.max_strength,
        payload_in.pos_x,
        payload_in.pos_y,
        payload_in.dungeon_level))"""
        
        indCol, indLin = 0, 0
        for col in payload_in.map:
            for val in col:
                #print ("{:c}".format(val+33), end = '')
                dungeon[indLin, indCol] = "{:c}".format(val+33)
                indCol += 1
            #print(" ")
            indLin +=1
        
        player.health = payload_in.current_health                   #armor, weapon1 and weapon2 are asignated when the player decides to equip/unequip items
        player.maxHealth = payload_in.max_health
        player.strength = payload_in.max_strength
        player.maxStrength = payload_in.max_strength
        player.level = payload_in.dungeon_level
        player.Xpos = payload_in.pos_x
        player.Ypos = payload_in.pos_y
        player.alive = payload_in.alive

                                                
        if str(payload_in.pickUp_message) != "b'nothing'":
            message = str(payload_in.pickUp_message)[2:-1]
            text = message.split(" ")
            if "gold." not in text:
                objType = utils.getType(text)
                dontClassify = False
                ObjToClassify = utils.Object("PLACEHOLDER", "PLACESUBTYPE")
                print(text)
                if objType == "scroll":
                    ObjToClassify = utils.Object("SCROLL", text[-2], 1)   #a scroll is defined by the inscription on it
                elif objType == "potion":
                    ObjToClassify = utils.Object("POTION", text[1], 1)           #a Potion is only defined by its colour
                elif (objType == "armor") or  (objType == "mail"):
                    ObjToClassify = utils.Object("ARMOR", text[0], 1)
                elif objType in ["bow", "darts", "arrows", "daggers", "shurikens", "mace", "long", "two-handed"]:
                    ObjToClassify = utils.Object("WEAPON", objType, 1)
                elif (objType == "food") or (objType == "slime-mold"):
                    if text[0] == "Some" or (objType == "slime-mold"):
                        ObjToClassify = utils.Object("FOOD", objType, 1)
                    else:
                        ObjToClassify = utils.Object("FOOD", objType, text[0])
                elif (objType == "wand") or (objType == "staff"):
                    ObjToClassify = utils.Object("WAND", text[1], 1)
                elif (objType == "unknown"):
                    dontClassify = True
                if not(dontClassify):
                    classified = False
                    print("type: ", ObjToClassify.type, " subtype: ", ObjToClassify.subtype)
                    for obj in inventory:
                        if (obj.type == ObjToClassify.type) and (obj.subtype == ObjToClassify.subtype):             #check if this item already exists in inventory
                            obj.quantity += ObjToClassify.quantity
                            classified = True
                            break
                    if not(classified):                                                                                 #try to assign the object to the first available key
                        assignedKeys = []
                        for obj in inventory:
                            assignedKeys.append(obj.key)
                        for letter in letters:
                            if letter not in assignedKeys:
                                ObjToClassify.key = letter
                                inventory.append(ObjToClassify)
                                classified = True
                                break
                    if not(classified):                                                                                 #if the object is still not classified, it means that the inventory is full. 
                        pass                                                                                            #we should never get there because a full inventory displays a message that does not contains key-subtypes words
        for i in inventory:
            print(i.type, i.subtype, i.quantity, i.key, "\n")
        time.sleep(0.1)
        if payload_in.need_ack == 1:
            key_input = " "
            print("Sending blank space \n")
            key_input = key_input.encode('ascii')
            nsent = csock.send(key_input)
            buff = csock.recv(512)
    
    return [csock, dungeon, player, inventory]

    """print("Closing connection to client")           #put this in the sendActionToGame function
    print("----------------------------")
    csock.close()"""

def sendToGame(csock, act1, act2, act3):
    key_input1 = act1.encode('ascii')
    nsent = csock.send(key_input1)
    buff = csock.recv(512)
    if act2 !="":
        key_input2 = act2.encode('ascii')
        nsent = csock.send(key_input2)
        buff = csock.recv(512)
        if act3 !="":
            key_input3 = act3.encode('ascii')
            nsent = csock.send(key_input3)
            buff = csock.recv(512)
    csock.close()

def main():
    inventory = []
    print("_____________________________________________________________##########################aaaaaaaaaaaaaaaaaaaaooooooooooooooo")
    inventory.append(utils.Object("FOOD", "food", 1, "a"))
    inventory.append(utils.Object("ARMOR", "ring", 1, "b"))
    inventory.append(utils.Object("WEAPON", "mace", 1, "c"))
    inventory.append(utils.Object("WEAPON", "short bow", 1, "d"))
    inventory.append(utils.Object("WEAPON", "arrows", 33, "e"))
    letters = ['f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x'] 
    PORT = 2300
    server_addr = ('localhost', PORT)
    ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")

    try:
        # bind the server socket and listen
        ssock.bind(server_addr)
        print("Bind done")
        ssock.listen(3)
        print("Server listening on port {:d}".format(PORT))

        while True:
            csock, client_address = ssock.accept()
            print("Accepted connection from {:s}".format(client_address[0]))

            buff = csock.recv(8192)
            while buff:
                print("\nReceived {:d} bytes".format(len(buff)))
                payload_in = Payload.from_buffer_copy(buff)
                print("Data read: gold={:d}, current health={:d}, max health={:d}, current exp={:d}, current level={:d}, current strength={:d}, max strength={:d}, pos_x={:d}, pos_y={:d}, dungeon_level={:d}, player_alive={:d}".format(
                payload_in.gold,
                payload_in.current_health,
                payload_in.max_health,
                payload_in.current_exp,
                payload_in.exp_level,
                payload_in.current_strength,
                payload_in.max_strength,
                payload_in.pos_x,
                payload_in.pos_y,
                payload_in.dungeon_level,
                payload_in.alive))

                for col in payload_in.map:
                    for val in col:
                        print ("{:c}".format(val+33), end = '')
                    print(" ")


                                                        
                if str(payload_in.pickUp_message) != "b'nothing'":
                    message = str(payload_in.pickUp_message)[2:-1]
                    text = message.split(" ")
                    if "gold." not in text:
                        objType = utils.getType(text)
                        dontClassify = False
                        ObjToClassify = utils.Object("PLACEHOLDER", "PLACESUBTYPE")
                        print(text)
                        if objType == "scroll":
                            ObjToClassify = utils.Object("SCROLL", text[-2], 1)   #a scroll is defined by the inscription on it
                        elif objType == "potion":
                            ObjToClassify = utils.Object("POTION", text[1], 1)           #a Potion is only defined by its colour
                        elif (objType == "armor") or  (objType == "mail"):
                            ObjToClassify = utils.Object("ARMOR", text[0], 1)
                        elif objType in ["bow", "darts", "arrows", "daggers", "shurikens", "mace", "long", "two-handed"]:
                            ObjToClassify = utils.Object("WEAPON", objType, 1)
                        elif (objType == "food") or (objType == "slime-mold"):
                            if text[0] == "Some" or (objType == "slime-mold"):
                                ObjToClassify = utils.Object("FOOD", objType, 1)
                            else:
                                ObjToClassify = utils.Object("FOOD", objType, text[0])
                        elif (objType == "wand") or (objType == "staff"):
                            ObjToClassify = utils.Object("WAND", text[1], 1)
                        elif (objType == "unknown"):
                            dontClassify = True
                        if not(dontClassify):
                            classified = False
                            print("type: ", ObjToClassify.type, " subtype: ", ObjToClassify.subtype)
                            for obj in inventory:
                                if (obj.type == ObjToClassify.type) and (obj.subtype == ObjToClassify.subtype):             #check if this item already exists in inventory
                                    obj.quantity += ObjToClassify.quantity
                                    classified = True
                                    break
                            if not(classified):                                                                                 #try to assign the object to the first available key
                                assignedKeys = []
                                for obj in inventory:
                                    assignedKeys.append(obj.key)
                                for letter in letters:
                                    if letter not in assignedKeys:
                                        ObjToClassify.key = letter
                                        inventory.append(ObjToClassify)
                                        classified = True
                                        break
                            if not(classified):                                                                                 #if the object is still not classified, it means that the inventory is full. 
                                pass                                                                                            #we should never get there because a full inventory displays a message that does not contains key-subtypes words
                for i in inventory:
                    print(i.type, i.subtype, i.quantity, i.key, "\n")
                time.sleep(0.1)
                if payload_in.need_ack == 0:
                    key_input = input("Enter key input \n")
                    while len(key_input)!=1:
                        key_input = input("Enter key input \n")
                else:
                    key_input = " "
                    print("Sending blank space \n")
                key_input = key_input.encode('ascii')
                nsent = csock.send(key_input)
                buff = csock.recv(512)

            print("Closing connection to client")
            print("----------------------------")
            csock.close()

    except AttributeError as ae:
        print("Error creating the socket: {}".format(ae))
    except socket.error as se:
        print("Exception on socket: {}".format(se))
    except KeyboardInterrupt:
        ssock.close()
    finally:
        print("Closing socket")
        ssock.close()


def main_backupu():
    inventory = {}
    letters = ['f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x'] 
    PORT = 2300
    server_addr = ('localhost', PORT)
    ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")

    try:
        # bind the server socket and listen
        ssock.bind(server_addr)
        print("Bind done")
        ssock.listen(3)
        print("Server listening on port {:d}".format(PORT))

        while True:
            csock, client_address = ssock.accept()
            print("Accepted connection from {:s}".format(client_address[0]))

            buff = csock.recv(8192)
            while buff:
                print("\nReceived {:d} bytes".format(len(buff)))
                payload_in = Payload.from_buffer_copy(buff)
                print("Data read: gold={:d}, current health={:d}, max health={:d}, current exp={:d}, current level={:d}, current strength={:d}, max strength={:d}, pos_x={:d}, pos_y={:d}, dungeon_level={:d}".format(
                payload_in.gold,
                payload_in.current_health,
                payload_in.max_health,
                payload_in.current_exp,
                payload_in.exp_level,
                payload_in.current_strength,
                payload_in.max_strength,
                payload_in.pos_x,
                payload_in.pos_y,
                payload_in.dungeon_level))

                for col in payload_in.map:
                    for val in col:
                        print ("{:c}".format(val+33), end = '')
                    print(" ");


                                                        
                if str(payload_in.pickUp_message) != "b'nothing'":
                    message = str(payload_in.pickUp_message)[2:-1]
                    text = message.split(" ")
                    if "gold." not in text:
                        objType = utils.getType(text)
                        l = len(inventory)
                        if objType == "scroll":
                            addToInventory = utils.InventObject("scroll", text[-2], text[-1])   #a scroll is defined by the inscription on it
                        elif objType == "potion":
                            addToInventory = utils.InventObject("potion", text[1], 0)           #a Potion is only defined by its colour
                        else:
                            addToInventory = text
                        inventory[letters[l]] = addToInventory
                for i in inventory:
                    print(i, inventory[i])
                time.sleep(0.1)
                if payload_in.need_ack == 0:
                    key_input = input("Enter key input \n")
                    while len(key_input)!=1:
                        key_input = input("Enter key input \n")
                else:
                    key_input = " "
                    print("Sending blank space \n")
                key_input = key_input.encode('ascii')
                nsent = csock.send(key_input)
                buff = csock.recv(512)

            print("Closing connection to client")
            print("----------------------------")
            csock.close()

    except AttributeError as ae:
        print("Error creating the socket: {}".format(ae))
    except socket.error as se:
        print("Exception on socket: {}".format(se))
    except KeyboardInterrupt:
        ssock.close()
    finally:
        print("Closing socket")
        ssock.close()


if __name__ == "__main__":
    main()