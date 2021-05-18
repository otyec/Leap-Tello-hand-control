import numpy as np
import vg

class Hand:
    
    def __init__(self):
        self.speed_LR = 0
        self.speed_FB = 0
        self.speed_UD = 0
        self.speed_ROT = 0
        
        # el alatti absz.értékû sebességek 0 ra lesznek állítva
        self.roundToZero = 5
        # sebesség határértéke: (roundtozero < x < 100)
        self.maxSpeed = 30
        
                
        self.origo = np.array([]) # plcaeholder for snapshot of palm parameters when a control action is started
        self.origo_isSet = False
    
    
    def set(self, maxSpeed=50, roundToZero=20):
        self.maxSpeed = maxSpeed
        self.roundtozero = roundToZero
    
    def analizeHandGestures(self, palm, fingers):
        
        self.LR = False
        self.FB = False
        self.UD = False
        self.ROT = False
        ## INIT kez okolben van, mind false
        
        ## LR tenyer normal x irany, ez es a nagyujj altal bezart szög < 60. nem mindegy melyik kez
        ## TODO bal kéz esetén megfordítani a keresztszorzat paramétereit / ifet kiegészíteni ? 
        if vg.angle(
            np.cross(palm[1], palm[0]),
            fingers[0] ) < 60:
            self.LR = True
         
        ## FB mutatoujj es a tenyer irany bezart szöge < 60   
        if vg.angle( fingers[1],  palm[1]) < 60:
            self.FB = True
            
        ## UD kis gyurus közepso + tenyer normal bezart szöge
        if vg.angle( np.add(fingers[3], fingers[4]), palm[0]) < 50: 
            ## ## fingers 2 hianyzik
            self.UD = True

        
        ## all on (kis+mutato), közepso + tenyer irany < 50
        if vg.angle(np.add(fingers[1], fingers[4]), palm[1]) < 50 and vg.angle(fingers[2], palm[1]) < 50:
            self.LR = True
            self.FB = True
            self.UD = True
            self.ROT = True
            
        ## ROT kisujj, mutatoujj szöge > 30
        if self.ROT and vg.angle(fingers[1], fingers[4]) > 30:
            self.LR = False
            self.FB = False
            self.UD = False
            
            
    def updateOrigo(self):
        
        if not (self.LR or self.FB or self.UD or self.ROT):
            self.origo_isSet = False
            
        elif not self.origo_isSet:
            self.origo = self.palm
            self.origo_isSet = True
            
               
    def CalculateAngles(self):
        
        ## a reszponzivitás teszthez:
        # # self.LR = False
        # # self.FB = False
        # # self.ROT = False
        
        #TODO ez csak jobb kézre jó. bal kéz esetén fordítva kell beszorozni
        origo_palm_perp = vg.perpendicular(self.origo[1], self.origo[0])
        palm_perp = vg.perpendicular(self.palm[1], self.palm[0])

        ## signed angle between origo palm norm and rejection of palm norm from origo palm dir, look is origo palm dir
        ## REGI signed angle between n0 and rejection of palm norm from origo palm dir, look is origo palm dir
        #NEW## signed angle between origo palm norm and rejection of palm norm from (rejetfion of palm dir from origo palm norm), look is (palm dir)      
        if self.LR:
            ## self.speed_LR = vg.signed_angle( self.origo[0], vg.reject(self.palm[0], self.origo[1]), self.origo[1] )
            self.speed_LR = vg.signed_angle( self.origo[0], vg.reject(self.palm[0], vg.reject(self.palm[1], self.origo[0])), self.origo[1] )
        else:
            self.speed_LR = 0
            
        if self.FB:
            ## signed angle between origo palm norm and rejection of palm norm from origo palm perpendicular, look is origo palm perpendicular
            ## REGI self.speed_FB = vg.signed_angle( self.origo[1], vg.reject(self.palm[1], origo_palm_perp), origo_palm_perp )
            # NEW## signed angle between origo palm norm and rejection of palm norm from (rejection of palm perpendicular from origo palm norm), look is origo palm perpendicular
            self.speed_FB = vg.signed_angle( self.origo[0], vg.reject(self.palm[0], vg,reject(palm_perp, self.origo[0])), origo_palm_perp )
        else:
            self.speed_FB = 0
            
        ## distance between origo y and palm y
        if self.UD:
            self.speed_UD = self.palm[2][1] - self.origo[2][1]
        else:
            self.speed_UD = 0
            
        ## signed angle between origo palm dir and rejection of palm dir from origo palm norm, look is origo palm norm
        if self.ROT:
            self.speed_ROT = vg.signed_angle(self.origo[1], vg.reject(self.palm[1], self.origo[0]), self.origo[0] )
        else:
            self.speed_ROT = 0
        
    def roundAngles(self):
        # TODO forgatást megszorozni? vagy valahol gyorsítani
        # közel 0-hoz -> 0 ra kerekíti
        self.speed_FB = 0 if abs(self.speed_FB) < self.roundToZero else self.speed_FB
        self.speed_LR = 0 if abs(self.speed_LR) < self.roundToZero else self.speed_LR
        self.speed_UD = 0 if abs(self.speed_UD) < self.roundToZero else self.speed_UD
        self.speed_ROT = 0 if abs(self.speed_ROT) < self.roundToZero else self.speed_ROT

        # nagyobb mint a max sebesseg
        self.speed_FB = self.maxSpeed if self.speed_FB > self.maxSpeed else self.speed_FB
        self.speed_LR = self.maxSpeed if self.speed_LR > self.maxSpeed else self.speed_LR
        self.speed_UD = self.maxSpeed if self.speed_UD > self.maxSpeed else self.speed_UD
        self.speed_ROT = 100 if self.speed_ROT > 100 else self.speed_ROT
            
        # absz értékben nagyobb mint a max sebesség
        self.speed_FB = -self.maxSpeed if -self.speed_FB > self.maxSpeed else self.speed_FB
        self.speed_LR = -self.maxSpeed if -self.speed_LR > self.maxSpeed else self.speed_LR
        self.speed_UD = -self.maxSpeed if -self.speed_UD > self.maxSpeed else self.speed_UD
        self.speed_ROT = -100 if -self.speed_ROT > 100 else self.speed_ROT
            
            
            
    def getControlParameters(self, palm, fingers):
    
        self.palm = palm
        self.fingers = fingers
              
        self.analizeHandGestures(self.palm, self.fingers)
        
        self.updateOrigo()
        
        if self.origo_isSet:
            
            self.CalculateAngles()
            
            self.roundAngles()
            msg = "rc " + str(int(self.speed_LR)) + " " + str(int(self.speed_FB)) + " " + str(int(self.speed_UD)) + " " + str(int(self.speed_ROT))
            return msg
                     
        else:
            print ("handstate rc 0 0 0 0")
            return "rc 0 0 0 0"
            
        
