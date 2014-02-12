idha
====

Ist der Herd an - Is the stove still on? A little project: raspberry pi + camera + python + opencv + music = Music when the stove is running


How to use:

- Install a raspberry pi (rpi) into your kitchen
- Connect the rpi to speakers
- Connect the rpi camera to the rpi
- Mount the rpi so it can see your stove
- Fix the parameters used to capture an image (raspistill) to capture just the area of the red lamp
- Enjoy music while your stove runs!

Installation:
- Install Raspberry Pi Camera
- Mount the Pi Camera so it can see your stove
- Play around with raspistill until you only receive the image of the on/off bulb/LED
- Clone / Download idha onto your system
- Insert the parameters into the cmdline of this program (just look for 'raspistill')
- add as cronjob (/crontab -e/):
/@reboot python INSERTYOURPATHHERE/idha.py/

