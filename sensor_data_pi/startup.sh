#!/bin/bash

cd /home/pi/python_project/Jordgubbarna/sensor_data_pi
pipenv install
pipenv run python client.py

