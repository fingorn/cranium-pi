#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Can enable debug output by uncommenting:
#import logging
#logging.basicConfig(level=logging.DEBUG)

import time, socket,os
from DbConnect import DbConnect
from lcdLib import LCDLib

import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855
from threading import Thread
from ThresholdControl import ThresholdControl

class TmsRasp:
	def __init__(self):
		
		print "Tms init main:"
		self.initParams()
		self.createTMSDevice()
		self.lcd = LCDLib()
		self.setLcdDetails()
		self.thresholdThread()
		self.mainLoopThread()
		self.addTempToDbThread()	
	
	
	def setLcdDetails(self):
		print "setLcdDetails deviceID:{0} deviceIP:{1}".format(self.deviceID,self.deviceIP)
		self.lcd.setHostname(self.deviceID)
		self.lcd.setIp(self.deviceIP)

	def createTMSDevice(self):
		#Create Device ID if not exist
		(ipaddr, deviceId ,gateway) = self.getDeviceIP()
		print "device id : " + deviceId
		try:
			#details = (deviceId,ipaddr)
			#self.getDB().createDeviceID(details)
			self.deviceID = deviceId
			self.deviceIP = ipaddr
		except Exception, e:
			print "Unable to update device information. " + str(e)			


	def getDeviceIP(self):
		ipaddr = None
		host = 'Unidentified'
		gateway = None
		try:
			gw = os.popen("ip -4 route show default").read().split()
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			host = socket.gethostname()
			s.connect((gw[2], 0))
			ipaddr = s.getsockname()[0]
			gateway = gw[2]
			print ("IP:", ipaddr, " GW:", gateway, " Host:", host)
		except Exception, e:
			print "Unable to obtain IP address"
				
		if ipaddr == None:
			self.deviceIpSet = False
		else:
			self.deviceIpSet = True
		return (ipaddr,host,gateway)		


	def initParams(self):
		self.__db__ = None
		# Raspberry Pi software SPI configuration.
		self.CLK = 18
		self.CS = 24
		self.DO = 25
		self.sensor = MAX31855.MAX31855(self.CLK, self.CS, self.DO)
		self.deviceID = None
		self.deviceIP = None
		self.currTemp = None
		self.deviceIpSet = False
		self.thresholdMain = None

	# Define a function to convert celsius to fahrenheit.
	def c_to_f(self,c):
		return c * 9.0 / 5.0 + 32.0


	# Uncomment one of the blocks of code below to configure your Pi or BBB to use
	# software or hardware SPI.

	def addTempToDbThread(self):
		
		thread = Thread(target = self.addTempToDB)
		thread.start()
		print "Database Temp update thread started.."
	
	def addTempToDB(self):
		dbCounter = 0	
		while True:
			try:
				if self.__db__ == None:
					print "db is null.  reconnecting.."
					self.checkDbConnection()
				else:
					if self.strToF(self.currTemp):
						print "Db Connection Exist. Upload temp to db " + str(self.currTemp)
						details = (self.deviceID,str(self.currTemp))
						self.getDB().addTempByDevice(details)
						print "Temp db upload successful"
					else:
						print "Invalid temperature detected"

			except Exception, e:
				#print "Error uploading temp to Db " + str(e)
				#try to reconnect if DbConnection is null
				self.__db__ = None
				self.deviceIpSet = False
			time.sleep(1.0)
			#dbCounter = dbCounter + 1
			#print "database update counter " + str(dbCounter)
	
	def strToF(self,num):
		valid = False
		try:
			value = float(num)
			print "strToF value:" + str(value)
			valid = True
		except Exception, e:
			return valid

	def mainLoopThread(self):
		#Wait 3 seconds to start main loop
		#time.sleep(3)
		thread = Thread(target = self.mainLoop)
		thread.start()
		print "Main Loop Started"

	def mainLoop(self):
		# Loop printing measurements every second.
		print 'Press Ctrl-C to quit.'
		while True:
			temp = self.sensor.readTempC()  
			self.currTemp = temp
			internal = self.sensor.readInternalC()
			#print 'Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, self.c_to_f(temp))
			#print '    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, self.c_to_f(internal))
			tempInF = self.c_to_f(temp)
			#print "temp in C : " + str(temp)
		
			#setLcdThresholdValues
			self.setlcdThresholdValues(temp)

			#inc thresholdMain sleep counter
			self.getThresholdMain().addThSlpCounter()		

			#print to LCD
			self.lcdTempOutput(temp)

			time.sleep(1.0)

	def setlcdThresholdValues(self,temp):
		self.lcd.setThresholdValues(self.getThresholdMain().getThldValues())
		status = self.getThresholdMain().getThresholdStatus(temp)
		self.lcd.setStatus(status)

				
	def lcdTempOutput(self,temp):
		#self.setLcdDetails()
		if not self.deviceIpSet:
			self.createTMSDevice()
			self.setLcdDetails()
		self.lcd.updateCurrentTemp(temp)

	def checkDbConnection(self):
		
		try:
			#print 'checking db connection.'
			dbConn = DbConnect()
			#self.__db__ = DbConnect()
			if dbConn.connect() == True:
				self.__db__ = dbConn
			details = (self.deviceID,self.deviceIP)
			self.getDB().createDeviceID(details)
	
			
		except Exception, e:
			self.__db__ = None
			#print 'Unable to connect to db.. retrying... ' + str(e)
			


	def getDB(self):
		return self.__db__

	def thresholdThread(self):
		self.thresholdMain = ThresholdControl()
		print "Current threshold :" + str(self.thresholdMain.getThldValues())
	
	def getThresholdMain(self):
		return self.thresholdMain


if __name__ == '__main__':
	instance = TmsRasp()
