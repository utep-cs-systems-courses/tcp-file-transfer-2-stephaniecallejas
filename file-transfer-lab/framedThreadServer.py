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
import sys
sys.path.append("../lib")       # for params
import re, socket, params, os
from os.path import exists
from threading import Thread, enumerate, Lock 
from time import time, sleep 

global dictionary   #Setting up needed variables
global dictLock
dictLock = Lock()
dictionary = dict()

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

from threading import Thread;
from encapFramedSock import EncapFramedSock

class Server(Thread):
    def __init__(self, sockAddr):
        Thread.__init__(self)
        self.sock, self.addr = sockAddr
        self.fsock = EncapFramedSock(sockAddr)
    def run(self):
        global dictionary, dictLock
        print("new thread handling connection from", self.addr)
        payload = self.fsock.receive(debug) #receive file name to be saved
        if debug: print("rec'd: ", payload)
        if not payload:     # done
            if debug: print(f"thread connected to {addr} done")
            self.fsock.close() #possible error
            return          # exit
        payload = payload.decode()     #receive byte array of name to be saved and convert to string 
        if exists(payload):
            self.fsock.send(b"True", debug)
        else:
            dictLock.acquire()         #Acquire lock to check if the wanted file is not already being saved by another thread
            currentCheck = dictionary.get(payload)
            if currentCheck == 'running':    #Checking dictionary
                self.fsock.send(b"True", debug)
                dictLock.release()
                print("the file " +payload+" is currently being transfered")
            else:
                dictionary[payload] = "running"    #If it is not currently being transferred then the thread can transfer it and
                dictLock.release()                 #you write to the dictionary that you are transferring the file
                sleep(40)  
                self.fsock.send(b"False", debug) #Tell client that the file is not being transferred and does not exist in the 
                try:                             #directory
                    payload2 = self.fsock.receive(debug)     #Receiving file data
                except:
                    print("connection lost while receiving.")
                    sys.exit(0)
                if not payload2:
                    sys.exit(0)
                try:
                    self.fsock.send(payload2, debug)
                except:
                    print("------------------------------")
                    print("connection lost while sending.")
                    print("------------------------------")

                output = open(payload, 'wb') #open and set to write byte array
                output.write(payload2) #writing to file 
                output.close()

                dictLock.acquire()       #After the file has been written, delete it from the dictionary
                del dictionary[payload]
                dictLock.release()
        self.fsock.close()
        

while True:
    sockAddr = lsock.accept()      #Continuously accept connections 
    server = Server(sockAddr)
    server.start()