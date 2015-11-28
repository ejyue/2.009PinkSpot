
import serial 
from time import sleep
count = 0
port =  "/dev/tty.usbmodem1421"

ser  = serial.Serial(port, 9600, timeout= 0 ) #start the serial port communication

ser.close()
ser.open()

while count < 25:
    count+=1
    data = ser.read(9999)

    print len(data)
    sleep(.1)
