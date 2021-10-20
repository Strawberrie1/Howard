# Import required modules
import time
import mini_driver
import RPi.GPIO as GPIO
import sys
from picamera import PiCamera
import numpy as np

import matplotlib as mpl
mpl.use('agg')       # Using this setting the image will not appear as expected
#mpl.use('TkAgg')    # Using this setting the image will appear but an error
                     # with the TKinter library will intermittently stop the program
import matplotlib.pyplot as plt

global balloonFound
balloonFound = False
global balloonDirection
balloonDirection = 0       # 0 is straight, 1 is left, 2 is right

def connect():             # Connect to mini driver board
    
    global miniDriver
    miniDriver = mini_driver.MiniDriver()
    global connected
    connected = miniDriver.connect()
    print "Connected = ", connected
    
    GPIO.output(9, True)
    GPIO.output(11,True)
    
def disconnect():          # Disconnect from mini driver board
    
    global miniDriver
    miniDriver.disconnect()
    del miniDriver
    
def setupGPIO():
    
    # Tells the GPIO library to use the GPIO references not the pin numbers
    
    print "Setting up the GPIO pins as inputs and outputs"
    GPIO.setmode(GPIO.BCM)

    # Set up the Berryclip board
    # Set the buttons to inputs
    GPIO.setup(7 , GPIO.IN)    # Black button
    GPIO.setup(25, GPIO.IN)    # Red button
    
    # Set the LEDs to outputs
    GPIO.setup(4, GPIO.OUT)    # Red
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(22, GPIO.OUT)   # Yellow
    GPIO.setup(10, GPIO.OUT)
    GPIO.setup(9, GPIO.OUT)    # Green
    GPIO.setup(11, GPIO.OUT)
    
    # Set the LEDs to off
    GPIO.output(4, False)
    GPIO.output(17, False)
    GPIO.output(22, False)
    GPIO.output(10, False)
    GPIO.output(9, False)
    GPIO.output(11, False)
    
    # Set up the distance sensors
    # Set the triggers to outputs
    GPIO.setup(18, GPIO.OUT)   # Front right
    GPIO.setup(20, GPIO.OUT)   # Front left
    GPIO.setup(16, GPIO.OUT)   # Back
    
    # Set the echos to inputs
    GPIO.setup(24, GPIO.IN)    # Front right
    GPIO.setup(21, GPIO.IN)    # Front left
    GPIO.setup(26, GPIO.IN)    # Back

    # Make sure the sensors aren't powered
    GPIO.output(18, GPIO.LOW)
    GPIO.output(20, GPIO.LOW)
    GPIO.output(16, GPIO.LOW)
    
    print "Waiting for the sensors to settle"
    
    global objectDetected
    global objectDetectedBack
    objectDetected = False
    objectDetectedBack = False
    
def setupMotors():
    
    # Sets front wheels to face forward
    # Experimentally determined that the value for the wheel servo centre was 70
    
    # Sets the poking servo to the back position,
    # I put the stick all the way back when it's at this angle to do this
    
    # miniDriver.setOutputs takes arguements in the following order:
    # (leftSpeed, rightSpeed, wheelAngle, pokeAngle)
    
    if connected:
        miniDriver.setOutputs( 0, 0, 70, 130)
        
def setupCamera():         # Connects to the camera
    
    global camera
    camera = PiCamera()
    
    
def forward(t):
    
    # The robot moves straight forward for a number of ~4cm intervals or
    # until it bumps into something then stops
    
    global objectDetected
      
    if connected:
        
        x = 0
        
        findDistanceFront()             # Check if there is an object in front
        if distance <= 30:
            objectDetected = True
            print "Object detected in front"
        
        while x < t and objectDetected == False:
            
            miniDriver.setOutputs( 50, 50, 70, 130)    # Starts the movement
            GPIO.output(22, True)       
            GPIO.output(10, True) 
            time.sleep(0.05)
            GPIO.output(22, False)
            GPIO.output(10, False)
            time.sleep(0.05)            # Flash both orange LEDs and wait 0.1s
            
            x += 1
            
            findDistanceFront()         # Check if there is an object in front
            if distance <= 30:
                objectDetected = True
                print "Object detected in front"
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()          # Resets GPIO settings
                disconnect()
                break
            
        miniDriver.setOutputs( 0, 0, 70, 130)    # Stops the movement
        time.sleep(0.5)
        
