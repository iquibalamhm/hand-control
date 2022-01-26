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

# define the list of boundaries
todaylowRight = np.loadtxt(os.path.sep.join([args.boundaries, 'lowRight']), dtype=int)
todayhighRight = np.loadtxt(os.path.sep.join([args.boundaries, 'highRight']), dtype=int)

todaylowLeft = np.loadtxt(os.path.sep.join([args.boundaries, 'lowLeft']), dtype=int)
todayhighLeft = np.loadtxt(os.path.sep.join([args.boundaries, 'highLeft']), dtype=int)
import time
import zmq
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
class DemoRope(App):
    #
    #
    world    = World(Vector(640.0, 480.0), Vector(0, 0), 4)

    grabbed  = None
    radius   = 15
    strength = 0.1

    print(args.camera)
    #camera selection Web-Cam/Intel
    cameraString = args.camera
    camera = Camera(cameraString)

    segments = 300

    def Reset(self):
        #print("reset class")
        rope = self.world.AddComposite()

        rope.reset()


        #self.rope.particles[-1].material.mass = 0.0
        #self.world.particles = list()
        #self.world.constraints = list()
        self.world.reset()
        for i in range(self.segments+1):
            rope.AddParticles(
                self.world.AddParticle(20+i*2, self.world.hsize.y,Material(0.4,0.4,1.0)),
            )
                # y=210.0
                #self.world.AddParticle(5.0 + i * 10.0, 200.0)) # y=270.0
        for i in range(0, self.segments):
            rope.AddConstraints(self.world.AddConstraint(rope.particles[i],rope.particles[i+1],1.0))
        
        rope.particles[0].material.mass = 0.0
        rope.particles[-1].material.mass = 0.0
    #
    def Initialize(self):
        #
        
        self.world.reset()
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
        elif game.mouse.get_pressed()[0]:
            if self.grabbed == None:
                closest = self.ClosestPoint()
                if closest[1] < self.radius:
                    self.grabbed = closest[0]
            if self.grabbed != None:
                mouse = Vector(game.mouse.get_pos()[0], game.mouse.get_pos()[1])
                force = (mouse - self.grabbed.position) * self.strength
                self.grabbed.ApplyImpulse(force)
            self.world.Simulate()
        else:
            if self.grabbed != None:
                self.world.SimulateWorldStop() 
                self.grabbed = None

        
        success, image = self.camera.getFrame()
        

            
        #
        self.cv_inputimage = cv2.flip(image.copy(),1)
        frameout =  VideoClass(success,image.copy())
        self.list_hands = frameout.list_hands
        self.cv_masksumimage = frameout.output
        #self.cv_greenfiltered = maskRight.tagged
        
        cv2.imshow('input-image',self.cv_inputimage)
        bin = cv2.waitKey(5)
            
        cv2.imshow('gree-filter',self.cv_masksumimage)
        if game.key.get_pressed()[game.K_ESCAPE]:
            self.Exit()


    #
    def Render(self):
        #
        self.screen.fill((24, 24, 24))
        for c in self.world.constraints:
            pos1 = (int(c.node1.position.x), int(c.node1.position.y))
            pos2 = (int(c.node2.position.x), int(c.node2.position.y))
            game.draw.line(self.screen, (255, 255, 0), pos1, pos2, 4)
        game.draw.line(self.screen, (130, 130, 130), (self.world.hsize.x,20), (self.world.hsize.x,460), 3)
        game.draw.line(self.screen, (130, 130, 130), (20,self.world.hsize.y), (620,self.world.hsize.y), 3)
        y = []
        x = []
        for p in self.world.particles:
            pos = (int(p.position.x), int(p.position.y))
            x.append(p.position.x-self.world.hsize.x)
            y.append(p.position.y*-1+self.world.hsize.y)
            game.draw.circle(self.screen, (255, 255, 255), pos, 8, 0)

        tempfit = CurveFit(x,y,2)

        # define the RGB value for white,
        #  green, blue colour .
        white = (255, 255, 255)
        green = (0, 255, 0)
        blue = (0, 0, 128)
        # create a font object.
        # 1st parameter is the font file
        # which is present in pygame.
        # 2nd parameter is size of the font
        font = game.font.Font('freesansbold.ttf', 15)
        font2 = game.font.Font('freesansbold.ttf', 13)

        # create a text surface object,
        # on which text is drawn on it.
        #text = font.render(tempfit.function, True, green, blue)
        #game.draw.arc(self.screen, (255,0,0), tempfit.ellipserect,  tempfit.startangle, tempfit.endangle,3)
        
        for l in range(len(tempfit.x_parabolic)-1):
            pos1 = (int(tempfit.x_parabolic[l]), int(tempfit.y_parabolic[l]))
            pos2 = (int(tempfit.x_parabolic[l+1]), int(tempfit.y_parabolic[l+1]))
            game.draw.line(self.screen, (255, 0, 0), pos1, pos2, 3)
            #game.draw.circle(self.screen, (255, 0, 0), pos1, 1, 0)

        text = font2.render("Yours : " +str(tempfit.function), True, green, blue)
        #game.draw.line(self.screen, (255, 0, 0), tempfit.startpoint, tempfit.endpoint, 3)


        # create a rectangular object for the
        # text surface object
        textRect = text.get_rect()

        # set the center of the rectangular object.
        textRect.center = (470, 30)

        # copying the text surface object
        # to the display surface object
        # at the center coordinate.
        self.screen.blit(text, textRect)

        text2 = font2.render("Target: y = - 0.0015 * x^2 + 0.042 * x + 115.0", True, green, blue)
        textRect2 = text2.get_rect()
        textRect2.center = (150, 30)
        self.screen.blit(text2, textRect2)

        text3 = font.render("Match the equations", True, green, blue)
        textRect3 = text3.get_rect()
        textRect3.center = (300, 10)
        self.screen.blit(text3, textRect3)
        
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
    def ClosestPoint(self):
        if game.mouse.get_pressed()[0]:
            mouse    = Vector(game.mouse.get_pos()[0], game.mouse.get_pos()[1])
        else:
            mouse    = Vector(self.list_hands[0].p1[0],self.list_hands[0].p1[1])
        closest  = None
        distance = float('inf')
        for particle in self.world.particles:
            d = mouse.distance(particle.position)
            if d < distance:
                closest  = particle
                distance = d
        return (closest, distance)

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