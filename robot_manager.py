#import required modules
import time
import mini_driver
import RPi.GPIO as GPIO
import sys
from picamera import PiCamera
import numpy as np

import matplotlib as mpl
mpl.use('agg')     #using this the image will not appear as expected
#mpl.use('TkAgg')    #using this the image will appear but an error with the TKinter library will intermittently stop the program
import matplotlib.pyplot as plt

#sys.path.append(r'/home/pi/quick2wire-python-api')

#from i2clibraries import i2c_hmc5883l

global balloonFound
balloonFound = False
global balloonDirection
balloonDirection = 0       # 0 is straight, 1 is left, 2 is right

def connect():
    
    #connect to mini_driver
    global miniDriver
    miniDriver = mini_driver.MiniDriver()
    global connected
    connected = miniDriver.connect()
    print "Connected = ", connected
    
    GPIO.output(9, True)
    GPIO.output(11,True)
    
def disconnect():
    
    #disconnect miniDriver
    global miniDriver
    miniDriver.disconnect()
    del miniDriver
    
def setupGPIO():
    
    #tells the GPIO library to use the GPIO references not the pin numbers
    
    GPIO.setmode(GPIO.BCM)

    #set up berryclip
    #sets the buttons to inputs
    GPIO.setup(7 , GPIO.IN)    #black button
    GPIO.setup(25, GPIO.IN)    #red button
    
    #sets the LEDs to outputs and to off
    GPIO.setup(4, GPIO.OUT)    #red
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(22, GPIO.OUT)   #yellow
    GPIO.setup(10, GPIO.OUT)
    GPIO.setup(9, GPIO.OUT)    #green
    GPIO.setup(11, GPIO.OUT)
    
    GPIO.output(4, False)
    GPIO.output(17, False)
    GPIO.output(22, False)
    GPIO.output(10, False)
    GPIO.output(9, False)
    GPIO.output(11, False)
    
    #set up distance sensors
    #set triggers to outputs
    GPIO.setup(18, GPIO.OUT)   #front right
    GPIO.setup(20, GPIO.OUT)   #front left
    GPIO.setup(16, GPIO.OUT)   #back
    
    #set echos to inputs
    GPIO.setup(24, GPIO.IN)    #front right
    GPIO.setup(21, GPIO.IN)    #front left
    GPIO.setup(26, GPIO.IN)    #back
    
    print "Setup GPIO pins as inputs and outputs"
    
    GPIO.output(18, GPIO.LOW)
    GPIO.output(20, GPIO.LOW)
    GPIO.output(16, GPIO.LOW)
    
    print "Waiting for sensors to settle"
    
    global objectDetected
    global objectDetectedBack
    objectDetected = False
    objectDetectedBack = False
    
def setupMotors():
    
    #sets front wheels to face forward
    #experimentally determined that the value for the wheel servo centre was ~70,
    #changed it to 71 to try to stop it twitching as much
    
    #sets the poke servo to the back position, I put the stick all the way back
    #when it's at this angle to do this
    
    if connected:
        miniDriver.setOutputs( 0, 0, 70, 130)
        
def setupCamera():
    global camera
    camera = PiCamera()
    
    
def forward(t):
    
    #robot moves straight forward for a number of ~4cm intervals or
    #until it bumps into something then stops
    
    global objectDetected
      
    if connected:
        
        x = 0
        
        findDistanceFront()
        if distance <= 30:
            objectDetected = True
            print "Object detected in front"
        
        while x < t and objectDetected == False:
            
            miniDriver.setOutputs( 50, 50, 70, 130)
            GPIO.output(22, True)       #flash both orange LEDs and wait 0.1s
            GPIO.output(10, True) 
            time.sleep(0.05)
            GPIO.output(22, False)
            GPIO.output(10, False)
            time.sleep(0.05)
            
            x += 1
            
            findDistanceFront()
            if distance <= 30:
                objectDetected = True
                print "Object detected in front"
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()   #resets GPIO settings
                disconnect()
                break
            
        miniDriver.setOutputs( 0, 0, 70, 130)
        time.sleep(0.5)
        
