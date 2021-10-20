import smbus    #for I2C communication
import time
import math

# register addresses
regSet = 0x0B        # set/reset period register
regMode = 0x09       # mode register 
regStatus = 0x06     # status register


# connection
bus = smbus.SMBus(1)
deviceAddress = 0x1e

# data registers
xAxis = 0x00
yAxis = 0x02
zAxis = 0x04

declination = 0.75        # magnetic declination is measured in degrees and minutes, this is 45 minutes in degrees
pi = 3.14159265359

def magnetometerInit():
    #configure set reset register
    bus.write_byte_data(deviceAddress, regSet, 0x01)
    #configure mode register to 01 for continuous measurement
    bus.write_byte_data(deviceAddress, regMode, 0x1D)
    

   
def readRawData(address):
    #read raw 16 bit value
    low = bus.read_byte_data(deviceAddress, address)
    high = bus.read_byte_data(deviceAddress, address + 1)
    
    # concatenate higher and lower value
    value = ((high << 8) | low)
    
    # get signed value from module
    if (value > 32768):
        value = value - 65536
    return value

# main

magnetometerInit()
print ("reading magnetometer")

while True:
    
   # flag = bus.read_byte_data(deviceAddress, regStatus)
   # a = "{0:b}".format(flag)
   # if a[len(a)-1] == 0:
   #     flag = bus.read_byte_data(deviceAddress, regStatus)
    
    x=readRawData(xAxis)
    y=readRawData(yAxis)
    z=readRawData(zAxis)
    
    print(x,y,z)
    
    heading = math.atan2(y,x) + declination
    
    # check for >360 and <0 degrees
    if (heading > 2*pi):
        heading = heading - 2*pi
    if (heading < 0):
        heading = heading + 2*pi
        
    #convert to degrees from rad
    headingAngle = int(heading * 180/pi)
    
    print ("Angle = ", headingAngle)
    time.sleep(1)





    
