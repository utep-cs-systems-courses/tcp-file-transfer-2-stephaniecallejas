#! /usr/bin/env python3

"""Lab 2 File Transfer
   Stephanie Callejas
   This lab assignment was created with the use of demos provided by the professors. 
   The lab involves a client and a server which communicated to each other to transfer files.
   In the first implementation the connection of multiple clients to a server was done by using 
   forking. In the second part Threads were introduced and the notion of Locks. Locks help to 
   avoid transferring files to the same place at the same time, which could cause errors. The
   lab also allows the use of a proxy to communicate between the client and the server as a 
   middle-man. The lab was done in collaboration with Zabdi Valenciana 
"""

import sys, os
sys.path.append("../lib")       # for params
import re, socket, params
from os.path import exists

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)


from framedSock import framedSend, framedReceive

while True:

    sock, addr = lsock.accept()
    print("connection rec'd from", addr)
    if not os.fork():
        
        payload = framedReceive(sock, debug)    #Receive name of the file to be saved as
        if not payload:
            break
        payload = payload.decode()
        if exists(payload):
            framedSend(sock, b"True", debug)   #If file already exists, return true
        else:
            framedSend(sock, b"False", debug)  #False otherwise
            try:
                payload2 = framedReceive(sock, debug)  #If false, receive the file data
            except:
                print("connection lost while receiving.")
                sys.exit(0)
            if not payload2:
                break
            try:
                framedSend(sock, payload2, debug)
            except:
                print("------------------------------")
                print("connection lost while sending.")
                print("------------------------------")

            output = open(payload, 'wb')
            output.write(payload2)       #Write byte array, will be converted to string
        sock.close()
                
                #When connection from client is cut off quickly, server will print the file content