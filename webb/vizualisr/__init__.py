from flask import Flask, render_template, flash
import datetime
import struct

# Sökväg till ID-file.
ID_file = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgummorna/Jordgubbarna/prog_files/ID_file.txt"
# Sökväg till de binära filerna.
path_to_project = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgummorna/Jordgubbarna/prog_files/"
# Skapar flask aplikationen och konfigrerar den.
# flask run använder sig av denna för att starta aplikationen korrekt.
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY="553e6c83f0958878cbee4508f3b28683165bf75a3afe249e"
)

# Våra mätvärdens enheter.
UNITS = {
    0: "°C",
    1: "RH"
}

# Hämtar alla våra enheters ID-nummer i ID-file.txt samt lägger till dessa i en lista utan "\n" 
# och returnerar dessa.
def get_meters():
    meters = []
    with open(ID_file, "r") as file_id:
        data = file_id.readlines()
        for line in data:
            meters.append(line.strip())
        return meters
# Tar in meters-listan med våra id-nummer och läser av de binära filerna med mätvärden mm.
# Sedan läser vi in första byten för att kolla hur många kanaler enheten har. Om noll bryts loopen.
# Vi hoppar 12 bytes fram i filen, förbi Id och tid. Läser in (6 * antal kanaler)      
def get_channels(meter):
    with open(f"{path_to_project}{meter}.bin", "rb") as file_val:
        channels = {}
        while True:
            num_channels = int.from_bytes(file_val.read(1), "big")
            if num_channels == 0:
                break
            file_val.read(12)
            data = file_val.read(6 * num_channels)
            for n in range(num_channels):
                channel, val, unit = struct.unpack_from("!BiB", data, (6 * n))
                if channel not in channels.keys():
                    channels[channel] = unit
        return channels

# This is a placeholder that returns a fixed set of 
# measurement data. In a proper system this would read
# the data from a database or the file system
def get_measurements(meter, channel):
    packets = []
    with open(f"{path_to_project}{meter}.bin", "rb") as file_val:
        while True:
            num_channels = int.from_bytes(file_val.read(1), "big")
            if num_channels == 0:
                break
            data = file_val.read(12)
            packet = file_val.read(6 * num_channels)
            id, time_sec = struct.unpack("!QI", data)
            for n in range(num_channels):
                channel_index, value, unit = struct.unpack_from("!BiB", packet, (6 * n))
                if channel_index == channel:
                    packets.append((time_sec, value, unit))
    #if (int(channel)) not in meters[meter]:
        # the function flash() is part of the flask system and lets us
        # register error/warning messages that should be shown on the
        # web page.
       # flash(f"The meter {meter} with channel {channel} does not exist.")
       # return []
    # this just generates a fixed set of measurement values
    # to have something to show...
    measurements = []
    num_packets = len(packets)
    if num_packets < 20:
        inter = num_packets
    else:
        inter = 20
        
    for i in range(inter):
        time = packets[-(i+1)][0]
        value = packets[-(i+1)][1]
        unit = packets[-(i+1)][2]
        value = float(value / 1000)
        date = datetime.datetime.fromtimestamp(time)
        measurements.append((date, value, UNITS[unit]))
    return measurements

# @app.route registers a handler for a specific URL
# in this case the URL / (i.e. the root of the server)

file_id = open(ID_file, 'r+')
#file_id.truncate(0)
@app.route("/")
def start_page():
    meters = get_meters()
    return render_template("start.html", meters=meters)

    # using @app.route with <something> makes "something" into
    # a path variable. In the case /meter/1234/channel/5678
    # the meter-argument would be set to (the string!) 1234
    # and channel to 5678.

@app.route("/meter/<meter>")
def show_channels(meter):
    channels = get_channels(meter)
    return render_template("channels.html", channels=channels, meter=meter)

@app.route("/meter/<meter>/channel/<channel>")
def show_measurements(meter, channel):
    measurements = get_measurements(meter, int(channel))
    return render_template("meter.html", meter=meter, channel=channel, measurements=measurements)
