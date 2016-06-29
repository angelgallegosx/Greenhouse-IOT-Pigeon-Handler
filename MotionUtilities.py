import numpy as np
import cv2
import time

# Get the background used to compare for motion detection.
# It takes to smaples and wait until they are almost equal
def get_background(cam_han):
	
	# Sum of Squares error
	last_err = 0
	err = 1000

	# If the samples are almost equal (based on the MSE) set this to be
	# the background
	while last_err != err:
		
		last_err = int(err)

		#Get a couple of frames at different time 
		frame_0 = cam_han.get_frame()
		time.sleep(1)
		frame_1 = cam_han.get_frame()
		
		# Calculate the Mean of Square Error
		err = np.sum( (frame_0 - frame_1)**2 )
		err = err / float(frame_0.shape[0]*frame_1.shape[1])
		
		# Take into account one decimal only
		err = int(err*10)
		print err

	return frame_0

# Get the difference among the given number of frames
def get_absolute_difference(frame_1, frame_2):
	diff = cv2.absdiff(frame_1, frame_2)
	#diff_2 = cv2.absdiff(frame_2, frame_3)
	#return cv2.bitwise_and(diff, diff_2)
	return diff

# Given the background and actual frame, it detect its most significant
# changes and return the number of components given
def detect_main_change(background_frame, actual_frame):

	# Get the changes from both images
	diff = get_absolute_difference(background_frame, actual_frame)
	
	thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
	#thresh = cv2.adaptiveThreshold(diff,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
		
	thresh = cv2.dilate(thresh, None, iterations=2)
	
	# Depending on the version of openCV
	cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)		
	#(_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	# Only return the main change from the background
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:1]

	return cnts

# Calibrate the angle of vision of the camera. Returns a function that transforms
# the position x from the screent to an approximation of its angle
def calibrate_with_camera(min_display_x, max_display_x, height, width):
	
	# Makes the triangle a right triangle
	width = width/float(2)

	# Pythagoras theorem
	hyp = np.sqrt( (height**2) + (width**2) )
	
	# Calculate the angle of the aperture
	angle = np.degrees( np.arccos( height/hyp ) )

	# Set the two points we already have to calculate the slope
	ref_1 = (min_display_x, 90+angle)
	ref_2 = (max_display_x, 90-angle)

	# Calculating the slope of the line ( (y_2-y_1) = m(x_2-x_1) )
	m = (ref_2[1]-ref_1[1]) / (ref_2[0]-ref_1[0]) 

	# Creates the equation for the line ( (y-y_1) = m(x-x_1) )
	f_x = lambda x: m*x + (ref_1[1] - (m*ref_1[0]) ) # mx+b

	return f_x

def detect_contour(component, threshold=1500):
	return True if cv2.contourArea(component) > threshold else False

def get_enclosure(component):
	return cv2.minEnclosingCircle(component)