def reverse(t):
    
    #robot moves straight backward for a time in seconds then stops
    
    global objectDetectedBack
    
    if connected:
        
        x = 0
        
        findDistanceBack()
        if distanceBack <= 20:
            objectDetectedBack = True
        
        while x < t and objectDetectedBack == False:
            miniDriver.setOutputs( -35, -35, 70, 130)
            GPIO.output(22, True)       #flash both orange LEDs and wait 0.1s
            GPIO.output(10, True) 
            time.sleep(0.05)
            GPIO.output(22, False)
            GPIO.output(10, False)
            time.sleep(0.05)
            
            x += 1
            
            findDistanceBack()
            if distanceBack <= 20:
                objectDetectedBack = True
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()   #resets GPIO settings
                disconnect()
                break
            
        miniDriver.setOutputs( 0, 0, 70, 130)
        
def moveLeft(t):
    
    #robot moves forward and left for a time in seconds then stops
    
    if connected:
        for x in range (t):
            miniDriver.setOutputs( 50, 50, 50, 130)
            GPIO.output(10, True)     #flash one orange LED and wait 1s
            time.sleep(0.15)
            GPIO.output(10, False)
            time.sleep(0.15)
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()   #resets GPIO settings
                disconnect()
                break

        miniDriver.setOutputs( 0, 0, 70, 130)
        
def moveRight(t):
    
    #robot moves forward and right for time in seconds
    
    if connected:  
        for x in range (t):
            miniDriver.setOutputs( 50, 50, 90, 130)
            GPIO.output(10, True)     #flash one orange LED and wait 0.3s
            time.sleep(0.15)
            GPIO.output(10, False)
            time.sleep(0.15)
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()   #resets GPIO settings
                disconnect()
                break

        miniDriver.setOutputs( 0, 0, 70, 130)
        
def rotateLeft(t):
    
    #robot turns left on the spot, pivoting about the left wheel.
    
    global objectDetectedBack
        
    if connected:
        
        x = 0
        
        findDistanceBack()
        if distanceBack <= 20:
            objectDetectedBack = True
        
        
        while x < t and objectDetectedBack == False:
            miniDriver.setOutputs( -50, 50, 140, 130)
            GPIO.output(22, True)     #flash other orange LED and wait 0.1s
            time.sleep(0.15)
            GPIO.output(22, False)
            time.sleep(0.15)
            
            x += 1
            
            findDistanceBack()
            if distanceBack <= 20:
                objectDetectedBack = True
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()   #resets GPIO settings
                disconnect()
                break
            
            if x < t:
                moveLeft(t-x)
            
        miniDriver.setOutputs( 0, 0, 70, 130)
        objectDetectedBack = False
        
def rotateRight(t):
    
    #robot turns right on the spot, pivoting about the right wheel.
    
    global objectDetectedBack
        
    if connected:
        
        x = 0
        
        findDistanceBack()
        if distanceBack <= 10:
            objectDetectedBack = True
            print "Object detected behind"
        
        while x < t and objectDetectedBack == False:
            
            #time.sleep(0.2)
            miniDriver.setOutputs( 50, -50, 7, 130)
            GPIO.output(22, True)     #flash other orange LED and wait 0.3s
            time.sleep(0.15)
            GPIO.output(22, False)
            time.sleep(0.15)
            
            x += 1
            print("x = ", x)
            findDistanceBack()
            if distanceBack <= 10:
                objectDetectedBack = True
                print "Object detected behind"
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()   #resets GPIO settings
                disconnect()
                break
            
        if x < t:
            moveRight(t-x)
            
        miniDriver.setOutputs( 0, 0, 70, 130)
        objectDetectedBack = False
        
def circleCW():
    
    print "Initiating circle..."
    time.sleep(1.0)
    moveRight(7)
    
def circleACW():
    
    print "Initiating circle..."
    time.sleep(1.0)
    moveLeft(7)
    
def square():
    
    for x in range (4):
        rotateRight(42)
        time.sleep(0.5)   #here in the 360 degree rotation will be the searching part.
        rotateRight(12)
        forward(10)
    
def poke(n):
    
    print "Popping..."
    for x in range (n):
        miniDriver.setOutputs( 0, 0, 70, 0)
        time.sleep(0.5)
        miniDriver.setOutputs(0, 0, 70, 130)
        time.sleep(0.5)
        
