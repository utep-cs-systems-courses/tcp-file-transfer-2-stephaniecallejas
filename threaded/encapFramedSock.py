import re

class EncapFramedSock:               # a facade
  def __init__(self, sockAddr):
    self.sock, self.addr = sockAddr
    self.rbuf = b""         # receive buffer
  def close(self):
    return self.sock.close()
  def send(self, file_name, payload, debugPrint=0):
    if debugPrint: print("framedSend: sending %d byte message" % len(payload))
    msg = str(len(payload)).encode() + b':' + file_name.encode() + b':' + payload
    while len(msg):
      nsent = self.sock.send(msg)
      msg = msg[nsent:]
  def receive(self, debugPrint=0):
    state = "getLength"
    msgLength = -1
    while True:
      if (state == "getLength"):
        match = re.match(b'([^:]+):(.*):(.*)', self.rbuf, re.DOTALL | re.MULTILINE) # look for colon
        if match:
          lengthStr, file_name, self.rbuf = match.groups()
          try: 
            msgLength = int(lengthStr)
          except:
            if len(self.rbuf):
              print("badly formed message length:", lengthStr)
              return None
          state = "getPayload"
      if state == "getPayload":
        if len(self.rbuf) >= msgLength:
         payload = self.rbuf[0:msgLength]
         self.rbuf = self.rbuf[msgLength:]
         return file_name, payload
      r = self.sock.recv(100)
      self.rbuf += r
      if len(r) == 0:
        if len(self.rbuf) != 0:
         print("FramedReceive: incomplete message. \n state=%s, length=%d, self.rbuf=%s" % (state, msgLength, self.rbuf))
        return None
      if debugPrint: print("FramedReceive: state=%s, length=%d, self.rbuf=%s" % (state, msgLength, self.rbuf))