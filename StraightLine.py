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

# define the list of boundaries
todaylowRight = np.loadtxt('lowRight.txt', dtype=int)
todayhighRight = np.loadtxt('highRight.txt', dtype=int)

todaylowLeft = np.loadtxt('lowLeft.txt', dtype=int)
todayhighLeft = np.loadtxt('highLeft.txt', dtype=int)
class DemoRope(App):
    #
    world    = World(Vector(640.0, 480.0), Vector(0, 0), 4)
    #
    grabbed  = None
    radius   = 15
    strength = 0.05
    segments = 300
    #camera selection
    cameraString = 'Intel'
    #
    def Initialize(self):
        #
        rope = self.world.AddComposite()
        #self.cap = cv2.VideoCapture(0)
        self.hand1 = HandClassOneColor([[]])

        mat = Material(1.0,1.0,1.0)
        for i in range(self.segments+1):
            rope.AddParticles(
                self.world.AddParticle(20+i*2, self.world.hsize.y,Material(0.4,0.4,1.0)),
            )
                # y=210.0
                #self.world.AddParticle(5.0 + i * 10.0, 200.0)) # y=270.0
        for i in range(0, self.segments):
            rope.AddConstraints(self.world.AddConstraint(rope.particles[i],rope.particles[i+1],1.0))
        
        rope.particles[int(len(rope.particles)/2)].material.mass = 0.0
        #rope.particles[-1].material.mass = 0.0
        self.camera = Camera(self.cameraString)
        #rope.particles[9].ApplyForce(Vector(400.0, -900.0))


    #
    def Update(self):
        #
        if self.hand1.numberofFingers == 3 and self.hand1.state=='Closed':
            if self.grabbed == None:
                closest = self.ClosestPoint()
                if closest[1] < self.radius:
                    self.grabbed = closest[0]
                #print('here')
            if self.grabbed != None:
                mouse    = Vector(self.hand1.centerTriangle[0],self.hand1.centerTriangle[1])
                force = (mouse - self.grabbed.position) * self.strength
                self.grabbed.ApplyImpulse(force)
                #print('here2')        
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
            #print('here3')

        success, image = self.camera.getFrame()

        if not success:
            print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        else:
            inputimage = cv2.flip(image.copy(),1)
            # Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image_rgb = image.copy()
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            #results = hands.process(image)

            # Draw the hand annotations on the image.
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            image_height, image_width, _ = image.shape
            
            maskRight = MaskClass(frame_HSV.copy(),todaylowRight,todayhighRight)
            maskRight.process()
            #cv2.imshow('green',maskgreen.tagged)
            
            maskLeft = MaskClass(frame_HSV.copy(),todaylowLeft,todayhighLeft)
            maskLeft.process()
            
            handRightcenters = []
            handRightcenters.append(maskRight.centers)
            self.handRight = HandClassOneColor(handRightcenters)

            handLeftcenters = []
            handLeftcenters.append(maskLeft.centers)
            self.handLeft = HandClassOneColor(handLeftcenters)

            font = cv2.FONT_HERSHEY_PLAIN
            if self.handRight.numberofFingers == 3:
                #print(str(self.hand1.area) + ' ' +str(self.hand1.state))
                cv2.putText(inputimage, 'Hand'+ str(self.handRight.state), (image_width-200,25), font, 2, (120,120,0), 3)
                #print(self.hand1.centerTriangle)
            else: 
                cv2.putText(inputimage, 'Not Right Hand', (image_width-300,25), font, 2, (120,120,0), 3)  
            
            if self.handLeft.numberofFingers == 3:
                #print(str(self.hand1.area) + ' ' +str(self.hand1.state))
                cv2.putText(inputimage, 'Hand'+ str(self.handLeft.state), (image_width-200,25), font, 2, (120,120,0), 3)
            else: 
                cv2.putText(inputimage, 'Not Left Hand', (image_width-300,25), font, 2, (120,120,0), 3)  
            
            masksum = maskRight.tagged 
            #
            self.cv_inputimage = inputimage
            self.cv_masksumimage = masksum
            self.cv_Rightfiltered = maskRight.tagged
            
            cv2.imshow('input-image',self.cv_inputimage)
            bin = cv2.waitKey(5)
            
            cv2.imshow('right-filter',self.cv_greenfiltered)
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
        

        #print("x" + str(x))
        #print("y"+ str(y))
        tempfit = CurveFit(x,y,1)

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
        
        # create a text surface object,
        # on which text is drawn on it.
        text = font.render("Yours : " +str(tempfit.function), True, green, blue)
        game.draw.line(self.screen, (255, 0, 0), tempfit.startpoint, tempfit.endpoint, 3)


        # create a rectangular object for the
        # text surface object
        textRect = text.get_rect()

        # set the center of the rectangular object.
        textRect.center = (470, 30)

        # copying the text surface object
        # to the display surface object
        # at the center coordinate.
        self.screen.blit(text, textRect)

        text2 = font.render("Target: y = 0.80 x + -15.0", True, green, blue)
        textRect2 = text2.get_rect()
        textRect2.center = (100, 30)
        self.screen.blit(text2, textRect2)

        text3 = font.render("Match the equations", True, green, blue)
        textRect3 = text3.get_rect()
        textRect3.center = (300, 10)
        self.screen.blit(text3, textRect3)

        if self.handRight.numberofFingers == 3 and self.handRight.state=='Closed':
            game.draw.circle(self.screen, (0, 255, 0), self.handRight.centerTriangle, 8, 0)
        elif self.handRight.numberofFingers == 3 and self.handRight.state=='Open':
            game.draw.circle(self.screen, (255, 0, 0), self.handRight.centerTriangle, 8, 0)
        game.display.update()

        if self.handRight.centerTriangle[0] < self.handLeft.centerTriangle[0]:
            self.gestureReset = True
        else:
            self.gestureReset = False
    #
    def ClosestPoint(self):
        if game.mouse.get_pressed()[0]:
            mouse    = Vector(game.mouse.get_pos()[0], game.mouse.get_pos()[1])
        else:
            mouse    = Vector(self.hand1.centerTriangle[0],self.hand1.centerTriangle[1])
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