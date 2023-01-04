### author: Roberto Vezzani

import serial
import serial.tools.list_ports

import configparser

import paho.mqtt.client as mqtt

class Bridge():

	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')
		self.setupSerial()
		self.setupMQTT()
  
		self.building_id = '22'
		self.room_id = '9'
		

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

	def setupMQTT(self):
		self.clientMQTT = mqtt.Client()
		self.clientMQTT.on_connect = self.on_connect
		self.clientMQTT.on_message = self.on_message
		print("connecting to MQTT broker...")
		self.clientMQTT.connect(
			self.config.get("MQTT","Server", fallback= "localhost"),
			self.config.getint("MQTT","Port", fallback= 1883),
			60)

		self.clientMQTT.loop_start()



	def on_connect(self, client, userdata, flags, rc):
		print("Connected with result code " + str(rc))

		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		self.clientMQTT.subscribe("mylight")


	# The callback for when a PUBLISH message is received from the server.
	def on_message(self, client, userdata, msg):
		print(msg.topic + " " + str(msg.payload))
		if msg.topic=='mylight':
			self.ser.write (msg.payload)



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
						print(self.inbuffer)
						self.useData()
						self.inbuffer =[]
					else:
						# append
						self.inbuffer.append (lastchar)

	def useData(self):
		# I have received a packet from the serial port. I can use it
		if len(self.inbuffer)<2:   # at least header, size, footer
			return False
		# split parts
		if self.inbuffer[0] != b'\xff':
			return False
		
		sensor_id = int.from_bytes(self.inbuffer[1], byteorder="little")
		sensor_name = ''
		match sensor_id:
			case 1: sensor_name = 'light_sensor'
			case 2: sensor_name = 'noise_sensor'
   
		numval = int.from_bytes(self.inbuffer[2], byteorder="little")
		data = b''
		for i in range (numval):
      
			#val.append(int.from_bytes(self.inbuffer[i+2], byteorder='little'))
			data += self.inbuffer[i+3]
   
			#strval = "Sensor %d: %d " % (i, val)
			#print(strval)
   
		val = int.from_bytes(data, byteorder='big')

		
		self.clientMQTT.publish('smartoffice/building_%s/room_%s/sensors/%s' % (self.building_id, self.room_id, sensor_name),'{:d}'.format(val))






if __name__ == '__main__':
	br=Bridge()
	br.loop()


