#!/usr/bin/python
#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#       Hall Effect Sensor
#
# This script tests the sensor on GPIO17.
#
# Author : Matt Hawkins
# Date   : 08/05/2018
#
# https://www.raspberrypi-spy.co.uk/
#
#--------------------------------------

# Import required libraries
import time
import datetime
import RPi.GPIO as GPIO
import math
import sched, time
from termcolor import colored
# Setting points up as doubles. Whenever a state transition occurs in the sensor, it is upped by 0.5.
# This way I don't have to deal with high and low.
# GPIO17
global points1
points1=0.0
# GPIO2
global points2
points2=0.0
# GPIO3
global points3
points3=0.0
# GPIO4
global points4
points4=0.0

def sensorCallback(channel):
  team = 0
  if (channel == 17):
    team = 1
  else:
    team = channel
  global points1
  global points2
  global points3
  global points4
  if (team == 1):
    points1 += 0.5
  if (team == 2):
    points2 += 0.5
  if (team == 3):
    points3 += 0.5
  if (team == 4):
    points4 += 0.5
  # Called if sensor output changes
  timestamp = time.time()
  stamp = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
#  if GPIO.input(channel):
    # No magnet
#    print("Sensor HIGH " + stamp + " " + str(channel))
#  else:
    # Magnet
#    print("Sensor LOW " + stamp + " " + str(channel))

def clear_screen():
  print(chr(27) + "[2J")
  return

def main():
  clear_screen()
  # Wrap main content in a try block so we can
  # catch the user pressing CTRL-C and run the
  # GPIO cleanup function. This will also prevent
  # the user seeing lots of unnecessary error
  # messages.

  # Get initial reading
  sensorCallback(17)
  sensorCallback(2)
  sensorCallback(3)
  sensorCallback(4)

  try:
    # Loop until users quits with CTRL-C
    while True :
      time.sleep(0.1)

  except KeyboardInterrupt:
    # Reset GPIO settings
    GPIO.cleanup()

print("Setting up... Just wait a moment.")

# Tell GPIO library to use GPIO references
GPIO.setmode(GPIO.BCM)

print("Setup GPIO pin as input on GPIO17")

# Set Switch GPIO as input
# Pull high by default
GPIO.setup(17 , GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(17, GPIO.BOTH, callback=sensorCallback, bouncetime=200)
GPIO.setup(2 , GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(2, GPIO.BOTH, callback=sensorCallback, bouncetime=200)
GPIO.setup(3 , GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(3, GPIO.BOTH, callback=sensorCallback, bouncetime=200)
GPIO.setup(4 , GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(4, GPIO.BOTH, callback=sensorCallback, bouncetime=200)

print("Done setting up. The round can begin!")
s = sched.scheduler(time.time, time.sleep)
global timeleft
timeleft = 300

def update_screen(scheduler):
  global timeleft
  global points1
  global points2
  global points3
  global points4
  clear_screen()
  print("Time left: " + str(timeleft) + " seconds.")
  print("\n\n\n\n\n")
  print(colored("Total Enlightened: " + str(int(math.floor(points1)) + int(math.floor(points2))), 'green'))
  print(colored("points1: " + str(int(math.floor(points1))), 'green'))
  print(colored("points2: " + str(int(math.floor(points2))), 'green'))
  print("\n\n\n")
  print(colored("Total Resistance: " + str(int(math.floor(points3)) + int(math.floor(points4))), 'blue'))
  print(colored("points3: " + str(int(math.floor(points3))), 'blue'))
  print(colored("points4: " + str(int(math.floor(points4))), 'blue'))
  timeleft-=1
  s.enter(1,1,update_screen,(scheduler,))

s.enter(1,1,update_screen, (s,))
s.run()

if __name__=="__main__":
   main()