def reverse(t):
    
    # The robot moves straight backward for a number of ~4cm intervals or
    # until it bumps into something then stops
    
    global objectDetectedBack
    
    if connected:
        
        x = 0
        
        findDistanceBack()              # Check if there is an object behind
        if distanceBack <= 20:
            objectDetectedBack = True
        
        while x < t and objectDetectedBack == False:
            
            miniDriver.setOutputs( -35, -35, 70, 130)   # Starts the movement
            GPIO.output(22, True)       
            GPIO.output(10, True) 
            time.sleep(0.05)
            GPIO.output(22, False)
            GPIO.output(10, False)
            time.sleep(0.05)            # Flash both orange LEDs and wait 0.1s
            
            x += 1
            
            findDistanceBack()          # Check if there is an object behind
            if distanceBack <= 20:
                objectDetectedBack = True
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()          # Resets GPIO settings
                disconnect()
                break
            
        miniDriver.setOutputs( 0, 0, 70, 130)           # Stops the movement
        
def moveLeft(t):
    
    # The robot moves forward and left for a time in seconds then stops
    
    if connected:
        for x in range (t):
            
            miniDriver.setOutputs( 50, 50, 50, 130)     # Starts the movement
            GPIO.output(10, True)     
            time.sleep(0.15)
            GPIO.output(10, False)
            time.sleep(0.15)             # Flashes one orange LED and wait 0.3s
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()           # Resets GPIO settings
                disconnect()
                break

        miniDriver.setOutputs( 0, 0, 70, 130)           # Stops the movement
        
def moveRight(t):
    
    # The robot moves forward and right for time in seconds then stops
    
    if connected:  
        for x in range (t):
            
            miniDriver.setOutputs( 50, 50, 90, 130)     # Starts the movement
            GPIO.output(10, True)     
            time.sleep(0.15)
            GPIO.output(10, False)
            time.sleep(0.15)             # Flashes one orange LED and wait 0.3s
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()           # Resets GPIO settings
                disconnect()
                break

        miniDriver.setOutputs( 0, 0, 70, 130)           # Stops the movement
            
def rotateLeft(t):
    
    # The robot turns left on the spot for a number of ~10 degree intervals,
    # or until it bumps into something, pivoting about the left wheel.
    
    global objectDetectedBack
        
    if connected:
        
        x = 0
        
        findDistanceBack()                # Check if there is an object behind
        if distanceBack <= 20:
            objectDetectedBack = True
            print "Object detected behind"
        
        while x < t and objectDetectedBack == False:
            
            miniDriver.setOutputs( -50, 50, 140, 130)    # Starts the movement
            GPIO.output(22, True)     
            time.sleep(0.15)
            GPIO.output(22, False)
            time.sleep(0.15)              # Flash the second orange LED and wait 0.3s
            
            x += 1
            
            findDistanceBack()            # Check if there is an object behind
            if distanceBack <= 20:
                objectDetectedBack = True
                print "Object detected behind"
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()            # Resets GPIO settings
                disconnect()
                break
            
            if x < t:             # If it stops before finishing the rotation,
                moveLeft(t-x)     # it will rotate forwards instead
            
        miniDriver.setOutputs( 0, 0, 70, 130)            # Stops the movement
        objectDetectedBack = False
        
def rotateRight(t):
    
    # The robot turns right on the spot for a number of ~10 degree intervals,
    # or until it bumps into something, pivoting about the right wheel.
    
    global objectDetectedBack
        
    if connected:
        
        x = 0
        
        findDistanceBack()                 # Check if there is an object behind
        if distanceBack <= 10:
            objectDetectedBack = True
            print "Object detected behind"
        
        while x < t and objectDetectedBack == False:
            
            miniDriver.setOutputs( 50, -50, 7, 130)       # Starts the movement
            GPIO.output(22, True)          
            time.sleep(0.15)
            GPIO.output(22, False)
            time.sleep(0.15)               # Flash the second orange LED and wait 0.3s
            
            x += 1

            findDistanceBack()             # Check if there is an object behind
            if distanceBack <= 10:
                objectDetectedBack = True
                print "Object detected behind"
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()             # Resets GPIO settings
                disconnect()
                break
            
        if x < t:                          # If it stops before finishing the rotation,
            moveRight(t-x)                 # it will rotate forwards instead
            
        miniDriver.setOutputs( 0, 0, 70, 130)              # Stops the movement
        objectDetectedBack = False

# Simple movements for testing. Not used in the main program.

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
        time.sleep(0.5)   
        rotateRight(12)
        forward(10)
    
