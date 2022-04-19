"""Console script for python_algebra."""
import argparse
import sys, os
sys.path.append(os.path.dirname(__file__))
# import the necessary packages
import numpy as np
import cv2
from numpy import empty

from HandClasses import *

import pygame as game

from AppUnity import *
from VerletPhysics import *
from Fits import *
from Camera import *

import pathlib

from media import *

import time
import zmq
context = zmq.Context()
socket = context.socket(zmq.PUB)
port = "5555"
print ("Collecting updates from weather server...")
#socket.connect ("tcp://localhost:%s" % port)
socket.bind("tcp://*:5555")

class DemoRope(App):
    #
    #
    #camera selection Web-Cam/Intel
    #cameraString = args.camera
    cameraString = "Web-Cam"
    camera = Camera(cameraString)
    input = ""
    def Reset(self):
        #print("reset class")
       pass
    #
    def Initialize(self):
        #
        pass


    #
    def Update(self):
        #     
        success, image = self.camera.getFrame()
        #
        self.cv_inputimage = cv2.flip(image.copy(),1)
        frameout =  VideoClass(success,image.copy(),self.size)
        self.list_hands = frameout.list_hands
        self.cv_masksumimage = frameout.output
        #self.cv_greenfiltered = maskRight.tagged
        #self.input = cv2.waitKey(1)
        #cv2.imshow('gree-filter',self.cv_masksumimage)



    #
    def Render(self):
        #

        # define the RGB value for white,
        #  green, blue colour .
        white = (255, 255, 255)
        green = (0, 255, 0)
        blue = (0, 0, 128)
        # create a rectangular object for the
        # text surface object

        # copying the text surface object
        # to the display surface object
        # at the center coordinate.
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN) # POLLIN for recv, POLLOUT for send
        poller2 = zmq.Poller()
        poller2.register(socket,zmq.POLLOUT)
        evts = poller.poll(5) # wait *up to* one second for a message to arrive.
        #    string = "1"
        #    socket.send()
        evts2 = poller2.poll(5)
        if len(evts)>0:
            print("CouldReceive")
        #if evts!= empty:
            message = socket.recv()
        string = "100,100,0"
        if(len(self.list_hands)==1):
            if self.list_hands[0].state=='Closed':
                string = str(self.list_hands[0].centerTriangle[0])+','+str(self.size[1]-self.list_hands[0].centerTriangle[1])+",1"
            elif self.list_hands[0].state=='Open':
                string = str(self.list_hands[0].centerTriangle[0])+','+str(self.size[1]-self.list_hands[0].centerTriangle[1])+",0"
            
        if len(evts2)>0:
            print("CouldSend")
            socket.send(string.encode())
            print (string.encode())
        topic = "1"
        messagedata = "2"
        #socket.send_string(string)

def main():
    """Console script for python_algebra."""
    parser = argparse.ArgumentParser(description='A test program.')
    parser.add_argument("-c","--camera", help="Select the camera from: Web-Cam/Intel", default= "Web-Cam")
    parser.add_argument("-b", "--boundaries", type=str,
            default=str(pathlib.Path(__file__).parent),
            help="Path to folder where boundiries are located")

    args = parser.parse_args()
    #parser = argparse.ArgumentParser()
    #parser.add_argument('_', nargs='*')
    #args = parser.parse_args()

    #print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "python_algebra.cli.main")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
