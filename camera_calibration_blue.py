# Import required modules
import time
from picamera import PiCamera
import numpy as np

camera = PiCamera()
camera.resolution = (320, 240)

data = np.empty((240*320*3), dtype=np.uint8)    # preallocate image

camera.start_preview()
time.sleep(2)
camera.capture(data,'rgb') # capture RGB image
camera.capture('/home/pi/Documents/Images/red.jpg')
camera.stop_preview()

data = data.reshape((240,320,3))

bMin = 255
gMax = 0
rMax = 0

for x in range(320):
    for y in range(240):
        if data[y,x,2] < bMin:
            bMin = data[y,x,2]
        if data[y,x,1] > gMax:
            gMax = data[y,x,1]
        if data[y,x,0] > rMax:
            rMax = data[y,x,0]
            
print ('Minimum Blue: ', bMin)
print ('Maximum Green: ', gMax)
print ('Maximum Red: ', rMax)
        
#clear data to save memory / prevent CPU overload
data = np.empty((240,320,3), dtype=np.uint8)
        
