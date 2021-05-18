try:
    from Tkinter import *
    import tkMessageBox
except ImportError:
    try:
        from tkinter import *
        from tkinter import messagebox
    except Exception:
        pass

import time, socket
from threading import Thread, Event
import sys

import cv2
from PIL import Image
from PIL import ImageTk
import imutils

import numpy as np

from tello import Tello
import handState as hs

## TODO kontrolleres irányítás

class myApp:
    
    
    def getLeapData(self):
        while self.running:
            try:
                msg = self.leap_socket.recv(128).decode()
                self.lbl.config(text=msg)
            except:
                print( sys.exc_info()[0] )
                print( sys.exc_info()[1] )
    
    def TelloVstream(self):
    
        self.cap = cv2.VideoCapture(r"udp://0.0.0.0:11111", cv2.CAP_FFMPEG)
        # self.cap = cv2.VideoCapture(r"out.mp4", cv2.CAP_FFMPEG)
        
        if not self.cap.isOpened:
            return
            
        while self.vstreamon:
            try:
                ret, frame = self.cap.read()
                
                if not ret:
                    break
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = imutils.resize(frame, height=360, width=480)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                self.lbl_Video.configure(image=image)
                self.lbl_Video.image=image
            except:
                print( sys.exc_info()[0] )
                print( sys.exc_info()[1] )
        self.lbl_Video.configure(image='')
        self.lbl_Video.image=''
        self.cap.release()
        self.Tello.StreamOff()
        ## TODO  utolsó frame miért marad ott...
            
    
    def startVstream(self):
        self.Tello.StreamOn()
        self.vstreamon = True
        self.telloVideoThread=Thread(target=self.TelloVstream)
        self.telloVideoThread.start()
        
    def stopVstream(self):
        self.vstreamon = False
        ## áttéve
        ## self.Tello.StreamOff()
        
    def __init__(self):
        self.root = Tk()
        self.Tello = Tello()
        self.Tello.StartListen()
        
        
        
        self.running = True
        self.vstreamon = False

        self.LeapSrv=LeapServer()
        self.LeapSrv.start()
        
        self.leap_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.leap_socket.connect(("127.0.0.1", 3331))
        ## self.leap_socket.settimeout(1)
        
        self.leapThread = Thread(target=self.getLeapData)
        self.leapThread.start()
        
        self.updateState()
        
        self.makeWidgets(self.root)
        
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.root.mainloop()
 
    def updateState(self):
    ##TODO csekk sef.running-ra ? de a main looppal egyutt lehet bezárul a socket miatt
        self.response = self.Tello.getResponse()
        self.state = self.Tello.getState()
        try:
            self.lbl_Response.configure( text = "response" + self.response )
            self.lbl_Battery.configure( text = "battery: " + self.state['bat'] + "%" )
            self.lbl_Height.configure( text = "height: " + self.state['h'] + "cm")
        except:
            pass
        self.root.after(66, self.updateState)
          
        
    def onClosing(self):
        self.Tello.StopListen()
        self.running=False
        self.leap_socket.close()
        self.leapThread.join()
        self.LeapSrv.close()
        self.root.destroy()
        
    def makeWidgets(self,parent):

        self.frame_Top = Frame(parent)
        self.frame_Top.grid(column=0, row=0)

        self.frame_Bottom= Frame(parent)
        self.frame_Bottom.grid(column=0, row=1)

        self.btn_Takeoff = Button(self.frame_Bottom, text='Takeoff', command = self.Tello.Takeoff ) 
        self.btn_Land = Button(self.frame_Bottom, text='Land', command = self.Tello.Land )
        self.btn_State = Button(self.frame_Bottom, text='State')
        self.btn_Video = Button(self.frame_Bottom, text='Video on', command=self.startVstream )
        self.btn_V_Off = Button(self.frame_Bottom, text='Video off', command=self.stopVstream )
        self.btn_SDK = Button(self.frame_Bottom, text='SDK mode', command = self.Tello.SdkMode )

        self.btn_Takeoff.pack( side = LEFT)
        self.btn_Land.pack( side = LEFT)
        self.btn_State.pack( side = LEFT )
        self.btn_Video.pack( side = LEFT )
        self.btn_V_Off.pack( side = LEFT )
        self.btn_SDK.pack( side = LEFT )

        self.lbl_Response = Label(self.frame_Top, text='Response:  ')
        self.lbl_Battery = Label(self.frame_Top, text='Battery:  ')
        self.lbl_Height = Label(self.frame_Top, text='Height:  ')

        self.lbl_Response.pack(side=LEFT)
        self.lbl_Battery.pack(side=LEFT)
        self.lbl_Height.pack(side=LEFT)
        
        self.scale_ZeroZone=Scale(self.root, label="holtjáték", from_=0, to=30, orient=HORIZONTAL)
        self.scale_MaxSpeed=Scale(self.root, label="max sebesség", from_=0, to=100, orient=HORIZONTAL)
        
        self.scale_ZeroZone.grid(column=0, row=2)
        self.scale_MaxSpeed.grid(column=0, row=3)
        
        self.btn_Apply=Button(self.root, text="Apply", command=self.applySettings)
        self.btn_Apply.grid(column=0, row=4)
        
        self.lbl_Video = Label(self.root, text = "video")
        self.lbl_Video.grid(column=0, row=5)

    def applySettings(self):
        maxSpeed = self.scale_MaxSpeed.get()
        holtjatek = self.scale_ZeroZone.get()
        
        if holtjatek > maxSpeed:
            maxSpeed = holtjatek
            self.scale_MaxSpeed.set(holtjatek)
            
        self.LeapSrv.set(maxSpeed, holtjatek)
        

