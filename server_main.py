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
                ("map", c_uint16 * 80 * 24)]


def main():
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

            buff = csock.recv(4096)
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


                time.sleep(0.1)
                key_input = input("Enter key input \n")
                while len(key_input)!=1:
                    key_input = input("Enter key input \n")
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