def poke(n):
    
    # Moves the pin forward then back, n is the number of pokes.
    
    print "Popping..."
    for x in range (n):
        miniDriver.setOutputs( 0, 0, 70, 0)
        time.sleep(0.5)
        miniDriver.setOutputs(0, 0, 70, 130)
        time.sleep(0.5)
        
def findDistanceFront():
    
    # Uses the front ultrasonic sensors to detect if there is an object
    # in front of the robot, and how far away it is
    
    global distance
    
    # Triggers the right distance sensor - it requires a pulse of 1 nanosecond to trigger it
    
    GPIO.output(18, GPIO.HIGH)   
    time.sleep(0.00001)          
    GPIO.output(18, GPIO.LOW)
    
    # Finds the time the echo took to come back
    
    testTime = time.time()
    
    while GPIO.input(24) == 0 and (time.time() - testTime) < 1: 
        pulseStartTime = time.time()
    while GPIO.input(24) == 1 and (time.time() - testTime) < 2:
        pulseEndTime = time.time()
        
    # Calculates the distance the object is away from the sensor
    # The speed of ultrasonic sound is ~34300cm/s, which is divided by 2
    # as the pulse goes there and back
        
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
            
    # If there is an error it assumes there is nothing in front of the sensor
            
    # Repeats this for the left sensor
    
    GPIO.output(20, GPIO.HIGH)
    time.sleep(0.00001)        
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
            
    # Returns the shorter of the two distances into the distance variable
    
    if dist1 < dist2:
        distance = dist1
        print "Using right distance: ", dist1, "cm"
    else:
        distance = dist2
        print "Using left distance: ", dist2, "cm"
        
def findDistanceBack():
    
    # Uses the back ultrasonic sensor to detect if there is an object
    # in front of the robot, and how far away it is.
    # Works in exactly the same way as the front ones, except it only
    # detects one distance and returns that.
    
    global distanceBack
    
    GPIO.output(16, GPIO.HIGH)
    time.sleep(0.00001)        
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
        
def approach():
    
    # A slower version of the forward() subroutine that moves until there is
    # something within 4cm of the robot
    
    global distanceApproached
    distanceApproached = 0     # It counts how far it's gone forward so it can reverse afterwards
    
    if connected:
        
        x = 0
        balloonClose = False
        
        findDistanceFront()            # Checks if there is anything in front
        if distance <= 4:
            balloonClose = True
            
        print "Approaching balloon"
        
        while balloonClose == False:
            
            miniDriver.setOutputs( 35, 35, 70, 130)   # Starts the movement
            GPIO.output(22, True)      
            GPIO.output(10, True) 
            time.sleep(0.05)
            GPIO.output(22, False)
            GPIO.output(10, False)
            time.sleep(0.05)            # Flashes both orange LEDs and wait 0.1s
            
            x += 1
            distanceApproached += 1
            
            findDistanceFront()         # Checks if there is anything in front
            if distance <= 4:
                balloonClose = True
            
            if GPIO.input(25) == 1:
                print "Stopping..."
                GPIO.output(9, False)
                GPIO.output(11,False)
                GPIO.cleanup()          # Resets GPIO settings
                disconnect()
                break
        
        
        miniDriver.setOutputs( 0, 0, 70, 130)         # Stops the movement
        time.sleep(0.5)
    
def takeImage():
    
    # Simple subroutine that shows a camera preview before taking an image and saving it
    # Unused in the final program
    
    camera.resolution = (2560,1936)
    camera.start_preview()
    time.sleep(5)
    camera.capture('/home/pi/Documents/Images/test.jpg')
    camera.stop_preview()
    
    
