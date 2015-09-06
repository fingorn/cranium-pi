#!/usr/bin/python

import time
import RPi.GPIO as GPIO

class ThresholdControl:
	def __init__(self):
		print "Setup GPIO"
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(17,GPIO.IN)
		
		print "Start Loop"
		self.listener()

	def listener(self):
		prev_input = 0
		while True:
			
			input= GPIO.input(17)
			print("input:" +str(input))
			if (not prev_input) and input:
				print("Button presesd")
			#Update prev input
			prev_input = input
			time.sleep(0.05)

if __name__ == '__main__':
	instance = ThresholdControl()

