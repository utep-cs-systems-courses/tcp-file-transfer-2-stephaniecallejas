#!/usr/bin/env python3

import sys
sys.path.append("../lib")
import socket, params, os, re
from encapFramedSock import EncapFramedSock
from threading import Thread, Lock

switchesVarDefaults = (
	(('-l', '--listenPort') ,'listenPort', 50001),
	(('-d', '--debug'), "debug", False), # boolean (set if present)
	(('-?', '--usage'), "usage", False), # boolean (set if present)
	)

paramMap = params.parseParams(switchesVarDefaults)
debug, PORT = paramMap["debug"], paramMap["listenPort"]
HOST = "127.0.0.1"

global lock, current_files
current_files = set()

if paramMap['usage']:
    params.usage()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind((HOST, PORT))
	s.listen(5)		#listen for up to 5 incoming conns
	lock = Lock()

	print("listening on:", (HOST, PORT))
	
	class Server(Thread):
		def __init__(self, sockAddr):
			Thread.__init__(self)
			self.clientSock, self.cliendAddr = sockAddr
			self.fsock = EncapFramedSock(sockAddr)
		def run(self):
			print("new thread handling connection from", self.cliendAddr)
		
			while True:
				payload = ""
				try:
					fileName, fileContents = self.fsock.receive(debug)
				except Exception as e:
					print("File transfer failed")
					print(e)
					sys.exit(0)
			
				conn, addr = s.accept()
				
				if debug: print("recieved: ", payload)

				if payload is None:
					print("File contents were empty, exiting...")
					sys.exit(0)

				fileName = fileName.decode()

				try:
					if not os.path.isfile("./received/" + fileName):
						#Get a lock to transfer the file
						lock.acquire()
						#If file is in current files then you can't write to it
						if fileName in current_files:
							print("File is currently being written to")
							lock.release()
							sys.exit(0)
						else:
							#If the file is not being written to then we can add it to the current files
							current_files.add(fileName)
							lock.release()
						
						currpath = os.path.dirname(os.path.realpath(__file__))
						file = open(currpath + "/received/" + fileName, 'w+b')
						file.write(fileContents)
						file.close()
						print("File ", fileName, " recieved!")
						#get lock to make sure that current files is not being written to
						lock.acquire()
						#because file is no longer in use, remove from set
						current_files.remove(fileName)
						lock.release()
						sys.exit(0)
					else:
						print("File is already on the server")
						sys.exit(1)
				except FileNotFoundError as e:
					print("File was not found")
					print(e)
					sys.exit(0)

	while True:
		sockAddr = s.accept()
		server = Server(sockAddr)
		server.start()