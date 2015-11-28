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

COMport = "/dev/cu.usbserial-ENYXTLPV" # define COMport number

mydmx = pysimpledmx.DMXConnection(COMport) # create dmx object

# assuming that we are getting pan angle and tilt angle, make sure we're getting floats!

# with light in upright position, @ tAngle = 45 and pAngle = 210, lamp is parallel to ground, lamp is perpendicular to flat edge

tAngle = float(70.0)
pAngle = float(80.0)

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

print "pfine = " + str(tAnglefine)
print "pcoarse = " + str(tAnglecoarse)

print "tfine = " + str(tAnglefine)
print "tcoarse = " + str(tAnglecoarse)


# for reals sending values to DMX

mydmx.setChannel(2,0)
mydmx.setChannel(3,24)
mydmx.setChannel(6, pAnglecoarse)
mydmx.setChannel(7, pAnglefine)
mydmx.setChannel(8, tAnglecoarse)
mydmx.setChannel(9, tAnglefine)
mydmx.setChannel(10, 250)

mydmx.render()

time.sleep(5)

tAngle = float(0.0)
pAngle = float(0.0)

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

print "pfine = " + str(tAnglefine)
print "pcoarse = " + str(tAnglecoarse)

print "tfine = " + str(tAnglefine)
print "tcoarse = " + str(tAnglecoarse)

# for reals sending values to DMX

mydmx.setChannel(2,0)
mydmx.setChannel(3,24)
mydmx.setChannel(6, pAnglecoarse)
mydmx.setChannel(7, pAnglefine)
mydmx.setChannel(8, tAnglecoarse)
mydmx.setChannel(9, tAnglefine)
mydmx.setChannel(10, 250)
mydmx.render() # render all of the above changes onto the DMX network
