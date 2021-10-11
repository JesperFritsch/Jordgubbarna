import paho.mqtt.client as mqtt
import struct
import datetime
# Sökväg till ID-file.
ID_file = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgummorna/Jordgubbarna/prog_files/ID_file.txt"
# Sökväg till de binära filerna.
path_to_project = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgummorna/Jordgubbarna/prog_files/"
# Gensvaret för när clienten mottager ett CONNACK svar från servern.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Quality of services = 1
    # Om vi tappar kontakten och den återfås kommer meddelandet skickas igen.
    client.subscribe("yrgo/hrm/project/measurement/#", qos=1)

# Gensvaret för när ett Publicerat meddelande är mottaget från servern.
def on_message(client, userdata, msg):
    # Läser ut de 12 första byten från payloaden
    # Sedan ställer vi oss högst upp i ID_file.txt och läser in den i listan id_list.
    (id, time_sec) = struct.unpack_from("!QI", msg.payload)
    file_id.seek(0)
    id_list = file_id.readlines()
    while True:
        # Om inte Payloadens ID finns i id_list skrivs denna till ID_file.txt.
        # Samt skapar en ny binärfil med dess Id-nummer.
        # Annars skriver vi binärt till den befinliga filen med append.
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
    #                                                              1 byte  4 byte      1 byte
    # Slice efter 12 bytes (efter ID och tid), för att få reda på hur många kanaler, (kanal/mätevärde/mätevärde enhet)/6
    # Sedan skickas en extra byte med payloaden med antal kanaler. 
    number_of_channels = (len(msg.payload[12:]) / 6)
    msg_to_file = int(number_of_channels).to_bytes(1, "big") + msg.payload
    meas_file.write(msg_to_file)
    meas_file.flush()
    meas_file.close()
    # Skriver ut antal kanaler på terminalen.
    print(number_of_channels)
    # Ändrar tiden från antal sekunder sedan 1970 till dagens datum och tid
    date = datetime.datetime.fromtimestamp(time_sec)
    # Skriver ut datum och Id på terminalen.
    print(f"{date}: {id:#0x}")

id_list = []

try:
    # Öppna ID_file.txt med alla Id-nummber
    file_id = open(ID_file, "r+")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    # Ansluter till borkern "broker.hivemq.com"
    client.connect("broker.hivemq.com", port=1883, keepalive=60)
    client.loop_forever()
    
finally:
    # Om allt i filen är läst stängs den.
    if file_id != None:
        file_id.close()
