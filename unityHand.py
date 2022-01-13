# import the necessary packages
import numpy as np
import argparse
import cv2

from HandClasses import *

import pygame as game

from App import *
from VerletPhysics import *
from Fits import *
from Camera import *

import os
import pathlib

from media import *

parser = argparse.ArgumentParser(description='A test program.')
parser.add_argument("-c","--camera", help="Select the camera from: Web-Cam/Intel", default= "Web-Cam")
parser.add_argument("-b", "--boundaries", type=str,
        default=str(pathlib.Path(__file__).parent),
        help="Path to folder where boundiries are located")

args = parser.parse_args()

import time
import zmq
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


class DemoRope(App):
    #
    #
    print("Using: " + args.camera)
    #camera selection Web-Cam/Intel
    cameraString = args.camera
    camera = Camera(cameraString)

    def Reset(self):
        #print("reset class")
        #self.rope.particles[-1].material.mass = 0.0
        #self.world.particles = list()
        print("res")
    #
    def Initialize(self):
        #self.cap = cv2.VideoCapture(0)
        self.hand1 = HandClassOneColor([[]])
        self.Reset()
        self.list_hands = []
        mat = Material(1.0,1.0,1.0)
        #self.rope.particles[9].ApplyForce(Vector(400.0, -900.0))


    #
    def Update(self):
        #
        if len(self.list_hands)>0 and self.list_hands[0].state=='Closed':
            if self.grabbed == None:
                closest = self.ClosestPoint()
                if closest[1] < self.radius:
                    self.grabbed = closest[0]

            if self.grabbed != None:
                mouse    = Vector(self.list_hands[0].centerTriangle[0],self.list_hands[0].centerTriangle[1])
                force = (mouse - self.grabbed.position) * self.strength
                self.grabbed.ApplyImpulse(force)
    
            self.world.Simulate()
       
        success, image = self.camera.getFrame()
        

            
        #
        self.cv_inputimage = cv2.flip(image.copy(),1)
        frameout =  VideoClass(success,image.copy())
        self.list_hands = frameout.list_hands
        self.cv_masksumimage = frameout.output
        #self.cv_greenfiltered = maskRight.tagged
        
        bin = cv2.waitKey(5)



    #
    def Render(self):
        #
        # define the RGB value for white,
        #  green, blue colour .

        # create a text surface object,
        # on which text is drawn on it.
        #text = font.render(tempfit.function, True, green, blue)


        # create a rectangular object for the
        # text surface object

        # copying the text surface object
        # to the display surface object
        # at the center coordinate.
       
        if(len(self.list_hands)==1):
            if self.list_hands[0].state=='Closed':
                game.draw.circle(self.screen, (0, 255, 0), self.list_hands[0].centerTriangle, 8, 0)
                print('here')
            elif self.list_hands[0].state=='Open':
                game.draw.circle(self.screen, (255, 0, 0), self.list_hands[0].centerTriangle, 8, 0)
            message = socket.recv()
            print("Received request: %s" % message)
            #  Do some 'work'.
            #  Try reducing sleep time to 0.01 to see how blazingly fast it communicates
            #  In the real world usage, you just need to replace time.sleep() with
            #  whatever work you want python to do, maybe a machine learning task?
            #time.sleep(1)
            #  Send reply back to client
            #  In the real world usage, after you finish your work, send your output here
            string = str(self.list_hands[0].centerTriangle[0])+','+str(self.list_hands[0].centerTriangle[1])
            socket.send(string.encode())
        game.display.update()

    #


if __name__ == "__main__":
    print ("Starting...")
    app = DemoRope("Swinging Rope", 640, 480, 30)
    app.Run()

    #if bin & 0xFF == ord('q'):
    #    print('exit')
    #elif bin & 0xFF ==ord('s'):
    #    print('save')

    #self.cap.release()
    # loop over the boundaries
    print ("Ending...")