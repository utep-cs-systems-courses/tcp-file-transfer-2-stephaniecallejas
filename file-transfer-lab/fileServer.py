#!/usr/bin/env python3

import sys
sys.path.append("../lib")
import socket, params, os, re
from framedSock import framedSend, framedReceive


switchesVarDefaults = (
	(('-l', '--listenPort') ,'listenPort', 50001),
	(('-d', '--debug'), "debug", False), # boolean (set if present)
	(('-?', '--usage'), "usage", False), # boolean (set if present)
	)

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, PORT = paramMap["debug"], paramMap["listenPort"]
HOST = "127.0.0.1"

if paramMap['usage']:
    params.usage()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind((HOST, PORT))
	s.listen(5)		#listen for up to 5 incoming conns
	print("listening on:", (HOST, PORT))
	
	while True:
		conn, addr = s.accept()
		
		if not os.fork():
			print("Connection from: ", addr)

			payload = ""
			try:
				fileName, fileContents = framedReceive(conn, debug)
			except Exception as e:
				print("File transfer failed")
				print(e)
				sys.exit(0)

			if debug: print("recieved: ", payload)

			if payload is None:
				print("File contents were empty, exiting...")
				sys.exit(0)

			fileName = fileName.decode()

			try:
				if not os.path.isfile("./received/" + fileName):
					currpath = os.path.dirname(os.path.realpath(__file__))
					file = open(currpath+"/received/" + fileName, 'w+b')
					file.write(fileContents)
					file.close()
					print("File ", fileName, " recieved!")
					sys.exit(0)
				else:
					print("File is already on the server")
					sys.exit(0)
			except FileNotFoundError as e:
				print("File was not found")
				print(e)
				sys.exit(0)