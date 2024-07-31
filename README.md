# Smart-AIoT-Devices-for-Entrance-People-Counting

This project is designed to count and classify people using a video stream. The program uses OpenCV for image processing, a Centroid Tracker for tracking people, and an MQTT client for communication.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [License](#license)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/people_counting.git

   Navigate to the project directory:
bash
cd people_counting
Install the required Python packages:
bash
pip install -r requirements.txt
Ensure you have the necessary model files (yolov4-tiny.cfg, yolov4-tiny.weights, coco.names) in the project directory.
Usage
Set up your video capture source in the script:
python
cap = cv2.VideoCapture('path_to_your_video.mp4')
Run the script:
bash
python people_count_1122.py
Features
Real-time people counting
MQTT client for communication
Automatic backup of data and daily reset
Customizable detection zones
Configuration
Environment Variables
Create a .env file in the project directory and set the following variables:

makefile
broker=<MQTT_BROKER>
port=<MQTT_PORT>
mail=<EMAIL>
username1=<MQTT_USERNAME>
password=<MQTT_PASSWORD>
subtopic1=<MQTT_SUBSCRIBE_TOPIC>
sensor_id=<SENSOR_ID>
Parameters
Adjust the parameters in the script according to your needs:

python
input_size = 320
confThreshold = 0.01
nmsThreshold = 0.2
vertical_middle_line_position = 240
horizontal_middle_line_position = 120
Dependencies
OpenCV
NumPy
paho-mqtt
python-dotenv
