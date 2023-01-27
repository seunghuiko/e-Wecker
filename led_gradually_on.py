import time
import datetime
from grovepi import *

# Connect the LED to digital port 4
led = 4
pinMode(led, "OUTPUT")

# Connect the button to digital port 8
button = 8
pinMode(button, "INPUT")

# Set the alarm time
alarm_time = datetime.time(8, 0, 0)

while True:
    # Get the current time
    current_time = datetime.datetime.now().time()

    # If the current time is before the alarm time, gradually increase the LED brightness
    if current_time < alarm_time:
        for i in range(0, 255):
            analogWrite(led, i)
            time.sleep(0.01)

    # If the button is pressed, turn off the LED and exit the loop
    if digitalRead(button) == 1:
        analogWrite(led, 0)
        break
