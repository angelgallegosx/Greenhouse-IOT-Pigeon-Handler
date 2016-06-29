#!/usr/bin/env python

import numpy as np
import threading
import signal
import Queue
import sys

from CameraHandler import CameraHandler
from ServoHandler import ServoHandler
from PumpHandler import PumpHandler
import MotionUtilities as MU

threads = []

# When the parent thread is killed by Ctrl+C, it stop also the child threads
def signal_handler(signal, frame):
	print('You pressed Ctrl+C!')

	# Join the threads
	for t in threads:
		t.stop()
		t.join()


	import RPi.GPIO as GPIO
	GPIO.cleanup()
	
	sys.exit(0)

def main():

	# Calibrate camera to servo. This is a function 
	get_angle = MU.calibrate_with_camera(13, 303, 50, 40)#MU.calibrate_with_camera(13, 303, 50, 34)

	# Servo handler
	servo = ServoHandler(18, 100, 2.5, 20)

	# Pump Handler
	pump = PumpHandler(16)

	# Camera handler 
	cam = CameraHandler(0, 8)

	# Keep track of the threads
	threads.append(cam)

	# This goes into a thread
	cam.start()

	# Create a background frame for comparisson
	background_frame = MU.get_background(cam)

	while True:

		smoothed_frame = cam.get_frame()
		component = MU.detect_main_change(background_frame, smoothed_frame)

		if len(component) != 0:

			component = component[0]

			# if the contour is too small, ignore it -> Not significant movement
			if MU.detect_contour(component):
				
				# Get the countour as a circle around the main change
				(x,y), radius = MU.get_enclosure(component)
				
				angle = int( get_angle(int(x)) )
				print angle

				# Change the position only when it was changed (significantly)
				servo.set_angle(angle)

				# The pump shoots!!!
				pump.shot(1)

		# Reduce the speed of the readings
		dummy_event = threading.Event()
		dummy_event.wait(1)

if __name__ == '__main__':

	signal.signal(signal.SIGINT, signal_handler)
	print('Press Ctrl+C to finish it')

	main()