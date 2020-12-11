#! /usr/bin/env python3

import sys
sys.path.append("../lib")
import socket, params, os, re
from encapFramedSock import EncapFramedSock

switchesVarDefaults = (
	(('-s', '--server'), 'server', "127.0.0.1:50001"),
	(('-d', '--debug'), "debug", False), # boolean (set if present)
	(('-?', '--usage'), "usage", False), # boolean (set if present)
	)

def getFile():
	invalid = True
	while invalid:
		try:
			filename = input(str("Please enter the filename to send:"))
			file = open(filename,'rb')
			return file, filename
			invalid = False
		except FileNotFoundError:
			print("I couldn't find your file! Please keep trying.")
	

paramMap = params.parseParams(switchesVarDefaults)
server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
	params.usage()

try:
	print(server)
	HOST, PORT = re.split(":", server)
	PORT = int(PORT)
except:
	print("Can't parse server:port from '%s'" % server)
	sys.exit(1)

	
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	if s is None:
		print('could not open socket')
		sys.exit(1)
	
	try:
		s.connect((HOST, PORT))
		encapSock = EncapFramedSock((s, (HOST, PORT)))
		file, filename = getFile();
		data = file.read()
		if len(data) == 0:
			print("Empty file.")
			sys.exit(1)
		print("sending file")
		encapSock.send(filename, data, debug)
		file.close()
	except ConnectionRefusedError:
		print("Could not connect to server!")