import math
import serial 
from time import sleep

"""
install pyserial to run the code. go to the link below to install:
https://learn.adafruit.com/arduino-lesson-17-email-sending-movement-detector/overview
"""

#######################################################################################
## data info
## dist1 on line 1  : int(data[6:14], 16)     NONE
## dist2 on line 1  : int(data[15:23], 16)    anchor 0 to 1
## dist3 on line 1  : int(data[24:32], 16)    anchor 0 to 2 
## dist4 on line 1  : int(data[33:41], 16)    anchor 1 to 2 
## dist1 on line 2  : int(data[71:79], 16)    tag to anchor 0 
## dist2 on line 2  : int(data[80:88], 16)    tag to anchor 1
## dist3 on line 2  : int(data[89:97], 16)    tag to anchor 2
## dist4 on line 2  : int(data[98:106], 16)   tag to anchor 3 
#######################################################################################
        

def distance(one, two):
    return ((one[0]-two[0])**2 + (one[1]-two[1])**2 + (one[2]-two[2])**2)**.5

def LawofCosines(Aop,Bop,Cop):
    return math.acos((Aop**2 + Bop**2 - Cop**2)/ (2 * Aop * Bop) )

def Loc_3D(dist0, dist1, dist2, Loc_1, Loc_2):
    """
    Uses Trilateration to return 3 coordinate points from Anchor position and distances
    """
    Position = []
    Position.append((dist0**2 - dist1**2 + Loc_1[0]**2)/ (2*Loc_1[0]))
    Position.append((dist0**2 - dist2**2 - Position[0]**2 +(Position[0]-Loc_2[0])**2 + Loc_2[1]**2)/(2*Loc_2[1]))

    #To avoid square rooting negative number when z = 0, but range of tracking error gives small negative value under intercept
    if (dist0**2 - Position[0]**2 - Position[1]**2) >= 0 :
        
        Position.append((dist0**2 - Position[0]**2 - Position[1]**2)**.5)
    else :
        Position.append(0)
            
    return Position 
    
"""
This is assuming DuPlessie MiniMac, position control NOT velocity control (for now)
Using mode 4 (16 bit, 10 channels) -> refer to manual to understand how to get to mode
Pan is 540 degrees, tilt is 270 degrees
Pan resolution is 0.013 degrees, tilt resolution is 0.007 degrees
Relevant Channels (Mode 4)
[5] pan (0 is left, 255 is right, 128 is neutral)
[6] pan fine (0 is left, 255 is right)
[7] pan (0 is up, 255 is down, 128 is neutral)
[8] pan fine (0 is up, 255 is down)
[9] pan/tilt speed
	0 - 2: tracking mode
	3 - 245: fast to slow
	246 - 248: tracking, PtS = SLO
	249 - 251: tracking, PtS = FST
	252 - 255: black out while moving
Currently NOT in a loop, just runs once
"""

import pysimpledmx # make sure it ais in same home directory
import time

COMport = '/dev/cu.usbserial-ENYXTLPV' # define COMport number

mydmx = pysimpledmx.DMXConnection(COMport) # create dmx object

# assuming that we are getting pan angle and tilt angle, make sure we're getting floats!

# with light in upright position, @ tAngle = 45 and pAngle = 210, lamp is parallel to ground, lamp is perpendicular to flat edge




def run_motor (tAngle, pAngle):
    print "   tANgle = ", str(tAngle) , "pAngle = " + str(pAngle)

    tAngle_threshold = 45
    
    tAngle = float(tAngle) - tAngle_threshold 
    pAngle = 360-float(pAngle)

    ################
    tAngle = 54.0
    
    # math for turning "real angles" into DMX values
    pAnglePercentage = pAngle/540
    tAnglePercentage = tAngle/270

    pAngleDMX = int(round(pAnglePercentage*65535))
    tAngleDMX = int(round(tAnglePercentage*65535))

    pAngleDMX = format(pAngleDMX, '016b')
    tAngleDMX = format(tAngleDMX, '016b')

    pAnglefine = int(pAngleDMX[8:16],2)
    pAnglecoarse = int(pAngleDMX[0:8],2)

    tAnglefine = int(tAngleDMX[8:16],2)
    tAnglecoarse = int(tAngleDMX[0:8],2)

    
    # for reals sending values to DMX
    
    mydmx.setChannel(1, pAnglecoarse)
    mydmx.setChannel(2, pAnglefine)
    mydmx.setChannel(3, tAnglecoarse)
    mydmx.setChannel(4, tAnglefine)
    mydmx.render() # render all of the above changes onto the DMX network

    time.sleep(0.07)