def findDistanceFront():
    
    global distance
    
    GPIO.output(18, GPIO.HIGH)
    time.sleep(0.00001)        #distance sensor requires pulse of 1 nanosecond to trigger it
    GPIO.output(18, GPIO.LOW)
    
    testTime = time.time()
    
    while GPIO.input(24) == 0 and (time.time() - testTime) < 1: 
        pulseStartTime = time.time()
    while GPIO.input(24) == 1 and (time.time() - testTime) < 2:
        pulseEndTime = time.time()
        
    if (time.time() - testTime) > 1:
        print "Echo not detected"
        dist1 = 1000
    else:
        try:
            pulseDuration = pulseEndTime - pulseStartTime
            dist1 = round(pulseDuration * 17150, 2)
            print "Right distance: ", dist1, "cm"
        except Exception as e:
            print "Error calculating distance: ", e
            dist1 = 1000
        
        #speed of ultrasonic sound ~34300cm/s
        #divide by 2 as going there and back
    
    GPIO.output(20, GPIO.HIGH)
    time.sleep(0.00001)        #distance sensor requires pulse of 1 nanosecond to trigger it
    GPIO.output(20, GPIO.LOW)
    
    testTime = time.time()
    
    while GPIO.input(21) == 0 and (time.time() - testTime) < 1:
        pulseStartTime = time.time()
    while GPIO.input(21) == 1 and (time.time() - testTime) < 2:
        pulseEndTime = time.time()
        
    if (time.time() - testTime) > 1:
        print "Echo not detected"
        dist2 = 1000
    else:
        try:
            pulseDuration = pulseEndTime - pulseStartTime
            dist2 = round(pulseDuration * 17150, 2)
            print "Left distance: ", dist2, "cm"
        except Exception as e:
            print "Error calculating distance: ", e
            dist2 = 1000
    
    if dist1 < dist2:
        distance = dist1
        print "Using right distance: ", dist1, "cm"
    else:
        distance = dist2
        print "Using left distance: ", dist2, "cm"
        
def findDistanceBack():
    
    global distanceBack
    
    GPIO.output(16, GPIO.HIGH)
    time.sleep(0.00001)        #distance sensor requires pulse of 1 nanosecond to trigger it
    GPIO.output(16, GPIO.LOW)
    
    testTime = time.time()
    
    while GPIO.input(26) == 0 and (time.time() - testTime) < 1:
        pulseStartTime = time.time()
    while GPIO.input(26) == 1 and (time.time() - testTime) < 2:
        pulseEndTime = time.time()
        
    if (time.time() - testTime) > 1:
        print "Echo not detected"
        distanceBack = 1000
    else:
        try:
            pulseDuration = pulseEndTime - pulseStartTime
            distanceBack = round(pulseDuration * 17150, 2)
            print "Distance backward: ", distanceBack, "cm"
        except Exception as e:
            print "Error calculating distance: ", e
            distanceBack = 1000
    
def searchPattern1():    #simple just doesn't bump into anything (hopefully) program
    
    global objectDetected
    global objectDetectedBack
    
    for x in range (5):
        forward(25)
        if objectDetected == True:
            #check if it's a balloon, if it is pop it, else continue

            rotateRight(10)
            objectDetected = False
            objectDetectedBack = False
    
    print "Finished search pattern"
    
def searchPattern2():    #spiral search pattern that pops balloons

    print "Beginning spiral search pattern..."
    
    spiralAngle = 270
    
    global objectDetected
    objectDetected = False
    global objectDetectedBack
    objectDetectedBack = False
    
    while spiralAngle > 0:     
        rotationAngle = 0
        while rotationAngle < 360:
            findBalloon()
            if balloonFound == True:
                GPIO.output(4, True)   #turn on red LED to show possible balloon found
                if balloonSmall == True:
                    forward(12)      #get closer before lining the angle up
                    findBalloon()
                
                x = 0
                while balloonDirection != 0 and x < 15:       #stop infinite loop by adding a counter
                    if balloonDirection == 1:
                        rotateLeft(1)
                        findBalloon()
                    elif balloonDirection == 2:
                        rotateRight(1)
                        findBalloon()
                    elif balloonDirection == 3:     # can no longer see balloon
                        rotateRight(3)         #rotate further to help find balloon
                        findBalloon()
                        x += 1
                        
                findBalloon()
                if balloonFound == True:
                    approach()
                    findBalloon()            #checks balloon is still in view
                    if balloonFound == True:
                        poke(2)
                GPIO.output(4, False)
                reverse(distanceApproached)
            rotateRight(3)
            rotationAngle +=30
        rotateRight(int(spiralAngle/10))
        spiralAngle -=30
        forward(16)
        if objectDetected == True:
            rotateRight(10)
            objectDetected = False
            objectDetectedBack = False
    
    print "Finished search pattern"
        
