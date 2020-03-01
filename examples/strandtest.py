#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import os
import time
from neopixel import *
import argparse
from bdffont import *
from matrixbuffer import *
import io
import requests
import xmltodict, json
import threading
from neopixelwrapper import *

MATRIX_ROWS = 8
MATRIX_COLS = 32
COLOR_BLACK = Color(0,0,0)
COLOR_BLUE = Color(0,0,255)
COLOR_GREEN = Color(255,0,0)
COLOR_AQUA = Color(255, 0, 255)
COLOR_RED = Color(0,255,0)
COLOR_PURPLE = Color(0,255,255)
COLOR_YELLOW = Color(255, 255, 0)
COLOR_WHITE = Color(255,255,255)

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)
urgency_mapping={
   'DUE':COLOR_RED,
    '0':COLOR_RED,
    '1':COLOR_RED,
    '2':COLOR_GREEN,
    '3':COLOR_GREEN,
    '4':COLOR_GREEN,
}

# LUAS API PARSING
def parse_urgency(tram_time):
    try:
      if  int(tram_time) > 4:
        return COLOR_YELLOW
    except:
      return urgency_mapping.get(tram_time)
    return urgency_mapping.get(tram_time)

def stringify_time(tram_item):
  if tram_item['@dueMins'] == 'DUE':
    return 'DUE'
  return tram_item['@destination'][0] + tram_item['@dueMins']

def parse_time(tram_item):
  return { 'urgency': parse_urgency(tram_item['@dueMins']), 'time': stringify_time(tram_item) }

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def fetch_times():
  rep = requests.get('http://luasforecasts.rpa.ie/xml/get.ashx?encrypt=false&stop=MYS&action=forecast')
  
  out = xmltodict.parse(rep.content)
  directions = out["stopInfo"]["direction"]
  for x in directions:
      if x['@name'] == "Outbound":
          tram = x["tram"]

	  if isinstance(tram, list):
          	return map(parse_time, tram)
	  else:
		return [parse_time(tram)]


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()
    font = BDFFont("/home/pi/rpi_ws281x/python/examples/5x8.bdf")
    display_wrapper = NeopixelWrapper()
    mb = MatrixBuffer(MATRIX_ROWS, MATRIX_COLS, font, display_wrapper)

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
    times = True
    try:

        while True:
	    mb.clear()
	    # current times
            previous_time = times
            times = fetch_times()
	    # if times != previous_time:
	    for index in range(len(times)):
              alignment = mb.ALIGN_RIGHT if index > 0 else mb.ALIGN_LEFT
              raw_time = times[index].get('time')
              mb.write_string(raw_time, times[index].get('urgency'), alignment)
            mb.show()
            #  time.sleep(20)
           # print ('Color wipe animations.')
           # colorWipe(display_wrapper.strip, Color(255, 0, 0))  # Red wipe
           # colorWipe(display_wrapper.strip, Color(0, 255, 0))  # Blue wipe
           # colorWipe(display_wrapper.strip, Color(0, 0, 255))  # Green wipe
           # print ('Theater chase animations.')
           # theaterChase(display_wrapper.strip, Color(127, 127, 127))  # White theater chase
           # theaterChase(display_wrapper.strip, Color(127,   0,   0))  # Red theater chase
           # theaterChase(display_wrapper.strip, Color(  0,   0, 127))  # Blue theater chase
           # print ('Rainbow animations.')
           # rainbow(display_wrapper.strip)
           # rainbowCycle(display_wrapper.strip)
           # theaterChaseRainbow(display_wrapper.strip)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(display_wrapper.strip, Color(0,0,0), 10)

