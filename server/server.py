import paho.mqtt.client as mqtt
import struct
import datetime

#meas_file = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgubbarna/exempelkod_projekt/hardv-python-example/measurements.bin"
ID_file = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgummorna/Jordgubbarna/prog_files/ID_file.txt"
path_to_project = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgummorna/Jordgubbarna/prog_files/"
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("jmj/project", qos=1)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # if we subscribe to more than one topic we need
    # to check which topic sent this message
    if msg.topic == "jmj/project":
        # By using unpack with the same format as we used for pack
        # we will get a tuple back with our data

        (id, time_sec) = struct.unpack_from("!QI", msg.payload)
        file_id.seek(0)
        id_list = file_id.readlines()
        print(id_list)
        while True:
            try:
                if not str(f"{id:#0x}\n") in id_list:
                    file_id.write(f"{id:#0x}\n")
                    meas_file = open(f"{path_to_project}{id:#0x}.bin", "wb")
                    file_id.flush()
                else:
                    meas_file = open(f"{path_to_project}{id:#0x}.bin", "ab")
                break
            except PermissionError as Err:
                print(f"\n{Err}\n")

        number_of_channels = (len(msg.payload[12:]) / 6)
        msg_to_file = int(number_of_channels).to_bytes(1, "big") + msg.payload
        meas_file.write(msg_to_file)
        meas_file.flush()
        meas_file.close()

        print(number_of_channels)

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

    client.connect("broker.hivemq.com", port=1883, keepalive=60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    client.loop_forever()
finally:
    if file_id != None:
        file_id.close()
