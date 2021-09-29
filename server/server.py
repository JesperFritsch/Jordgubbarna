import paho.mqtt.client as mqtt
import struct
import datetime

#meas_file = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgubbarna/exempelkod_projekt/hardv-python-example/measurements.bin"
ID_file = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgubbarna/exempelkod_projekt/hardv-python-example/prog_files/ID_file.txt"
some_path = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgubbarna/exempelkod_projekt/hardv-python-example/prog_files/"
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("some/topic", qos=1)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # if we subscribe to more than one topic we need
    # to check which topic sent this message
    if msg.topic == "some/topic":
        # By using unpack with the same format as we used for pack
        # we will get a tuple back with our data

        
        (id, time_sec) = struct.unpack_from("!QI", msg.payload)
        file_id.seek(0)
        id_list = file_id.readlines()
        print(id_list)
        if not str(f"{id}\n") in id_list:
            file_id.write(f"{id}\n")
            meas_file = open(f"{some_path}{id}.bin", "wb")
            file_id.flush()
        else:
            meas_file = open(f"{id}.bin", "ab")
        number_of_meters = (len(msg.payload[12:]) / 6)
        msg_to_file = int(number_of_meters).to_bytes(1, "big") + msg.payload
        meas_file.write(msg_to_file)
        meas_file.close()

        print(number_of_meters)

        date = datetime.datetime.fromtimestamp(time_sec)
        print(f"{date}: {id:#0x}")

# Create a MQTT client with callbacks for
# connecting to the MQTT server and receiving data
id_list = []

try:
    file_id = open(ID_file, "r+")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", port=1883, keepalive=60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    client.loop_forever()
finally:
    if file_id != None:
        file_id.close()
