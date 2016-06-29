import RPi.GPIO as GPIO
import threading
import time

class ServoHandler(object):

	def __init__(self, servo_pin, PWM_frq, left_pos, right_pos):

		# Raspberry Pi pin for the servo
		self.servo_pin = servo_pin
		
		# Set the pin numbering scheme to the one in fritzing
		GPIO.setmode(GPIO.BCM)

		# Set the pin 18 to be an output pin
		GPIO.setup(servo_pin, GPIO.OUT)

		# It will be used to transform angles to positions
		self.get_position = self.__calibrate(left_pos, right_pos)

		# The servos position is controlled by the pulsewidth of a X Hz PWM signal  
		self.pwm = GPIO.PWM(servo_pin, PWM_frq)

		self.old_angle = 90

		self.pwm.start(5)

	# Calculate the values requred for using angles with the servo
	def __calibrate(self, left_pos, right_pos):

		# Set the two points we already have to calculate the slope
		ref_1 = (0, left_pos)
		ref_2 = (180, right_pos)

		# Calculating the slope of the line ( (y_2-y_1) = m(x_2-x_1) )
		m = (ref_2[1]-ref_1[1]) / (ref_2[0]-ref_1[0])

		# Creates the equation for the line ( (y-y_1) = m(x-x_1) )
		f_x = lambda x: m*x + (ref_1[1] - (m*ref_1[0]) ) # mx+b

		self.get_position = f_x
		#self.get_position = lambda x: float(x)/10 + 2.5

		return f_x

	def set_angle(self, angle):

		if angle < self.old_angle-2 or angle > self.old_angle+2:
			print angle, self.get_position(angle)
			self.pwm.ChangeDutyCycle( self.get_position(angle) )
			self.old_angle = angle
		return angle, self.get_position(angle)

	def __del__(self):
		GPIO.cleanup()