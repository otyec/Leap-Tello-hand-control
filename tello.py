import socket
import sys
from threading import Thread

from strUtil import stateToDict

class Tello:

    def __init__(self):
    
        self.TELLO_ADDRESS = ('192.168.10.1', 8889)
        self.RESPONSE_ADDRESS = ('', 9000)
        self.STATE_ADDRESS = ('0.0.0.0', 8890)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.state = {}
        self.response = ""
        self.listening = False
        
    def sendCommand(self, command):
        msg=command.encode(encoding='utf-8')
        self.socket.sendto(msg, self.TELLO_ADDRESS)
    
    def SdkMode(self):
        self.sendCommand( "command" )
    
    def Takeoff(self):
        self.sendCommand( "takeoff" )

    def Land(self):
        self.sendCommand( "land" )
        
    def StreamOn(self):
        self.sendCommand( "streamon" )
    
    def StreamOff(self):
        self.sendCommand( "streamoff" )
    
    def getState(self):
        return self.state
        
    def getResponse(self):
        return self.response

    
    def ListenResponse(self):

        while self.listening:                 
            try:
                data, server = self.resp_sock.recvfrom(1518)
                resp = data.decode('utf-8')
                self.response = resp
            except:
                print( sys.exc_info()[0] )
                print( sys.exc_info()[1] )
    
    def ListenState(self):
    
        while self.listening:
            try:
                data, server = self.state_sock.recvfrom(1518)
                state = data.decode('utf-8')
                state = stateToDict(state)
                self.state = state
            except:
                print( sys.exc_info()[0] )
                print( sys.exc_info()[1] )
    
    def StartListen(self):
    
        self.listening = True
        self.resp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.resp_sock.bind(self.RESPONSE_ADDRESS)
        
        self.state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.state_sock.bind(self.STATE_ADDRESS)
        
        self.response_thread = Thread(target=self.ListenResponse)
        self.state_thread = Thread(target=self.ListenState)
        
        self.response_thread.start()
        self.state_thread.start()
        
        
    def StopListen(self):
        self.listening = False
        self.resp_sock.close()
        self.state_sock.close()
        
