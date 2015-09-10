#!/usr/bin/python

from threading import Thread
import time
import RPi.GPIO as GPIO
import tmsconfig

class ThresholdControl:
	def __init__(self):
		print "Setup GPIO"
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(17,GPIO.IN)
		
		#Setup configs
		self.setThresholdArray()
		print "Start Loop"
		self.listenerThread()

	def getThldIdx(self):
		return self.currThresholdIndex

	def setThresholdArray(self):
		self.thresholdMap = tmsconfig.temp_thresholds
		self.currThresholdIndex = 0
		self.thresholdCount = len(self.thresholdMap)
		self.setThresholdValues()
	
	def setThresholdValues(self):
		self.th_name = self.thresholdMap[self.getThldIdx()]['name']
		self.min_temp = self.thresholdMap[self.getThldIdx()]['min_temp']
		self.max_temp = self.thresholdMap[self.getThldIdx()]['max_temp']
		#Test print
		print "Current threshold value: {0} : {1} - {2} ".format(self.th_name,self.min_temp,self.max_temp)

	def getThresholdStatus(self,temp):
		if (float(temp) < float(self.min_temp)):
			return "Low"
		elif (float(self.min_temp) <= float(temp) <= float(self.max_temp)):
			return "OK"
		else:
			return "HI"

	def listenerThread(self):
		thread = Thread(target = self.mainLoop)
		thread.start()
		print "ThresholdControl Main loop started"

	def mainLoop(self):
		prev_input = 0
		prev_input = GPIO.input(17)
		while True:
			
			input= GPIO.input(17)
			#print("input:" +str(input))
			if (not prev_input) and input:
				#print("Button presesd")
				self.thresholdCycle()
			#Update prev input
			prev_input = input
			time.sleep(0.05)

	def thresholdCycle(self):
		self.incThldIdx()
		self.setThresholdValues()
	
	def incThldIdx(self):
		if (self.getThldIdx() >= self.thresholdCount - 1):
			#Set counter index back to 0
			self.currThresholdIndex = 0
		else:
			self.currThresholdIndex += 1
		
	def getThldValues(self):
		return [self.th_name,self.min_temp,self.max_temp]	
		

if __name__ == '__main__':
	instance = ThresholdControl()

