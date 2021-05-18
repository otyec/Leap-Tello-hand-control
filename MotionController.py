################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import os, sys, inspect, thread, time, subprocess ,socket
import math

import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture


class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    
## fps reduce minden masodik framet eldob
    fpsReduce = False
      
## socket
    msg = ("Hello")
    msg = msg.encode('utf-8')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 3224))
    s.listen(1)
    
## socket_accept
    print ("waiting for gui to be opened")
    sock, addr = s.accept()
    print ("//client connected")

    def on_init(self, controller):
        print ("Initializing")

    def on_connect(self, controller):
        print ("Connected")

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print ("Disconnected")

    def on_exit(self, controller):
    
##close socket?
        self.sock.close()
        print ("Exited")

    def on_frame(self, controller):
        
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # Get hands
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction
            palm_position = hand.palm_position

## palm parameters          
            msg = str(normal)[1:-1] + " " + str(direction)[1:-1] + " " + str(palm_position)[1:-1]

            # Get arm bone
            arm = hand.arm

            # Get fingers
            for finger in hand.fingers:
## finger direction vectors
                msg = msg + " " + str(finger.direction)[1:-1]  ## lista zarojeleit vagja le ## 0. a naygujj 


                # Get bones
                for b in range(0, 4):
                    bone = finger.bone(b)
                    
## socket send
#TODO jobb/bal kez kuldeni
            if not self.fpsReduce:
                self.fpsReduce = True
                self.sock.send(msg.encode('utf-8'))
            else:
                self.fpsReduce = False

            
        # Get gestures
        for gesture in frame.gestures():
            if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                circle = CircleGesture(gesture)

                # Determine clock direction using the angle between the pointable and the circle normal
                if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                    clockwiseness = "clockwise"
                else:
                    clockwiseness = "counterclockwise"

                # Calculate the angle swept since the last frame
                swept_angle = 0
                if circle.state != Leap.Gesture.STATE_START:
                    previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                    swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI


            if gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture(gesture)


            if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                keytap = KeyTapGesture(gesture)


            if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                screentap = ScreenTapGesture(gesture)


    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main():
    #string = "asd"
    #os.system('ros2 action send_goal -f fibonac action_tutorials/action/Fibonacci "{order: 5}"')
    #os.system('echo "'+ '%s' % string + '"')
    
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    #háttérben is megkapja a frameket.
    controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)
    
    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print ("Press Enter to quit...")
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()