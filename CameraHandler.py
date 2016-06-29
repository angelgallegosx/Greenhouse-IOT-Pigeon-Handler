import numpy as np
import cv2
import threading

class CameraHandler(threading.Thread):

	def __init__(self, camera_number, fps=30):
		threading.Thread.__init__(self)

		# Set the source of the camera: Usually 0
		self.cam = cv2.VideoCapture(camera_number) 

		# Defines if the camera is reading or not
		self.sensing = False

		# Last frame read -- Initialized to one smoothed frame
		self.smoothed_frame = self.__get_smoothed_frame( self.cam.read()[1] )

		# Set the screen location of the movement
		self.screen_location = -1

		#self.cam.set(cv2.cv.CV_CAP_PROP_FPS, fps)
		self.fps = fps/float(60)

	# Set the flag to true and start reading
	def run(self):
		self.sensing = True
		self.main_loop()

	# Stop the main loop
	def stop(self):
		self.sensing = False

	# Get a new frame from the camera (matrix)
	def __get_new_frame(self):
		return self.cam.read()[1]

	# Get a camera frame smoothed with effects that ease the contour
	# Comparisson
	def __get_smoothed_frame(self, frame):
		
		# Convert the frame into grayscale
		frame_gray_scale = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
		# Apply a gaussian blur to the image for ...
		smoothed_frame = cv2.GaussianBlur(frame_gray_scale, (21, 21), 0) 

		return smoothed_frame

	def get_frame(self):
		return self.smoothed_frame

	def main_loop(self):

		while self.sensing:

			# Take a frame from the camera. This frame is used for real-time representation
			frame = self.__get_new_frame()

			# Get the smoothed version of the frame for comparisson
			self.smoothed_frame = self.__get_smoothed_frame(frame)