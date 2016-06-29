import RPi.GPIO as GPIO
import time

class PumpHandler(object):
	
	def __init__(self, pump_pin):
		
		self.pin = pump_pin
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pump_pin, GPIO.OUT)
		

	def shot(self, time_seconds):
		
		GPIO.output(self.pin, GPIO.HIGH)
		
		time.sleep(time_seconds)
		GPIO.output(self.pin, GPIO.LOW)
		