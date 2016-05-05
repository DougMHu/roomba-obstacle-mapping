#!/usr/bin/python

# Copyright (c) 2010-2013 Roger Light <roger@atchoo.org>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution. 
#
# The Eclipse Distribution License is available at 
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    Roger Light - initial implementation
# Copyright (c) 2010,2011 Roger Light <roger@atchoo.org>
# All rights reserved.

# This shows a simple example of an MQTT subscriber.

import sys
import time
try:
	import paho.mqtt.client as mqtt
	print "imported"
except ImportError:
	# This part is only required to run the example from within the examples
	# directory when the module itself is not installed.
	#
	# If you have the module installed, just use "import paho.mqtt.client"
	import os
	import inspect
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../src")))
	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)
	import paho.mqtt.client as mqtt

class mqtt_sampler(object):
	def __init__(self):
		self.samples = []

		# If you want to use a specific client id, use
		# mqttc = mqtt.Client("client-id")
		# but note that the client id must be unique on the broker. Leaving the client
		# id parameter empty will generate a random id for you.
		self.mqttc = mqtt.Client()
		self.mqttc.on_message = self.on_message
		self.mqttc.on_connect = on_connect
		self.mqttc.on_publish = on_publish
		self.mqttc.on_subscribe = on_subscribe
		# Uncomment to enable debug messages
		#mqttc.on_log = on_log
		self.mqttc.connect("iot.eclipse.org", 1883, 60)

		self.mqttc.subscribe("MQTTExample/LED", 0)
		#self.message = ""
		#mqttc.publish("WigWag/Roomba/", "yoyo")

		self.mqttc.loop_start()

	def take_sample(self):
		#self.mqttc.loop_start()
		#time.sleep(1)
		#self.mqttc.loop_stop(force=False)
		# parse message for x and y
		pass

		self.message = self.parse(self.message)
		self.samples.append(self.message)

	def get_samples(self):
		self.mqttc.loop_stop(force=False)
		return self.samples

	def on_connect(self, mqttc, obj, flags, rc):
		print("rc: "+str(rc))

	def on_message(self, mqttc, obj, msg):
		print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
		self.message = msg.payload
		self.message = self.parse(self.message)
		self.samples.append(self.message)

	def on_publish(self, mqttc, obj, mid):
		print("mid: "+str(mid))

	def on_subscribe(self, mqttc, obj, mid, granted_qos):
		print("Subscribed: "+str(mid)+" "+str(granted_qos))
		# store xs and ys

	def on_log(self, mqttc, obj, level, string):
		#parse
		#append(location)
		print "message: ", string
		print(string)

	def parse(self, message):
		s=message
		x = float(s.split(",")[0].split(":")[1])
		y = float(s.split(",")[1].split(":")[1])
		#s = s.split(",")
		x_y = [x,y]
		return x_y



def on_connect(mqttc, obj, flags, rc):
	print("rc: "+str(rc))

def on_message(mqttc, obj, msg):
	print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

def on_publish(mqttc, obj, mid):
	print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
	print("Subscribed: "+str(mid)+" "+str(granted_qos))
	# store xs and ys

def on_log(mqttc, obj, level, string):
	#parse
	#append(location)
	print "message: ", string
	print(string)

# sampler = mqtt_sampler()
# sampler.take_sample()
# sampler.take_sample()
# print "samples: ", sampler.get_samples()