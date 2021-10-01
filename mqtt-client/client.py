import paho.mqtt.client as mqtt
import time 
import random
import struct

# initialize random number generator
random.seed()

class Meter:
    def __init__(self, channel):
        self.channel = channel
        self.value = 0

class HumidMeter(Meter):
    def __init__(self, channel):
        super().__init__(channel)
        self.unit = 1

    def get_value(self):
        self.value = random.randint(-128, 127)

class TempMeter(Meter):
    def __init__(self, channel):
        super().__init__(channel)
        self.unit = 0
    
    def get_value(self):
        self.value = random.randint(-128, 127)



# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# Create a MQTT client and register a callback
# for connect events
client = mqtt.Client()
client.on_connect = on_connect

# Connect to a broker
client.connect("localhost", port=1883, keepalive=60)

# Start a background loop that handles all
# communication with the MQTT broker
client.loop_start()

id = random.getrandbits(64)

meters = []
meters.append(HumidMeter(0))
meters.append(TempMeter(1))

while True:
    time.sleep(1)

    time_sec = int(time.time())
    # to pack data into a "C struct" (i.e. bytes object)
    # use the struct package. The first argument is
    # a format string describing the data format
    # and then all the data that should be packed into
    # it. In this case we have ! = network byte order 
    # Q = unsigned 8 bytes, b = signed 1 byte
    data = struct.pack("!QI", id, time_sec)
    for meter in meters:
        meter.get_value()
        meter_data = struct.pack("!BiB", meter.channel, meter.value, meter.unit)
        data += meter_data

    # publish the data to the topic some/topic
    # using the packed struct as payload and
    # MQTT QoS set to 1
    client.publish("some/topic", payload=data, qos=1)
