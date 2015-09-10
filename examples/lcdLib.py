#!/usr/bin/python
import math
import time

import Adafruit_CharLCD as LCD

class LCDLib:
	def __init__(self):
		self.initVars()
		self.setupOutput()


	def initVars(self):
		# Raspberry Pi pin configuration:
		self.lcd_rs        = 27  # Note this might need to be changed to 21 for older revision Pi's.
		self.lcd_en        = 22
		self.lcd_d4        = 10
		self.lcd_d5        = 9
		self.lcd_d6        = 11
		self.lcd_d7        = 4
		self.lcd_backlight = 3

		# alternatively specify a 20x4 LCD.
		self.lcd_columns = 20
		self.lcd_rows    = 4

		# Initialize the LCD using the pins above.
		self.lcd = LCD.Adafruit_CharLCD(self.lcd_rs, self.lcd_en, self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7,self.lcd_columns, self.lcd_rows, self.lcd_backlight)
		
		self.currTempInC = None
		self.hostname = None
		self.ip = None
		self.thresholdValues = ['A',0,0]
		self.status = "-"

	def setThresholdValues(self,thVals):
		if (thVals != self.thresholdValues):
			self.thresholdValues = thVals
	
	def getThresholdValues(self):
		return self.thresholdValues	

	def setHostname(self,hostname):
		self.hostname = hostname

	def setIp(self,ip):
		self.ip = ip

	def setStatus(self,status):
		self.status = status

	def getIp(self):
		if self.ip is None:
			return "Not connected"
		else:
			return self.ip

	def setupOutput(self):
		self.lcd.set_backlight(0)
		time.sleep(2)
		self.lcd.set_backlight(1)
		self.lcd.message('TMS activated')

	def updateMessage(self,msg):
		self.lcd.message(msg)

	def updateCurrentTemp(self,temp):
		self.currTempInC = temp
		self.refreshTemp()
	
	def updateHeaders(self):
		header = '{0: <20.20}'.format('TMS Version 1.0')
		ip = '{0: <20.20}'.format('IP:'+self.ip)
		self.lcd.setCursor(0,0)
		self.lcd.message(header)
	

	def refreshTemp(self):
		header = '{0: <20.20}'.format('TMS Version 1.0')
		ip = '{0: <20.20}'.format('IP:'+self.getIp())
		temp = '{0: <20.20}'.format('Temp(C): '+str(self.currTempInC)+ ' ' + self.status)
		device = '{0: <20.20}'.format(self.hostname)
		blank = '{0: <20.20}'.format('')
		threshold = '{0: <20.20}'.format("Mode " + self.getThresholdValues()[0] + ":" + str(self.getThresholdValues()[1])+ "-"+ str(self.getThresholdValues()[2]) + "c")
		self.lcd.clear()
		#self.lcd.message(header+ ip + temp + device)
		#self.lcd.setCursor(0,2)
		#self.lcd.message(device+temp+ip+header)
		self.lcd.message(device+temp+ip+threshold)


if __name__ == '__main__':
	instance = LCDLib()
	