def approach():
    
    global distanceApproached
    distanceApproached = 0     #counting how far it's gone forward so it can reverse afterwards
    #findDistanceFront()
    #startDistance = distance    #starting distance to object as it was overshooting sometimes
    
    if connected:
        
        x = 0
        balloonClose = False
        
        findDistanceFront()
        if distance <= 4:
            balloonClose = True
            
        print "Approaching balloon"
        
        while balloonClose == False: # and distanceApproached*8 < startDistance:     # 8cm per loop roughly
            
            miniDriver.setOutputs( 35, 35, 70, 130)
            GPIO.output(22, True)       #flash both orange LEDs and wait 0.1s
            GPIO.output(10, True) 
            time.sleep(0.05)
            GPIO.output(22, False)
            GPIO.output(10, False)
            time.sleep(0.05)
            
            x += 1
            distanceApproached += 1
            
            findDistanceFront()
            if distance <= 4:
                balloonClose = True
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()   #resets GPIO settings
                disconnect()
                break
        
        
        miniDriver.setOutputs( 0, 0, 70, 130)
        time.sleep(0.5)
    
def takeImage():
    camera.resolution = (2560,1936)
    camera.start_preview()
    time.sleep(5)
    camera.capture('/home/pi/Documents/Images/test.jpg')
    camera.stop_preview()
    
    