def findBalloon():
    
    # Detects if the correct colour and size object are in front of the robot
    # Finds the centre of the object if there is one
    # and calculates if it is directly in front of the robot
    # Depending on the mpl setting at the top of the code, may display the image
    # of what it is seeing as red on black with a blue cross
    
    global balloonFound
    global balloonDirection
    global balloonSmall
    
    # Prepare the camera and empty arrays to hold the rgb data in
    
    xRes = 160
    yRes = 128
    
    camera.resolution = (xRes, yRes)                 
    data = np.empty((yRes*xRes*3), dtype=np.uint8)    
    threshold = np.empty((yRes,xRes), dtype=bool)
    
    mpl.rcParams['toolbar'] = 'None'      # Remove the display's toolbar as unnecessary
    
    try:
        print "Capturing image"
        camera.capture('/home/pi/Documents/Images/fullView.jpg')   # Save a full colour image
        camera.capture(data,'rgb')                                 # Capture an RGB image
    
        data = data.reshape((yRes,xRes,3))

        # Creates an array of bools for correct colour
        # Red
        if balloonColour == 1:  
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
        
        # Blue
        elif balloonColour == 2: 
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
                    
        # Lowers the noise in the array
        for x in range(xRes):
            for y in range(yRes):
                if x > 0 and x < (xRes - 1) and y > 0 and y < (yRes - 1):  # If it's not a border pixel
                    if threshold[y-1,x] == False and threshold[y+1,x] == False:
                        threshold[y,x] = False
                    elif threshold[y,x-1] == False and threshold[y,x+1] == False:
                        threshold[y,x] = False
                    elif threshold[y-1,x] == True and threshold[y+1,x] == True and threshold[y,x-1] == True and threshold[y,x+1] == True:
                        threshold[y,x] = True
                else:
                    threshold[y,x] = False      # Sets border pixels to false
        
        # Turns the array of bools back into an RGB image to be displayed
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
                    
        # Finds the centre of the balloon
        
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
                    
        # Marks the centre as a blue cross on the display
        
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
        
        # Determines whether the object is large enough to be a balloon
        # Determines whether the balloon is straight ahead, to the left or to the right
      
        if xMax >= 20 and yMax >=20:
            balloonFound = True
            print "Balloon found"
            if xCentre > (xRes/2) + 15:
                balloonDirection = 2        # 0 for straight, 1 for left, 2 for right
            elif xCentre < (xRes/2) - 15:
                balloonDirection = 1
            else:
                balloonDirection = 0
            # Detects the distance to the balloon by its size so if it's too far away 
            # we approach before refining the angle
            if xMax <= 80 and yMax <= 80:      
                balloonSmall = True
            else:
                balloonSmall = False
        else:
            balloonFound = False
            balloonDirection = 3
        
        plt.imshow(data)   # Plots the data
        plt.axis('off')    # Removes the axes as unnecessary
        
        # Clear the data array to save memory / prevent CPU overload
        data = np.empty((yRes,xRes,3), dtype=np.uint8)
        
        # Saves the red and black figure
        plt.savefig('/home/pi/Documents/Images/RedBlack.png', dpi=150)
        print "image saved"
        
        # Displays the image if the settings are correct
        plt.show(block=False)
        time.sleep(3)
        plt.close()
        plt.cla()
        
        if GPIO.input(25) == 1:
            print "Stopping..."
            GPIO.output(9, False)
            GPIO.output(11,False)
            GPIO.cleanup()         # Resets GPIO settings
            disconnect()
            
    except Exception as e:
        print "Error taking image: ", e
        
def searchPattern1():
    
    # Simple movement program that just doesn't bump into anything (hopefully)
    # Not used in the final program
    
    global objectDetected
    global objectDetectedBack
    
    for x in range (5):
        forward(25)
        if objectDetected == True:
            rotateRight(10)
            objectDetected = False
            objectDetectedBack = False
    
    print "Finished search pattern"
    
def searchPattern2():
    
    # The final spiral search pattern that pops balloons

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
                GPIO.output(4, True)      # Turn on the red LED to show possible balloon found
                if balloonSmall == True:
                    forward(12)           # Get closer before lining the angle up
                    findBalloon()
                
                x = 0
                while balloonDirection != 0 and x < 15:    # Stop an infinite loop by adding a counter
                    if balloonDirection == 1:
                        rotateLeft(1)
                        findBalloon()
                    elif balloonDirection == 2:
                        rotateRight(1)
                        findBalloon()
                    elif balloonDirection == 3:     # Means it can no longer see the balloon
                        rotateRight(3)              # Rotate further to help find the balloon again
                        findBalloon()
                        x += 1
                        
                findBalloon()
                if balloonFound == True:
                    approach()
                    findBalloon()                   # Checks the balloon is still in view
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
            
#-------------------------------------------------------------------------------------------
    
# Main program
        
print "This program is set up to search for balloons and pop them."

global balloonColour
balloonColour = int(input("Which colour balloon do you want to search for? Enter 1 for red, 2 for blue: "))
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
print "Press and hold the red button until the green lights go off to stop the program."
    
while True:
        
    if GPIO.input(7) == 1:
        searchPattern2()
            
    if GPIO.input(25) == 1:
        print "Stopping..."
        GPIO.output(9, False)
        GPIO.output(11,False)
        GPIO.cleanup()         # Resets GPIO settings
        disconnect()
        break
    
print "Program stopped."
    

        
        