##########################################################################
#user defined variables: port, count_average, num_output 

#serial port address. Windows uses 'COM1', 'COM2'.. 
#but MAC uses different types of address. 
port =  "/dev/tty.usbmodem1421"


#########################################################################

count = 0 #start counting
dist_ta_a0 = 0 
dist_ta_a1 = 0 
dist_ta_a2 = 0 
dist_ta_a3 = 0 #distance from tag to anchor 3 
dist_a0_a1 = 0 
dist_a0_a2 = 0
dist_a1_a2 = 0 

ser  = serial.Serial(port, 9600, timeout= 0 ) #start the serial port communication

#ser_motor = serial.Serial(motor_port, 9600)

#############################################################################
#print 'zeroing anchor distances' 
print 'Please place the TAG in the ANCHOR 3 holder' #tag position =  anchor 3 position
#time_start_cali_anchors = time.clock()
countupto = 30 #recording up to countupto times. You can change the number`
numdata = 0 
dist0 = [] 
dist1 = []
dist2 = []
dist3 = []
dist4 = []
dist5 = []

while numdata < countupto:   
    data = ser.read(9999)
#    print data
    print len(data)
    if len(data) > 80 : #when the data has both 'ma' and 'mc'
        numdata += 1 
        if data[0:2] == 'ma': # 'ma' means the data show the distances between anchors 
            dist0.append( int(data[33:41], 16)) #bw anchor 1 and 2 
            dist1.append( int(data[80:88], 16)) #bw anchor 3(tag) and 1 
            dist2.append( int(data[89:97], 16)) #bw anchor 3(tag) and 2
            dist3.append( int(data[15:23], 16)) #bw anchor 0 and 1
            dist4.append( int(data[24:32], 16)) #bw anchor 0 and 2
            dist5.append( int(data[71:79], 16)) #bw anchor 0 and 3 
#    else:
#        print "no data"
    sleep(0.2) # collect the data every 0.5 seconds 
#Calculate the averages of ten continuous distances and print them out 
dist_a1_a2 = float( sum(dist0) ) / len(dist0) 
dist_a1_a3 = float( sum(dist1) ) / len(dist1)
dist_a2_a3 = float( sum(dist2) ) / len(dist2)
dist_a0_a1 = float( sum(dist3) ) / len(dist3)
dist_a0_a2 = float( sum(dist4) ) / len(dist4)
dist_a0_a3 = float( sum(dist5) ) / len(dist5)

print 're-calculating might be needed due to the distance error bw TAG and ANCHOR 3' 
print 'dist_a1_a2: ', dist_a1_a2
print 'dist_a1_a3(T0): ', dist_a1_a3
print 'dist_a2_a3(T0): ', dist_a2_a3
print 'dist_a0_a1: ', dist_a0_a1
print 'dist_a0_a2: ', dist_a0_a2
print 'dist_a0_a3(T0): ', dist_a0_a3

#time_done_cali_anchors = time.clock()
#print 'time for anchor calibration :', time_done_cali_anchors - time_start_cali_anchors
#############################################################################
## IDENTIFYING ANCHOR POSITIONS

##Modification from the three anchor system version : A0->A1 / A1->A2 / A2->A3
##Anchor 0 on the Light 
##Anchor 1 Bottom left corner 
##Anchor 2 Bottom right corner
##Anchor 3 Top left corner, --> 0-1-2 must be oriented so +z is upward
Loc_1 = [0,0,0]  #Location of A1
Loc_2 = [dist_a1_a2, 0, 0] #Location of A2 