def findBalloon():
    
    global balloonFound
    global balloonDirection
    global balloonSmall
    
    #plt.ion()
    
    xRes = 160
    yRes = 128
    
    camera.resolution = (xRes, yRes)
    data = np.empty((yRes*xRes*3), dtype=np.uint8)    # preallocate image
    threshold = np.empty((yRes,xRes), dtype=bool)
    
    mpl.rcParams['toolbar'] = 'None'      #remove axes and toolbar as unnecessary
    
    try:
        print "Capturing image"
        camera.capture('/home/pi/Documents/Images/fullView.jpg')   #save full colour image
        camera.capture(data,'rgb') #capture RGB image
    
        data = data.reshape((yRes,xRes,3))
        
        

        # creates array of bools for correct colour
        if balloonColour == 1:  #(red)
            rMin = 55
            for x in range(xRes):
                for y in range(yRes):
                    if data[y,x,0] > rMin:
                        gMax = int(data[y,x,0]*0.7)
                        bMax = int(data[y,x,0]*0.75)
                        if data[y,x,1] < gMax and data[y,x,2] < bMax:
                            threshold[y,x] = True
                        else:
                            threshold[y,x] = False
                    else:
                        threshold[y,x] = False
        
        elif balloonColour == 2: #(blue)
            bMin = 40
            rMax = 10
            for x in range(xRes):
                for y in range(yRes):
                    if data[y,x,2] > bMin:
                        gMax = int(data[y,x,2]*0.75)
                        if data[y,x,1] < gMax and data[y,x,0] < rMax:
                            threshold[y,x] = True
                        else:
                            threshold[y,x] = False
                    else:
                        threshold[y,x] = False
                    
        #lowers the noise
        for x in range(xRes):
            for y in range(yRes):
                if x > 0 and x < (xRes - 1) and y > 0 and y < (yRes - 1):  #if it's not a border pixel
                    if threshold[y-1,x] == False and threshold[y+1,x] == False:
                        threshold[y,x] = False
                    elif threshold[y,x-1] == False and threshold[y,x+1] == False:
                        threshold[y,x] = False
                    elif threshold[y-1,x] == True and threshold[y+1,x] == True and threshold[y,x-1] == True and threshold[y,x+1] == True:
                        threshold[y,x] = True
                else:
                    threshold[y,x] = False      #set border pixels to false
        
        #turns the array of bools back into rgb to be displayed
        for x in range(xRes):
            for y in range(yRes):
                if threshold[y,x] == True:
                    data[y,x,0] = 250
                    data[y,x,1] = 0
                    data[y,x,2] = 0
                else:
                    data[y,x,0] = 0
                    data[y,x,1] = 0
                    data[y,x,2] = 0
                    
        #finds and marks centre of balloon
        
        xMax = 0
        yCentre = 0
        for y in range(yRes):
            xCurrent = 0
            for x in range(xRes):
                if threshold[y,x] == True:
                    xCurrent += 1
                elif xCurrent > xMax:
                    xMax = xCurrent
                    yCentre = y
                    xCurrent = 0
                else:
                    xCurrent = 0
        
        yMax = 0
        xCentre = 0
        for x in range(xRes):
            yCurrent = 0
            for y in range(yRes):
                if threshold[y,x] == True:
                    yCurrent += 1
                elif yCurrent > yMax:
                    yMax = yCurrent
                    xCentre = x
                    yCurrent = 0
                else:
                    yCurrent = 0
        
        data[yCentre,xCentre,0] = 0
        data[yCentre,xCentre,1] = 0
        data[yCentre,xCentre,2] = 250
        data[yCentre+1,xCentre,0] = 0
        data[yCentre+1,xCentre,1] = 0
        data[yCentre+1,xCentre,2] = 250
        data[yCentre-1,xCentre,0] = 0
        data[yCentre-1,xCentre,1] = 0
        data[yCentre-1,xCentre,2] = 250
        data[yCentre,xCentre+1,0] = 0
        data[yCentre,xCentre+1,1] = 0
        data[yCentre,xCentre+1,2] = 250
        data[yCentre,xCentre-1,0] = 0
        data[yCentre,xCentre-1,1] = 0
        data[yCentre,xCentre-1,2] = 250

      #  print("pixels across: ", xMax)
      #  print("pixels up: ", yMax)
      
        if xMax >= 20 and yMax >=20:
            balloonFound = True
            print "Balloon found"
            if xCentre > (xRes/2) + 15:
                balloonDirection = 2      # 0 for straight, 1 for left, 2 for right
            elif xCentre < (xRes/2) - 15:
                balloonDirection = 1
            else:
                balloonDirection = 0
            if xMax <= 80 and yMax <= 80:      #detects distance to balloon so if it's too far away we approach before refining angle
                balloonSmall = True
            else:
                balloonSmall = False
        else:
            balloonFound = False
            balloonDirection = 3
        
        plt.imshow(data)   #plots data
        plt.axis('off')    #removes axes
        
        #clear data to save memory / prevent CPU overload
        data = np.empty((yRes,xRes,3), dtype=np.uint8)
        
        plt.savefig('/home/pi/Documents/Images/RedBlack.png', dpi=150)
        print "image saved"
        
        plt.show(block=False)
        time.sleep(3)
        plt.close()
        plt.cla()
        
        if GPIO.input(25) == 1:
            print "Stopping..."
            GPIO.output(9, False)
            GPIO.output(11,False)
            GPIO.cleanup()   #resets GPIO settings
            disconnect()
            
        
    except Exception as e:
        print "Error taking image: ", e
            
#-------------------------------------------------------------------------------------------
    
#main program

        
print "This program is set up to search for balloons and pop them."

global balloonColour
balloonColour = int(input("What colour balloon do you want to search for? Enter 1 for red, 2 for blue: "))
if balloonColour == 1:
    print "Red balloons selected."
elif balloonColour == 2:
    print "Blue balloons selected."
else:
    print "Incorrect value entered. Please restart the program."
    sys.exit()
    
print "Please wait for the program to finish initialisation and give further instructions."
        
setupGPIO()
connect()
setupMotors()
setupCamera()

print "Press the black button initiate the search pattern."
print "Press the red button to stop the program."
    
while True:
        
    if GPIO.input(7) == 1:
        searchPattern2()
            
    if GPIO.input(25) == 1:
        print "Stopping..."
        GPIO.output(9, False)
        GPIO.output(11,False)
        GPIO.cleanup()   #resets GPIO settings
        disconnect()
        break
    
print "Program stopped."
    

        
        


