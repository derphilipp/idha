#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import time
import numpy
import os
# import sys
import subprocess
import logging


def is_on(img):
    """Returns boolean if the stove is on or not
    """
    logging.info("Checking if stove is on")
    light_off = numpy.array([180, 30, 30], numpy.uint8)
    light_on = numpy.array([255, 255, 255], numpy.uint8)
    filtered = cv2.inRange(img, light_off, light_on)
    amount = cv2.countNonZero(filtered)
    # Assumption: Some pixels could flicker -> More than 50 pixels
    # light indicate an 'on' bulb
    logging.info("Amount: %d", amount)
    if amount > 10:
        logging.info("Stove is on!")
        return True
    else:
        logging.info("Stove is off")
        return False

logging.basicConfig(filename='/var/log/idha.log', level=logging.INFO)


class CameraGrabber:
    """ Object to handle camera input
    """
    @property
    def is_running(self):
        """ Is the camera running?
        """
        if not self.process:
            return False
        elif self.process.poll() is not None:
            return False
        else:
            return True

    def __init__(self):
        self.process = None
        self.reset()

    def reset(self):
        """ Restart camera
        """
        logging.info("(Re)starting Camera")
        self.process = False
        os.system('killall raspistill')
        self.capture()
        time.sleep(3)

    def capture(self):
        """ Capture one picture via subprocess
        """
        if not self.process:
            logging.info("Capturing Image")
            cmd = ("raspistill -vf -hf -o /run/shm/image.jpg "
                   "-e bmp -roi 0.594,0.534,0.011,0.011 -tl 1000 "
                   "-w 28 -h 21 -t 21600000 -n >/run/shm/cam.log")
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                            shell=True, preexec_fn=os.setsid)
            time.sleep(3)

    def check_to_run(self):
        """ Check if the camera is currently running
        """
        if not self.is_running:
            self.reset()
        else:
            pass

    def image(self):
        """ Check if camera is running and return path to image
        """
        self.check_to_run()
        return "/run/shm/image.jpg"


class MusicPlayer:
    """ Object to handle instance of musicplayer
    """
# PIPENAME="/tmp/omx.pip"

    def __init__(self):
        logging.info("Initializing Music Player")
        self.process = False
        self.is_playing = False
        os.system('mkfifo /tmp/omx.pipe')
        os.system('killall omxplayer')
        os.system('killall omxplayer.bin')

    def play(self):
        """ Start to play music
        """
        if not self.is_playing:
            cmd = "omxplayer http://stream.laut.fm/radioindie"
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                            shell=True, preexec_fn=os.setsid)
            self.is_playing = True

    def stop(self):
        """ Stop to play music
        """
        if self.is_playing:
            os.killpg(self.process.pid, subprocess.signal.SIGTERM)
            self.is_playing = False


# Filter Values for "Light should be off" and "Light should be on"
# Probably needs some tweaking
MUSIC = MusicPlayer()
CAPTURE = CameraGrabber()

COUNT_ON = 0
COUNT_OFF = 0
logging.info("Start of main loop")

while True:
    logging.debug("Loop")
    IMG = cv2.imread(CAPTURE.image())
#   if the stove is on, count up to 20
    if is_on(IMG):
        COUNT_OFF = 0
        if COUNT_ON > 20:
            logging.debug("Starting music.play()")
            MUSIC.play()
        else:
            logging.debug("It is still on :)")
            COUNT_ON = COUNT_ON+1
            logging.debug("Count amount: %d", COUNT_ON)
    else:
        COUNT_ON = 0
        if COUNT_OFF > 20:
            logging.info("stop music")
            MUSIC.stop()
        else:
            COUNT_OFF = COUNT_OFF+1
    time.sleep(1)

    if cv2.waitKey(200) & 0xFF == ord('q'):
        break
