#! /usr/bin/env python
import argparse
import cv2
import sys
import time
import datetime
import imutils
from collections import deque
import numpy as np


cam_device = 0
laser = (0,0)
maxlen=10
pts = deque(maxlen=10)
detected = ""
radius= 0
circle_pos = (0,0)
boundary_x=(200,220)   #aristera kai katw
boundary_y=(400,180)   #deksia kai panw
laser_position = ""
X = ""
Y = ""
stop_trigger=False
send_trigger=""
border_trigger = False
x_border_trig = False
y_border_trig = False
center = None    

class LaserTracker(object):

    def __init__(self, cam_width=640, cam_height=480, hue_min=20, hue_max=160,
                 sat_min=100, sat_max=255, val_min=200, val_max=256,
                 display_thresholds=True):

        self.cam_width = cam_width
        self.cam_height = cam_height
        self.hue_min = hue_min
        self.hue_max = hue_max
        self.sat_min = sat_min
        self.sat_max = sat_max
        self.val_min = val_min
        self.val_max = val_max
        self.display_thresholds = display_thresholds

        self.capture = None  # camera 
        self.channels = {
            'hue': None,
            'saturation': None,
            'value': None,
            'laser': None,
        }

    def create_and_position_window(self, name, xpos, ypos):
        cv2.namedWindow(name)
        cv2.resizeWindow(name, self.cam_width, self.cam_height)
        cv2.moveWindow(name, xpos, ypos)

    def setup_camera_capture(self, device_num):
        try:
            pass
            #device = int(device_num)
            #sys.stdout.write("Using Camera Device: {0}\n".format(device_num))
        except (IndexError, ValueError):
            device_num = ""
            #sys.stderr.write("Invalid Device. Using default device 0\n")

        self.capture = cv2.VideoCapture(device_num)
        if not self.capture.isOpened():
            sys.stderr.write("Faled to Open Capture device. Quitting.\n")
            sys.exit(1)

        self.capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.cam_width
        )
        self.capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.cam_height
        )
        return self.capture

    def handle_quit(self, delay=10):
        key = cv2.waitKey(delay)
        c = chr(key & 255)
        if c in ['q', 'Q', chr(27)]:
            sys.exit(0)

    def threshold_image(self, channel):
        if channel == "hue":
            minimum = self.hue_min
            maximum = self.hue_max
        elif channel == "saturation":
            minimum = self.sat_min
            maximum = self.sat_max
        elif channel == "value":
            minimum = self.val_min
            maximum = self.val_max

        (t, tmp) = cv2.threshold(
            self.channels[channel], 
            maximum, # threshold 
            0, 
            cv2.THRESH_TOZERO_INV 
        )

        (t, self.channels[channel]) = cv2.threshold(
            tmp,
            minimum, 
            255,
            cv2.THRESH_BINARY 
        )

        if channel == 'hue':
            self.channels['hue'] = cv2.bitwise_not(self.channels['hue'])


    def detect(self, frame):
        global laser
        global pts
        global detected
        global maxlen
        global radius
        global circle_pos
        global laser_position
        global boundary_x
        global boundary_y
        global X, Y
        global center
        global stop_trigger, send_trigger
        global y_border_trig         
        global x_border_trig 
        global border_trigger
        #Point pt;
        #pt.x = 10;
        #pt.y = 8;
        frame = imutils.resize(frame, width=600)
        
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # diaxorismos tou video se xrwmatika kanalia
        h, s, v = cv2.split(hsv_img)
        self.channels['hue'] = h
        self.channels['saturation'] = s
        self.channels['value'] = v

        # thresholds twn HSV
        self.threshold_image("hue")
        self.threshold_image("saturation")
        self.threshold_image("value")

        # AND se HSV gia entopismo laser
        self.channels['laser'] = cv2.bitwise_and(
            self.channels['hue'],
            self.channels['value']
        )
        self.channels['laser'] = cv2.bitwise_and(
            self.channels['saturation'],
            self.channels['laser']
        )

        # sigxoneush HSV
        hsv_image = cv2.merge([self.channels['hue'],self.channels['saturation'],self.channels['value'],])
        
       
        (_, cnts, _) = cv2.findContours(self.channels['laser'].copy(), cv2.RETR_EXTERNAL,
         cv2.CHAIN_APPROX_SIMPLE)
        
        if len(cnts) > 0:
    		c = max(cnts, key=cv2.contourArea)
    		(circle_pos, radius) = cv2.minEnclosingCircle(c)
    		M = cv2.moments(c)
      
    		if (M["m10"] != 0) or (M["m00"] != 0) or (M["m01"] != 0):  
    			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    			laser = center
		else:  
    		     laser = circle_pos
    		     #msg = "laser too far"
           
    		# elegxos megethos laser
    		if True:#radius > 5:
    			
    			cv2.circle(frame, (int(laser[0]), int(laser[1])), int(radius),
    				(0, 255, 255), 2)
    			cv2.circle(frame, center, 5, (0, 0, 255), -1) 
    			laser = center
    			detected = "Yes"
                cv2.line(frame,(300,230),laser,(0,255,0),5)
            #else:
                #print 'Laser Lost'
    			#detected = "No"
    			#area = ""

        
    		if laser != None and boundary_x != None:
    		  #stop_trigger = True 
    		  if x_border_trig == True or y_border_trig == True:
    			#print 'outside border'
    			stop_trigger = False
    			#ser.write( X + "-" + Y + "'\n")
    		  elif border_trigger == False or y_border_trig == False:
    			if stop_trigger == False:
    			  # print 'inside border'
    			   stop_trigger = True

       
    		  if laser[1] > boundary_x[1]: 
    			X = "D"
    			x_border_trig = True
    			cv2.line(frame,(300,230),laser,(150,0,255),5)        
       
    		  if laser[1] < boundary_y[1]:
    			X = "U"
    			x_border_trig = True
    			cv2.line(frame,(300,230),laser,(0,0,255),5) 
       
    		  if laser[1] > boundary_y[1] and laser[1] < boundary_x[1]: #inside square
    			X = "-"       
    			x_border_trig = False
    		  if laser[0] >  boundary_x[0]:
    			Y = "-"             
    			y_border_trig = False 
       
    		  if laser[0] > boundary_y[0]:
    			Y = "R" 
    			y_border_trig = True
    			cv2.line(frame,(300,230),laser,(0,0,255),5) 
       
    		  if laser[0] < boundary_y[0] and laser[0] < boundary_x[0]:
    			Y = "L" 
    			y_border_trig = True 
       