class LeapServer:
    def __init__(self):
        self.hand = hs.Hand()
        
        self.leap_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.leap_socket.settimeout(0.2)
        self.leap_socket.connect(("127.0.0.1", 3224))
        
        self.gui_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gui_socket.bind(("127.0.0.1", 3331))
        self.gui_socket.listen(1)

        self.GUIsock = None
        self.GUIaddr = None
        self.sock = None
        print ("leap-gui communication created")
        
        self.run_thread = Thread(target=self.run)
        
    def set(self, maxSpeed, roundToZero):
        self.hand.set(maxSpeed, roundToZero)
        

    def run(self):
        self.GUIsock, self.GUIaddr = self.gui_socket.accept()
        
        MSG_VEL_0 = "rc 0 0 0 0".encode("utf-8")
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        TELLO_ADDRESS = ('192.168.10.1', 8889)
        
        while True:
            
            try:
                msg=self.leap_socket.recv(2048).decode("utf-8")
                param_list = re.split(',?\s', msg)
                
                #ha nem olvas elég gyorsan több üzenet lesz a bufferben
                if len(param_list) == 24:
                
                    palm = np.array(param_list[0:9]).astype('float32')
                    palm = palm.reshape(3,3)
                    #tenyer normalvektora, tenyer iranyvektora, tenyer koordinatai
                    
                    ## TODO self.GUIsock.send(msg.encode('utf-8'))
                   
                    fingers = np.array(param_list[9:25]).astype('float32')
                    fingers = fingers.reshape(5,3)
                    #ujjak iranyvektorai nagyujjtol kezdve [[x, y, z], ...]
                    cmnd = self.hand.getControlParameters(palm, fingers)
                    print(cmnd)
                    self.sock.sendto(cmnd.encode("utf-8"), TELLO_ADDRESS)
                    
            except socket.timeout:
                print( sys.exc_info()[0] )
                print("timeout rc 0 küldve")
                self.sock.sendto(MSG_VEL_0, TELLO_ADDRESS)
                
            ## socket bezárásakor a ciklus is bezáródik:
            except:
                break
                print( "leapserver egyéb hiba")
                print( sys.exc_info()[0] )
                print( sys.exc_info()[1] )
                
            
    def start(self):
        self.run_thread.start()
        
    def close(self):
        self.leap_socket.close() # run leáll
        self.gui_socket.close()


if __name__=="__main__":
    app=myApp()




