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

rMin = 255
gMax = 0
bMax = 0

for x in range(320):
    for y in range(240):
        if data[y,x,0] < rMin:
            rMin = data[y,x,0]
        if data[y,x,1] > gMax:
            gMax = data[y,x,1]
        if data[y,x,2] > bMax:
            bMax = data[y,x,2]
            
print ('Minimum Red: ', rMin)
print ('Maximum Green: ', gMax)
print ('Maximum Blue: ', bMax)
        
#clear data to save memory / prevent CPU overload
data = np.empty((240,320,3), dtype=np.uint8)
        