# Solve for ANCHOR 3 position 
Angle_123 = LawofCosines(dist_a1_a2, dist_a2_a3, dist_a1_a3) #Solve for Angle 2    
y = dist_a2_a3 * math.sin(Angle_123)
x = dist_a2_a3 * math.cos(Angle_123)

## If anchors set up as shown above, double points shouldn't be an issue
## However, ** Anchor 2 to the right of Anchor 1 issue
Loc_3 = [dist_a1_a2 - x, y, 0]

# Solve for ANCHOR 0 position

Light_Location = Loc_3D(dist_a0_a1, dist_a0_a2, dist_a0_a3, Loc_2, Loc_3)

print ''
print "Location of Anchor 0 (light): " +str(Light_Location)
print "Location of Anchor 1 (bottom left corner): " + str(Loc_1)
print "Location of Anchor 2 (bottom right corner): " + str(Loc_2)
print "Location of Anchor 3 (Top left corner): " + str(Loc_3)

print "Calibration is done" 

#time_done_cali_light = time.clock()
#print 'time for LIGHT calibration :', time_done_cali_light - time_done_cali_anchors
###########################################################################################
## LIGHT POSITION CALIBRATION
##    Light_Location = []
##    TAG_0 = float(raw_input("Light_TAG_0: "))
##    TAG_1 = float(raw_input("Light_TAG_1: "))
##    TAG_2 = float(raw_input("Light_TAG_2: "))
##
##    Light_Location.append((TAG_0**2 - TAG_1**2 - Loc_1[0]**2)/ (2*Loc_1[0]))
##    Light_Location.append((TAG_0**2 - TAG_2**2 - Loc_2[0]**2 + Loc_2[1]**2)/(2*Loc_2[1]) - Loc_2[0] * Light_Location[0]/ Loc_2[1])
##    Light_Location.append((TAG_0**2-Light_Location[0]**2-Light_Location[1]**2)**.5)
##Light_Location = [1952.126246752051, 534.2969281540112, 864.9456106062033]
##print "Light Location"
##print Light_Location

############################################################################################
##LIGHT ORIENTATION CALIBRATION! UNFINISHED
## Transforming between 2 spherical coordinate systemss


############################################################################################

#Measruing tag to anchor distsances and solve for the tilt/ pan angles
#time_start_tracking = time.clock()
# The total number of outputs. 
# (count_average * num_ouput) is the total number of measurings
ans = raw_input ('ready ?')

num_output = 300
count = 0
totalcount = 0 
countupto = 10
dist0 = [] 
dist1 = []
dist2 = []
dist3 = []
previous_position = [0,0,0]
previous_count = 0
previous_pAngle = 0
previous_tAngle = 0
first_measurement = 0 
run_motor(0,0)
sleep(3)
# Will locate until told to stop

Model_Tilt = 0
Model_Pan = 0 

#print ser_motor.readline()
#while totalcount < countupto * num_output :
#    print totalcount 
#while locate_again == 'y':
while True:
    data = ser.read(9999)
    print len(data)
    if len(data) > 80 :
#        print data    
        ##### for debugging only. Printing the whole data
        count += 1
        totalcount += 1 
        if data[0:2] == 'ma': # 'ma' means the data show the distances between anchors 
#            dist0.append ( int(data[71:79], 16)) # bw tag and anchor 0
            dist1.append( int(data[80:88], 16)) #bw tag and anchor 1 
            dist2.append( int(data[89:97], 16)) #bw tag and anchor 2
            dist3.append( int(data[98:106], 16)) # bw tag and anchor 3
        elif data[0:2] == 'mc': # if there is no 'ma' data    
#            dist0.append( int(data[6:14], 16) ) #bw tag and anchor 0
            dist1.append( int(data[15:23], 16) ) #bw tag and anchor 1
            dist2.append( int(data[24:32], 16) ) #bw tag and anchor 2
            dist3.append( int(data[33:41], 16) ) #bw tag and anchor 3
#        print 'count :', count
    if count == countupto :
