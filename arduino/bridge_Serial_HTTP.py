### author: Roberto Vezzani

import serial
import serial.tools.list_ports
import requests
import configparser


class Bridge():

	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')
		self.setupSerial()


	def setupSerial(self):
		# open serial port
		self.ser = None

		if self.config.get("Serial","UseDescription", fallback=False):
			self.portname = self.config.get("Serial","PortName", fallback="COM1")
		else:
			print("list of available ports: ")
			ports = serial.tools.list_ports.comports()

			for port in ports:
				print (port.device)
				print (port.description)
				if self.config.get("Serial","PortDescription", fallback="arduino").lower() \
						in port.description.lower():
					self.portname = port.device

		try:
			if self.portname is not None:
				print ("connecting to " + self.portname)
				self.ser = serial.Serial(self.portname, 9600, timeout=0)
		except:
			self.ser = None

		# self.ser.open()

		# internal input buffer from serial
		self.inbuffer = []

	def postdata(self, i, val):
		if i>0:
			return
		url = self.config.get("HTTPAIO","Url")+"/data"
		myobj = {'value': val}
		headers = {'X-AIO-Key': 'aio_WmfO50SOelmkqksWHc19TQjBeVsd'}
		x = requests.post(url, data=myobj, headers=headers)
		print(x.json())

	def loop(self):
		# infinite loop for serial managing
		#
		while (True):
			#look for a byte from serial
			if not self.ser is None:

				if self.ser.in_waiting>0:
					# data available from the serial port
					lastchar=self.ser.read(1)

					if lastchar==b'\xfe': #EOL
						print("\nValue received")
						self.useData()
						self.inbuffer =[]
					else:
						# append
						self.inbuffer.append (lastchar)

	def useData(self):
		# I have received a packet from the serial port. I can use it
		if len(self.inbuffer)<3:   # at least header, size, footer
			return False
		# split parts
		if self.inbuffer[0] != b'\xff':
			return False

		numval = int.from_bytes(self.inbuffer[1], byteorder='little')

		for i in range (numval):
			val = int.from_bytes(self.inbuffer[i+2], byteorder='little')
			strval = "Sensor %d: %d " % (i, val)
			print(strval)
			self.postdata(i, val)






if __name__ == '__main__':
	br=Bridge()
	br.loop()

