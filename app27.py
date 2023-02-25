# Notwendige packages laden
from flask import Flask, render_template, request
from threading import Thread
import datetime
import webbrowser
import time
import grovepi
import vlc
import requests
import pyttsx3
from grove_rgb_lcd import *
from math import isnan
from datetime import datetime
from datetime import timedelta
import pandas as pd
from rpi_ws281x import PixelStrip, Color
import argparse

## LEDs einrichten
def colorWipe(strip, c, wait_ms=300):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, c)
        strip.show()
        time.sleep(wait_ms / 1000.0)

LED_COUNT = 82         # Number of LED pixels. -> final: ca. 88
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
args = parser.parse_args()
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

white = Color(255, 255, 255)
white1 = Color(127, 127, 127)
white2 = Color(63, 63, 63)
white3 = Color(31, 31, 31)
white4 = Color(15, 15, 15)
white5 = Color(7, 7, 7)
white6 = Color(3, 3, 3)
white7 = Color(1, 1, 1)
red = Color(255, 0, 0)
green = Color(0, 255, 0)
blue = Color(0, 0, 255)
yellow = Color(255, 255, 0)
cyan = Color(0, 255, 255)
magenta = Color(255, 0, 255)
black = Color(0, 0, 0)

## Wettervorhersage einrichten
# API key for OpenWeather API
api_key = "bbdfb34fb97b47d43ed9b09f8bd7f7fb"
# API endpoint for Berlin weather forecast
url = "http://api.openweathermap.org/data/2.5/weather?q=Berlin&appid=bbdfb34fb97b47d43ed9b09f8bd7f7fb"
# Make API request
response = requests.get(url)
data = response.json()
# Temperatur und Luftfeuchtigkeit (rF) auslesen
temperature = data["main"]["temp"]
humidity = data["main"]["humidity"]

# Button einrichten
button = 4 # Button an Port 4 anschließen
grovepi.pinMode(button, "INPUT")

# Weckton einrichten - hier koennte man dann noch alternative Sounds anlegen
birds = vlc.MediaPlayer("/home/pi/webapp/birds.mp3") # Vogelzwitschern

# Webserver einrichten 
app = Flask(__name__)
@app.route("/")

def server():
    now = datetime.now() # aktuelles Datum und Uhrzeit
    dateString = now.strftime("%d.%m.%Y") # Datum als String
    templateData = {
      'title' : 'Dein Wecker',
      'date' : dateString
      }
    weckzeit = request.args.get('weckzeit') # Weckzeit-Eingabe abgreifen
    standort = request.args.get('standort') # Standort-Eingabe abgreifen
    weckton = request.args.get('weckton')   # Weckton-Eingabe abgreifen
    # Abgegriffene Eingaben in separate Dateien abspeichern,
    # um sie auch ausserhalb der Funktion auslesen zu koennen
    file = open("Weckzeit.csv", "w")
    file.write(str(weckzeit))
    file.close()
    file = open("Standort.csv", "w")
    file.write(str(standort))
    file.close()
    file = open("Weckton.csv", "w")
    file.write(str(weckton))
    file.close()
    
    return render_template('index.html', **templateData, weckzeit=weckzeit, standort=standort, weckton=weckton)

def host():
    if __name__ == '__main__':
        app.run(debug=True, use_reloader=False, host='0.0.0.0')
        
def wecken():
    now = time.strftime("%H:%M:%S")
    weckzeit = 1
    
    while grovepi.digitalRead(button) == 0:
    
        while now != weckzeit:
            now = time.strftime("%H:%M") # now-Variable mit aktueller Uhrzeit updaten
            setRGB(0,255,0) # Hintergrundfarbe gruen fuer lcd-Display
            setText_norefresh("Es ist " + now + " Uhr")
            file = open("Weckzeit.csv", "r") # eingestellte Weckzeit auslesen
            for line in file:
                data = line.strip().split(";")
            weckzeit = data[0] # eingestellte Weckzeit auslesen
            time.sleep(0.5)
        
        if now == weckzeit:
            setRGB(255,0,0)
            setText_norefresh(now + " Uhr! " + "Zeit zum Aufstehen!")
            birds.play()            
    
    if grovepi.digitalRead(button) == 1: # wenn Button gedrueckt wird
        birds.stop()
        now = time.strftime("%H:%M")
        temp = str(round(temperature - 273.15, 0))
        hum = str(humidity)
        setRGB(0,255,0)
        setText_norefresh("Es ist " + now + " Uhr" +
                          temp + "C - "
                          + "rF: " + hum + "%")
        if "rain" in data:
            engine = pyttsx3.init()
            engine.setProperty('rate', 120)
            engine.setProperty('voice', 'german')
            engine.say("Du solltest heute einen Regenschirm mitnehmen")
            engine.runAndWait()
    
        else:
            engine = pyttsx3.init()
            engine.setProperty('rate', 120)
            engine.setProperty('voice', 'german')
            engine.say("Du brauchst heute keinen Regenschirm")
            engine.runAndWait()
            
        time.sleep(5)

def licht():
    now = time.strftime("%H:%M:%S")
    weckzeit_adj_str = ("06:00:00")
    weckzeit = ("07:00:00")
    
    while now != weckzeit_adj_str:
        now = time.strftime("%H:%M:%S") # now-Variable mit aktueller Uhrzeit updaten // string format
        file = open("Weckzeit.csv", "r") # eingestellte Weckzeit auslesen // string format
        for line in file:
            data = line.strip().split(";")
            weckzeit = data[0] # eingestellte Weckzeit auslesen
        weckzeit_dt = datetime.strptime(weckzeit, "%H:%M").time() # datetime format
        diff = "00:05" # string format
        diff_dt = datetime.strptime(diff, "%H:%M").time() # datetime format
        t1 = timedelta(hours=weckzeit_dt.hour, minutes=weckzeit_dt.minute, seconds=weckzeit_dt.second)
        t2 = timedelta(hours=diff_dt.hour, minutes=diff_dt.minute, seconds=diff_dt.second)
        weckzeit_adj_dt = t1-t2 # timedelta format
        weckzeit_adj_str = str(weckzeit_adj_dt)
        weckzeit_adj_dt = datetime.strptime(weckzeit_adj_str, "%H:%M:%S").time()
        weckzeit_adj_str = weckzeit_adj_dt.strftime("%0H:%M:%S")
        time.sleep(0.05)
        
    if now == weckzeit_adj_str:
        colorWipe(strip, white7, 200)
        colorWipe(strip, white6, 200)
        colorWipe(strip, white5, 200)
        colorWipe(strip, white4, 200)
        colorWipe(strip, white3, 200)
        colorWipe(strip, white2, 200)
        colorWipe(strip, white1, 200)
        colorWipe(strip, white, 200)

        
# Die verschiedenen Funktionen mit threading parallel ausfuehren:
thread1 = Thread(target=server)
thread2 = Thread(target=host)
thread3 = Thread(target=wecken)
thread4 = Thread(target=licht)

thread1.start()
thread2.start()
thread3.start()
thread4.start()