#        print 'calculating '
        if len(dist1) != 0 and len(dist2) != 0 and len(dist3) != 0:
#            dist_ta_a0 = float( sum( dist0 ) ) / len(dist0)
            dist_ta_a1 = float( sum( dist1 ) ) / len(dist1)
            dist_ta_a2 = float( sum( dist2 ) ) / len(dist2)
            dist_ta_a3 = float( sum( dist3 ) ) / len(dist3)
#            dist0 = [] 
            dist1 = []
            dist2 = []
            dist3 = [] 
            count = 0 
            ##### for debugging only. Printing out the distances 
##            print 'count :', count
#            print 'reading distances from tags'
#            print 'dist_ta_a0 :', dist_ta_a0    
#            print 'dist_ta_a1 :', dist_ta_a1    
#            print 'dist_ta_a2 :', dist_ta_a2
#            print 'dist_ta_a3 :', dist_ta_a3


            ###### Position Tracking
            Our_Space_Point = Loc_3D(dist_ta_a1, dist_ta_a2, dist_ta_a3, Loc_2, Loc_3)
            """
            if previous_position == [0,0,0]:
                previous_position = Our_Space_Point
            else:
                distance_changed = distance(previous_position, Our_Space_Point)
                if previous_count > 3:
                    previous_count = 0
                    previous_position = Our_Space_Point
                elif distance_changed > 10000:
                    print 'ignoring date/ distance changed :', distance_changed
                    previous_count += 1 
                    Our_Space_Point = previous_position
                else :
                    previous_count = 0 
                    previous_position = Our_Space_Point
            """
            print 'space :', Our_Space_Point  
            ## PAN-TILT, Tilt 0 -> (0,0,-z), Pan 0 -> (-x ,0 ,0) for light behind point, (x,0,0) for light in front of point. 

            ## Light behind Tag
            if Our_Space_Point[1] >= Light_Location[1]:
                Model_Tilt = math.acos((Light_Location[2]- Our_Space_Point[2]) /distance(Light_Location, Our_Space_Point))
                if  Our_Space_Point[0] >= Light_Location[0] :
                    Model_Pan = math.pi - math.atan((Our_Space_Point[1] - Light_Location[1]) / (Our_Space_Point[0]  - Light_Location[0] ))
                else:
                    Model_Pan = math.atan((Our_Space_Point[1] - Light_Location[1]) / (Light_Location[0] - Our_Space_Point[0]  ))
            ## Light infront of Tag
            else:
                print 'LIGHT in front of the TAG' 
                Model_Tilt = Model_Tilt
                Model_Pan = Model_Pan


            #Angle into String and setting len of string = 3 
            tAngle = int(Model_Tilt*360.0/(2*math.pi))
            pAngle = int(Model_Pan*360.0/(2*math.pi))

            if first_measurement == 0:
                previous_pAngle = pAngle
                previous_tAngle = tAngle
                first_measurement = 1
            else:
                if previous_count > 1:
                    previous_count = 0
                    previous_pAngle = pAngle
                    previous_tAngle = tAngle 
                elif (previous_pAngle - pAngle) ** 2 > 1000 or (previous_tAngle - tAngle)**2 > 1000:
                    print 'ignoring data'
                    print 'tAngle :', tAngle, '    pAngle :', pAngle,
                    previous_count += 1 
                    pAngle = previous_pAngle
                    tAngle = previous_tAngle
                else:
                    previous_count = 0 
                    previous_pAngle = pAngle
                    previous_tAngle = tAngle 

#            print 'Tilt_Angle :', tAngle , '   Pan_Angle :', pAngle
            run_motor(tAngle, pAngle)
                
#                locate_again = raw_input("Again? (y or n): ")
#            time_end_tracking= time.clock()
#            print 'time for tracking :', time_end_tracking - time_start_tracking 
#            time_start_tracking = time_end_tracking 

    sleep(0.05) # collect the data every 0.2 seconds 

#ser_motor.write('255000000')
mydmx.setChannel(2,0)
#ser.close()#end the communication

#print "Done tracking"




##########################################################################################
