#!/usr/bin/env python
# -*- coding: utf-8 -*-

from neopixel import *


# LED strip configuration:
LED_COUNT      = 256      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 12    # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


class NeopixelWrapper:

	def __init__(self):

		self.color_on = Color(1,1,0)
		self.color_off = Color(0,0,0)

		self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
		self.strip.begin()

	def matrix_to_array(self, matrix):
		arr = []
		rows = len(matrix)
		cols = len(matrix[0])

		for c in xrange(cols):
			for r in xrange(rows):
				if c % 2 == 0:
					arr.append(matrix[7 - r][31 - c])
				else:
					arr.append(matrix[r][31 - c])

		return arr

	def display(self, matrix):
		arr = self.matrix_to_array(matrix)
		for i in xrange(len(arr)):
			self.strip.setPixelColor(i, arr[i])

		self.strip.show()



