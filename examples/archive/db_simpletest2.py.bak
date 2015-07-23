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

import Adafruit_GPIO.SPI as SPI
import Adafruit_MAX31855.MAX31855 as MAX31855

class TmsRasp:
	def __init__(self):
		
		
		self.__db__ = None
		self.initParams()
		print "Tms init main:"
		self.checkDbConnection()
		
		pass
	
	


	def createTMSDevice(self):
		#Create Device ID if not exist
		(ipaddr, deviceId ,gateway) = self.getDeviceIP()
		print "device id : " + deviceId
		try:
			details = (deviceId,ipaddr)
			self.getDB().createDeviceID(details)
			self.deviceID = deviceId
			self.deviceIP = ipaddr
		except Exception, e:
			print "Unable to update device information. " + str(e)			


	def getDeviceIP(self):
		gw = os.popen("ip -4 route show default").read().split()
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect((gw[2], 0))
		ipaddr = s.getsockname()[0]
		gateway = gw[2]
		host = socket.gethostname()
		print ("IP:", ipaddr, " GW:", gateway, " Host:", host)
		return (ipaddr,host,gateway)		


	def initParams(self):
		# Raspberry Pi software SPI configuration.
		self.CLK = 18
		self.CS = 24
		self.DO = 25
		self.sensor = MAX31855.MAX31855(self.CLK, self.CS, self.DO)
		self.deviceID = None
		self.deviceIP = None

	# Define a function to convert celsius to fahrenheit.
	def c_to_f(self,c):
		return c * 9.0 / 5.0 + 32.0


	# Uncomment one of the blocks of code below to configure your Pi or BBB to use
	# software or hardware SPI.


	def addTempToDB(self,serOutput):
		try:
			print "Test upload to db " + str(serOutput)
			details = (self.deviceID,str(serOutput))
			self.getDB().addTempByDevice(details)
			return True							
		except Exception, e:
			print "Error uploading to Db " + str(e)
			#try to reconnect if DbConnection is null
			return False
		#	if self.getDB().getDbConnection() is None:
		#		try:

		#			print "Db Connection is null. Reconnecting..."
		#			self.getDB().connect()
		#			self.createTMSDevice()
		#		except Exception, e2:
		#			print 'Unable to connect to database. Retrying..' + str(e2) 

	def mainLoop(self):
		# Loop printing measurements every second.
		print 'Press Ctrl-C to quit.'
		while True:
			temp = self.sensor.readTempC()  
			internal = self.sensor.readInternalC()
			print 'Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, self.c_to_f(temp))
			print '    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, self.c_to_f(internal))
			tempInF = self.c_to_f(temp)
			#print "temp in C : " + str(temp)
			if not self.addTempToDB(temp):
				self.checkDbConnection()
				break
			time.sleep(1.0)

	def checkDbConnection(self):
		while True:
			try:
				print 'checking db connection.'
				self.__db__ = DbConnect()
				self.getDB().connect()
				
				self.createTMSDevice()
				self.mainLoop()
				break
			except Exception, e:
				print 'Unable to connect to db.. retrying... ' + str(e)
				time.sleep(5)
				


	def getDB(self):
		return self.__db__

if __name__ == '__main__':
	instance = TmsRasp()
