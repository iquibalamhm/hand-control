import cv2
from matplotlib import set_loglevel
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_drawing_styles = mp.solutions.drawing_styles
import numpy as np
flag = False
# For static images:
IMAGE_FILES = []

class Hand:
  p1 = [-1,-1]
  p2 = [-1,-1]
  p3 = [-1,-1]
  fingertips = []

  def center(self):
    return [(self.p1[0]+self.p2[0]+self.p3[0])/3,(self.p1[1]+self.p2[1]+self.p3[1])/3]
  
  def Area(self):
      lines = np.hstack([self.fingertips,np.roll(self.fingertips,-1,axis=0)])
      area = 0.5*abs(sum(x1*y2-x2*y1 for x1,y1,x2,y2 in lines))
      if(area<1200):
          self.state = 'Closed'
      else:
          self.state = 'Open'
      return area
  def __init__(self,hand_landmarks,width,height):
      # For webcam input:
      
      if(len(hand_landmarks)):
        self.p1 = [hand_landmarks[4]['x']*width,hand_landmarks[4]['y']*height]
        self.p2 = [hand_landmarks[8]['x']*width,hand_landmarks[8]['y']*height]
        self.p3 = [hand_landmarks[12]['x']*width,hand_landmarks[12]['y']*height]
        self.fingertips = [self.p1, self.p2,self.p3]
        self.centerTriangle = self.center()
        self.area = self.Area()
      else:
        self.state = 'Undef'    
class VideoClass:
  def __init__(self,success, image):
      with mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
          
          if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
          else:
            #Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            results = hands.process(image)
          # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            self.list_hands = []
            if results.multi_hand_landmarks:
              for hand_landmarks in results.multi_hand_landmarks:
                #print(type(hand_landmarks))
                handlandmarks_dict = MessageToDict(hand_landmarks)
                self.list_hands.append(Hand(handlandmarks_dict['landmark'],image.shape[0],image.shape[1]))
                for idx in range(len(self.list_hands)):
                  print(self.list_hands[idx].state)
                print(len(self.list_hands))
                mp_drawing.draw_landmarks(
                  image,
                  hand_landmarks,
                  mp_hands.HAND_CONNECTIONS,
                  mp_drawing_styles.get_default_hand_landmarks_style(),
                  mp_drawing_styles.get_default_hand_connections_style())
      self.output = image