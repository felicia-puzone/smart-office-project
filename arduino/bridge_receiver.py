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
		self.setupMQTT()

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

