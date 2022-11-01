import serial
import serial.tools.list_ports

import configparser

import paho.mqtt.client as mqtt

"""
This bridge receives data from the cloud and sends them to actuators through serial port.

TESTING: I have to pilot the colors of a led strip. This script will subscribe to the topic "led_messages" on hivemqtt broker, translate the messages to set low level byte encoding (see doc), and send them on serial. 

Commands will be published by Windows MQTTX client.
"""

class Bridge():

	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config_receiver.ini')
		self.setupSerial()
		self.setupMQTT()
  
	def setupSerial(self):
		self.ser = None

		if self.config.get("Serial","UseDescription", fallback=False):
			self.portname = self.config.get("Serial","PortName", fallback="COM5")
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
		self.clientMQTT = mqtt.Client("ryanna")
		self.clientMQTT.on_connect = self.on_connect
		self.clientMQTT.on_message = self.on_message
		print("connecting to MQTT broker...")
		self.clientMQTT.connect("broker.hivemq.com",
			port= 1883, keepalive= 60)

		self.clientMQTT.loop_start()



	def on_connect(self, client, userdata, flags, rc):
		print("Connected with result code " + str(rc))

		# Subscribing in on_connect() means that if we lose the connection and
		# reconnect then subscriptions will be renewed.
		self.clientMQTT.subscribe("led_messages")


	# The callback for when a PUBLISH message is received from the server.
	def on_message(self, client, userdata, msg):
		print(msg.topic + " " + str(msg.payload))
		if msg.topic=='led_messages':
			print('{}{}'.format("Le payload", msg.payload))
   
		match msg.payload:
			case b'{\n  "msg": "RED"\n}':
				print("I'm in RED CASE!!")
				self.ser.write (b'\x01\xff')

			case b'{\n  "msg": "BLUE"\n}':
				self.ser.write (b'\x05\xff')

			case b'{\n  "msg": "GREEN"\n}':
				self.ser.write (b'\x04\xff')

   
if __name__ == '__main__':
    print("Bridge Started")
    br=Bridge()
    while(True): pass
    

