
import paho.mqtt.client as mqtt
import time 
import random
import struct
import Adafruit_DHT

# Paths for our files
temperature_file = "/sys/bus/w1/devices/28-20320e0f8cf0/temperature"
id_file = "/home/pi/python_project/Jordgubbarna/sensor_data_pi/ID.txt"
# GPIO23 on our pi that dht11 signal is connected. 
pin = 23
dht11 = Adafruit_DHT.DHT11
random.seed()


class Meter:
    def __init__(self, channel):
        self.channel = channel
        self.value = 0

class Dht11Humid(Meter):
    def __init__(self, channel):
        super().__init__(channel)
        self.unit = 1

    def get_value(self):
        h, c = Adafruit_DHT.read_retry(dht11, pin)
        self.value = int(h * 1000)

class TempMeter(Meter):
    def __init__(self, channel):
        super().__init__(channel)
        self.unit = 0
    
    def get_value(self):
        with open(temperature_file, "rb") as temp:
            self.value = int(temp.read())

class Dht11Temp(Meter):
    def __init__(self, channel):
        super().__init__(channel)
        self.unit = 0
    
    def get_value(self):
        h, c = Adafruit_DHT.read_retry(dht11, pin)
        self.value = int(c * 1000)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

# Create a MQTT client and register a callback
# for connect events
client = mqtt.Client()
client.on_connect = on_connect

# Connect to a broker
client.connect("broker.hivemq.com", port=1883, keepalive=60)

# Start a background loop that handles all
# communication with the MQTT broker
client.loop_start()
# Opens id_file and reads it. If it is empty, then we random generate an id using our
# "random libary" if not empyt we use the existing id.
with open(id_file,"r+") as id_file:
    result = id_file.readline()
    if len(result) == 0:
        id = random.getrandbits(64)
        id_file.seek(0)
        id_file.write(hex(id))
    else:
        id = int(result, base=16)

print(f"ID: {hex(id)}")

# List of sensores that are connected to our pi.
meters = []
meters.append(Dht11Humid(0))
meters.append(Dht11Temp(1))
meters.append(TempMeter(2))

# function that publish our data one time every minute.
while True:
    on_time = time.time_ns() % 60_000_000_000
    if on_time >= 0 and on_time <= 60_000_000:
        time_sec = int(time.time())
        # firstly pack id and time to data.
        data = struct.pack("!QI", id, time_sec)
        # looking for how many meters we have the list
        # loops threw all meters and gives them channel,value and unit.
        for meter in meters:
            meter.get_value()
            meter_data = struct.pack("!BiB", meter.channel, meter.value, meter.unit)
            data += meter_data

    # publish the data to the topic yrgo/hrm/project/measurement/#
    # using the packed struct as payload and
    # MQTT QoS set to 1
        client.publish(f"yrgo/hrm/project/measurement/{id}", payload=data, qos=1)