#    		  else:  #laser pointer outside the square
#    			send_trigger  = "-"
#    			print "inside square"                    

#    			if stop_trigger == True:
#    			   stop_trigger = False                       
        else:
           detected = "No"

           #laser_boundary= "-"
           
        laser_position = X + ":" + Y #+ ":" + L + ":" + R   

        cv2.putText(frame, "Last Point: {}".format(laser), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, "Detected: {}".format(detected), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, "Player A",(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        cv2.putText(frame, "Radius: {}".format(radius), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        #cv2.putText(frame, "{}".format(laser_position), (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                             #left#down #right#up  
        #cv2.rectangle(frame, boundary_x, boundary_y, 150,  thickness=3, lineType=3, shift=0)
        
        cen=300
        rad = 200
        for i in range(5):
            for j in range(2):
                cv2.circle(frame, (300, 230), rad, (0,0,0), 1)
                rad = (rad - 19)

        cv2.circle(frame, (cen, 230), 10, (0,0,0), 1)

        v = 230 - 12
        cv2.putText(frame, "X", (cen-4, 235), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
        for i in range(1,11):
            cv2.putText(frame, str(11-i), (cen-4, v), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
            v = v - 19

        #cv2.imshow('mask', self.channels['laser'])
        cv2.imshow('Laser Target Game', frame)
        return hsv_image

    def run(self):
        
        global cam_device
        self.setup_camera_capture(cam_device)

        while True:
            success, frame = self.capture.read()
            if not success: 
                self.setup_camera_capture(1)
                success, frame = self.capture.read()

            hsv_image = self.detect(frame)
            self.handle_quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Laser Target Game')
    parser.add_argument('-W', '--width',
        default=640,
        type=int,
        help='Camera Width'
    )
    parser.add_argument('-H', '--height',
        default=480,
        type=int,
        help='Camera Height'
    )

    params = parser.parse_args()

    tracker = LaserTracker(
        cam_width=params.width,
        cam_height=params.height,
        hue_min=20,
        hue_max=160,
        sat_min=100,
        sat_max=255,
        val_min=200,
        val_max=255,
        display_thresholds=False
    )
    tracker.run()
