#!/usr/bin/python

import RPi.GPIO as GPIO
import argparse

reles=[23, 24, 25, 27]

parser = argparse.ArgumentParser(description='Liga ou desliga reles')
parser.add_argument('--on', metavar='N', nargs='+', type=int, help='liga reles N')
parser.add_argument('--off', metavar='N', nargs='+', type=int, help='desliga reles N')

args = parser.parse_args()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

try:
	for rele in args.on:
		print("ligando: " +str(rele) + " (#" + str(reles[rele-1]) + ")")
		GPIO.setup(reles[rele-1],GPIO.OUT)
		GPIO.setup(reles[rele-1],GPIO.LOW)

except:
	nothing = True

try:
	for rele in args.off:

		if GPIO.gpio_function(reles[rele-1]) == GPIO.OUT:
			GPIO.setup(reles[rele-1],GPIO.HIGH)
			print("desligando: " +str(rele) + " (#" + str(reles[rele-1]) + ")")
		else:
			print("erro! rele " + str(rele) + " (#" + str(reles[rele-1]) + ")  nao eh output.")

except:
	nothing = True
