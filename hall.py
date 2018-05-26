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

# Note from Gamer1120: I am not proud of this code. It does what it needs to do and is only used for 1 weekend.

# Import required libraries
import time
import datetime
import RPi.GPIO as GPIO
import math
import sched, time
import json
import subprocess
from termcolor import colored
import os
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
global ROUND_LENGTH
ROUND_LENGTH = 60
global READ_ONLY_READY_TIME
READ_ONLY_READY_TIME = 5
global READY_TIME
READY_TIME = READ_ONLY_READY_TIME
global FIRST_CP
FIRST_CP = datetime.datetime.fromtimestamp(1527285600)
global CURRENT_CP
diff = datetime.datetime.now() - FIRST_CP
days, seconds = diff.days, diff.seconds
CURRENT_CP = days * 24 + seconds // 3600
global CONTROLLING_FACTION
global FNULL
FNULL = open(os.devnull, 'w')
global PUMP_1_POINTS
PUMP_1_POINTS = 0
global PUMP_2_POINTS
PUMP_2_POINTS = 0
global PUMP_3_POINTS
PUMP_3_POINTS = 0
global PUMP_4_POINTS
PUMP_4_POINTS = 0

#0 neutral
#1 enl
#2 res
def controlling_faction(scheduler):
  output = subprocess.check_output(["curl", "-s", "localhost:8080/v1/info"])
  json_output = json.loads(output)
  global CONTROLLING_FACTION
  CONTROLLING_FACTION = json_output['result']['controllingFaction']
  s.enter(1,1,controlling_faction,(scheduler,))

def checkpoint_info(cp):
  enl_score = 0
  res_score = 0
  tied_score = 0
  lines = [line.strip() for line in open("/home/pi/kaltenberg-alchemist/checkpoints/" + str(cp))]
  for i, line in enumerate(lines):
    if i % 2 == 0 and line == 1:
      enl_score += 1
    elif i % 2 == 1 and line == 1:
      res_score += 1
    elif i % 2 == 1:
      tied_score += 1
  return enl_score, res_score, tied_score

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
  if GPIO.input(channel):
    # No magnet
    print("Sensor HIGH " + stamp + " " + str(channel))
  else:
    # Magnet
    print("Sensor LOW " + stamp + " " + str(channel))

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

def reset_game():
  global timeleft
  global points1
  global points2
  global points3
  global points4
  global READY_TIME
  global PUMP_1_POINTS
  PUMP_1_POINTS = 0
  global PUMP_2_POINTS
  PUMP_2_POINTS = 0
  global PUMP_3_POINTS
  PUMP_3_POINTS = 0
  global PUMP_4_POINTS
  PUMP_4_POINTS = 0

  READY_TIME = READ_ONLY_READY_TIME
  timeleft = ROUND_LENGTH
  points1 = 0
  points2 = 0
  points3 = 0
  points4 = 0


print("Done setting up. The round can begin!")
s = sched.scheduler(time.time, time.sleep)
global timeleft
timeleft = ROUND_LENGTH


def update_screen(scheduler):
  global timeleft
  global points1
  global points2
  global points3
  global points4
  global READY_TIME
  global CURRENT_CP

  clear_screen()
  diff = datetime.datetime.now() - FIRST_CP
  days, seconds = diff.days, diff.seconds
  CURRENT_CP = days * 24 + seconds // 3600
  if READY_TIME > 0:
    clear_screen()
    print("GET READY! The round starts in: " + str(READY_TIME))
    print("You're battling for checkpoint: " + str(CURRENT_CP))
    print("\n\n\n\n\n\n\n\n\n\n\n")
    s.enter(1,1,update_screen,(scheduler,))
    READY_TIME -= 1
    return
  if timeleft == 0:
    print("Game over!")
    f = open("/home/pi/kaltenberg-alchemist/checkpoints/" + str(CURRENT_CP), "a+")
    if (PUMP_1_POINTS + PUMP_2_POINTS) > (PUMP_3_POINTS + PUMP_4_POINTS):
      print("The Enlightened are victorious!")
      f.write("1\n")
      f.write("0\n")
    elif (PUMP_1_POINTS + PUMP_2_POINTS) < (PUMP_3_POINTS + PUMP_4_POINTS):
      print("The Resistance are victorious!")
      f.write("0\n")
      f.write("1\n")
    else:
      print("The round was a tie!")
      f.write("0\n")
      f.write("0\n")
    enl_score_old, res_score_old, tied_score_old = checkpoint_info(CURRENT_CP - 1)
    enl_score, res_score, tied_score = checkpoint_info(CURRENT_CP)
    print("\n\n\n\nScoreboard for this round:")
    print(colored("Total Enlightened: " + str(int(math.floor(PUMP_1_POINTS)) + int(math.floor(PUMP_2_POINTS))), 'green'))
    print(colored("Pump 1: " + str(int(math.floor(PUMP_1_POINTS))), 'green'))
    print(colored("Pump 2: " + str(int(math.floor(PUMP_2_POINTS))), 'green'))
    print("\n\n\n")
    print(colored("Total Resistance: " + str(int(math.floor(PUMP_3_POINTS)) + int(math.floor(PUMP_4_POINTS))), 'blue'))
    print(colored("Pump 3: " + str(int(math.floor(PUMP_3_POINTS))), 'blue'))
    print(colored("Pump 4: " + str(int(math.floor(PUMP_4_POINTS))), 'blue'))
    print("Previous checkpoint: " + str(CURRENT_CP - 1) + "\nRounds won: " + colored("Enlightened: " + str(enl_score_old), "green") + colored(" Resistance: " + str(res_score_old), "blue") + " Tied: " + str(tied_score_old))
    print("Current checkpoint (excluding this round): " + str(CURRENT_CP) + "\nRounds won: " + colored("Enlightened: " + str(enl_score), "green") + colored(" Resistance: " + str(res_score), "blue") + " Tied: " + str(tied_score))
    raw_input("Press the enter key to start a new round!...")
    clear_screen()
    reset_game()
    clear_screen()
  clear_screen()
  if timeleft != ROUND_LENGTH:
    cf = CONTROLLING_FACTION
    print("GO! Time left in this round: " + str(timeleft) + " seconds.")
    print("\n\n\n\n\n\n\n\n")
    if cf == "Enlightened":
      print("The Enlightened are controlling the portal! Only they can earn points!")
    elif cf == "Resistance":
      print("The Resistance are controlling the portal! Only they can earn points!")
    elif cf == "Neutral":
      print("No-one is controlling the portal! No points are earned!")
    print("\n")
    print(colored("Total Enlightened: " + str(int(math.floor(PUMP_1_POINTS)) + int(math.floor(PUMP_2_POINTS))), 'green'))
    print(colored("Pump 1: " + str(int(math.floor(PUMP_1_POINTS))), 'green'))
    print(colored("Pump 2: " + str(int(math.floor(PUMP_2_POINTS))), 'green'))
    print("\n\n\n")
    print(colored("Total Resistance: " + str(int(math.floor(PUMP_3_POINTS)) + int(math.floor(PUMP_4_POINTS))), 'blue'))
    print(colored("Pump 3: " + str(int(math.floor(PUMP_3_POINTS))), 'blue'))
    print(colored("Pump 4: " + str(int(math.floor(PUMP_4_POINTS))), 'blue'))
  else:
    clear_screen()
  timeleft -= 1
  s.enter(1,1,update_screen,(scheduler,))

s.enter(1,1,update_screen, (s,))
s.enter(1,1,controlling_faction, (s,))
s.run()


if __name__=="__main__":
   main()
