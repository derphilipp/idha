#!/usr/bin/env python
import cv2
import time
import numpy
import os
import sys
import subprocess
import logging

def is_on(img):
	logging.info("Checking if stove is on")
	LIGHT_OFF = numpy.array([180,30,30],numpy.uint8)
	LIGHT_ON = numpy.array([255,255,255],numpy.uint8)
	filtered = cv2.inRange(img,LIGHT_OFF,LIGHT_ON)
	amount=cv2.countNonZero(filtered)
	# Assumption: Some pixels could flicker -> More than 50 pixels light indicate an 'on' bulb
	logging.info("Amount: %d" % amount)
	if amount > 10:
		logging.info("Stove is on!")
		return True
	else:
		logging.info("Stove is off")
		return False

logging.basicConfig(filename='/var/log/idha.log',level=logging.INFO)

class CameraGrabber:
    @property
    def isRunning(self):
        if self.process == False:
            return False
        elif self.process.poll() != None:
            return False
        else:
            return True

    def __init__(self):
        self.reset()
    def reset(self):
        logging.info("(Re)starting Camera")
        self.process = False
        os.system('killall raspistill')
        self.capture()
        time.sleep(3)

    def capture(self):
        if self.process == False:
            logging.info("Capturing Image")
            cmd = "raspistill -vf -hf -o /run/shm/image.jpg -e bmp -roi 0.594,0.534,0.011,0.011 -tl 1000 -w 28 -h 21 -t 21600000 -n >/run/shm/cam.log"
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
            time.sleep(3)
    def checkToRun(self):
        if not self.isRunning:
            self.reset()
        else:
            pass
    def image(self):
        self.checkToRun()
        return "/run/shm/image.jpg"

class MusicPlayer:
	#PIPENAME="/tmp/omx.pip"
	
	def __init__(self):
		logging.info("Initializing Music Player")
		self.process = False
		self.state = False
		os.system('mkfifo /tmp/omx.pipe')
		os.system('killall omxplayer')
		os.system('killall omxplayer.bin')

	def play(self):
		if self.state == False:
			cmd = "omxplayer http://stream.laut.fm/radioindie"
			self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
			self.state = True

	def stop(self):
		if self.state==True:
			os.killpg(self.process.pid, subprocess.signal.SIGTERM) 
			self.state = False

		



# Filter Values for "Light should be off" and "Light should be on" 
# Probably needs some tweaking 
music = MusicPlayer()
capture = CameraGrabber()

count_on = 0
count_off = 0
logging.info("Start of main loop")

while True:
	logging.debug("Loop")
	img = cv2.imread(capture.image())
	
	#if the stove is on, count up to 20
	if is_on(img):
		count_off = 0
		if count_on > 20:
			logging.debug("Starting music.play()")
			music.play()
		else:
			logging.debug("It is still on :)")
			count_on = count_on +1
			logging.debug("Count amount: %d" % count_on)
	else:
		count_on =0
		if count_off > 20:
			logging.info("stop music")
			music.stop()
		else:
			count_off = count_off+1
	time.sleep(1)
		
	if cv2.waitKey(200) & 0xFF == ord('q'):
		break
