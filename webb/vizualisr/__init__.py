from os import truncate
from flask import Flask, render_template, flash
import datetime
import struct

ID_file = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgubbarna/prog_files/ID_file.txt"
path_to_project = "C:/Users/Jes_p/OneDrive/Dokument/python_work/Jordgubbarna/prog_files/"
# This creates the flask application and configures it
# flask run will use this to start the application properly
app = Flask(__name__)
app.config.from_mapping(
    # This is the session key. It should be a REALLY secret key!
    SECRET_KEY="553e6c83f0958878cbee4508f3b28683165bf75a3afe249e"
)
#hej
# The mapping of units in accordance with our specification
UNITS = {
    0: "°C",
    1: "RH"
}
meters = {}
# This is a placeholder that returns a fixed set of meters
# in a proper system this would look in a database or in
# the file system for a list of meters in the system
def get_meters():
    with open(ID_file, "r") as file_id:
        data = file_id.readlines()
        for line in data:
            meters[int(line.strip(), base=16)] = []
        return meters
    
def get_channels(meter):
    with open(f"{path_to_project}{meter}.bin", "rb") as file_val:
        channels = []
        for i in range(20):
            num_channels = int.from_bytes(file_val.read(1), "big")
            if num_channels == None:
                break
            file_val.read(12)
            data = file_val.read(6 * num_channels)
            for n in range(num_channels):
                channel, val, unit = struct.unpack_from("!BiB", data, (6 * n))
                if channel not in channels:
                    channels.append(channel)
        #meters[meter] = channels
        return channels

# This is a placeholder that returns a fixed set of 
# measurement data. In a proper system this would read
# the data from a database or the file system
def get_measurements(meter, channel):
    if (int(channel)) not in meters[meter]:
        # the function flash() is part of the flask system and lets us
        # register error/warning messages that should be shown on the
        # web page.
        flash(f"The meter {meter} with channel {channel} does not exist.")
        return []
    # this just generates a fixed set of measurement values
    # to have something to show...
    buffer = file_id.readlines()
    file_id.seek(0)
    measurements = []
    time = 1624537020
    for i in range(20):
        date = datetime.datetime.fromtimestamp(time)
        measurements.append((date, buffer[-(i+1)], UNITS[0]))
        time = time - 10 * 60
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
    channels = get_channels(hex(int(meter)))
    return render_template("channels.html", channels=channels)

@app.route("/meter/<meter>/channel/<channel>")
def show_measurements(meter, channel):
    measurements = get_measurements(meter, channel)
    return render_template("meter.html", meter=meter, channel=channel, measurements=measurements)