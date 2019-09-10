#!/usr/bin/env python3
# coding: utf8
##
#	HectorHardware.py		API class for Hector9000 hardware
#
# imports
from __future__ import division

devEnvironment = True

import time
import sys
import Adafruit_PCA9685
from HectorConfig import config

# Uncomment to enable debug output.
import logging

if not devEnvironment:
    import RPi.GPIO as GPIO
    from hx711 import HX711

logging.basicConfig(level=logging.DEBUG)


class HectorHardware:

    def __init__(self, cfg):

        self.config = cfg
        if not devEnvironment:
            GPIO.setmode(GPIO.BOARD)

            hx1 = cfg["hx711"]["CLK"]
            hx2 = cfg["hx711"]["DAT"]
            hxref = cfg["hx711"]["ref"]
            self.hx = HX711(hx1, hx2)
            self.hx.set_reading_format("LSB", "MSB")
            self.hx.set_reference_unit(hxref)
            self.hx.reset()
            self.hx.tare()

            pcafreq = cfg["pca9685"]["freq"]
            self.pca = Adafruit_PCA9685.PCA9685()
            self.pca.set_pwm_freq(pcafreq)
            self.valveChannels = cfg["pca9685"]["valvechannels"]
            self.numValves = len(self.valveChannels)
            self.valvePositions = cfg["pca9685"]["valvepositions"]
            self.fingerChannel = cfg["pca9685"]["fingerchannel"]
            self.fingerPositions = cfg["pca9685"]["fingerpositions"]
            self.lightPin = cfg["pca9685"]["lightpin"]
            self.lightChannel = cfg["pca9685"]["lightpwmchannel"]
            self.lightPositions = cfg["pca9685"]["lightpositions"]

            print("arm step + dir")
            self.armEnable = cfg["a4988"]["ENABLE"]
            self.armReset = cfg["a4988"]["RESET"]
            self.armSleep = cfg["a4988"]["SLEEP"]
            self.armStep = cfg["a4988"]["STEP"]
            self.armDir = cfg["a4988"]["DIR"]
            self.armSteps = cfg["a4988"]["numSteps"]
            print("arm step %d + dir %d" % (self.armStep, self.armDir))

            GPIO.setup(self.lightPin, GPIO.OUT)
            GPIO.output(self.lightPin, False)
            GPIO.setup(self.armEnable, GPIO.OUT)
            GPIO.output(self.armEnable, True)
            GPIO.setup(self.armReset, GPIO.OUT)
            GPIO.output(self.armReset, True)
            GPIO.setup(self.armSleep, GPIO.OUT)
            GPIO.output(self.armSleep, True)
            GPIO.setup(self.armStep, GPIO.OUT)
            GPIO.setup(self.armDir, GPIO.OUT)
        print("done")


        self.pump = cfg["pump"]["MOTOR"]
        if not devEnvironment:
            GPIO.setup(self.pump, GPIO.IN)  # pump off; will be turned on with GPIO.OUT (?!?)


    def scale_readout(self):
        if not devEnvironment:
            weight = self.hx.get_weight(5)
            print("weight = %.1f" % weight)
        else:
            weight = 0
        return weight

    def scale_tare(self):
        if not devEnvironment:
            self.hx.tare()

    def pump_start(self):
        print("start pump")
        if not devEnvironment:
            GPIO.setup(self.pump, GPIO.OUT)

    def pump_stop(self):
        print("stop pump")
        if not devEnvironment:
            GPIO.setup(self.pump, GPIO.IN)

    def valve_open(self, index, open=1):
        if (index < 0 and index >= len(self.valveChannels) - 1):
            return
        if open == 0:
            print("close valve no. %d" % index)
        else:
            print("open valve no. %d" % index)
        ch = self.valveChannels[index]
        pos = self.valvePositions[index][1 - open]
        print("ch %d, pos %d" % (ch, pos))

        if not devEnvironment:
            self.pca.set_pwm(ch, 0, pos)

    def valve_close(self, index):
        if not devEnvironment:
            self.valve_open(index, open=0)

    def valve_dose(self, index, amount, timeout=30):
        sr = 0
        if not devEnvironment:
            if (index < 0 and index >= len(self.valveChannels) - 1):
                return
            t0 = time.time()
            self.scale_tare()
            self.pump_start()
            self.valve_open(index)
            sr = self.scale_readout()
            while sr < amount:
                sr = self.scale_readout()
                if (time.time() - t0) > timeout:
                    self.pump_stop()
                    self.valve_close(index)
                    return -1
                time.sleep(0.1)
            self.pump_stop()
            self.valve_close(index)
        return sr

    def finger(self, pos=0):
        if not devEnvironment:
            self.pca.set_pwm(self.fingerChannel, 0, self.fingerPositions[pos])

    def ping(self, num, retract=True):
        print("ping :-)")
        if not devEnvironment:
            self.pca.set_pwm(self.fingerChannel, 0, self.fingerPositions[1])
            for i in range(num):
                self.pca.set_pwm(self.fingerChannel, 0, self.fingerPositions[1])
                time.sleep(.15)
                self.pca.set_pwm(self.fingerChannel, 0, self.fingerPositions[2])
                time.sleep(.15)
            if retract:
                self.pca.set_pwm(self.fingerChannel, 0, self.fingerPositions[1])
            else:
                self.pca.set_pwm(self.fingerChannel, 0, self.fingerPositions[0])

    def cleanAndExit(self):
        print("Cleaning...")
        if not devEnvironment:
            GPIO.cleanup()
        print("Bye!")
        sys.exit()

    # Helper function to make setting a servo pulse width simpler.
    def set_servo_pulse(self, channel, pulse):
        pulse_length = 1000000  # 1,000,000 us per second
        pulse_length //= 60  # 60 Hz
        print('{0} us per period'.format(pulse_length))
        pulse_length //= 4096  # 12 bits of resolution
        print('{0} us per bit'.format(pulse_length))
        pulse *= 1000
        pulse //= pulse_length
        if not devEnvironment:
            self.pca.set_pwm(channel, 0, pulse)


# end class HectorHardware

if __name__ == "__main__":
    if not devEnvironment:
        hector = HectorHardware(config)
        hector.ping(int(sys.argv[1]))
        hector.finger(0)
if __name__ == "XX__main__":
    if not devEnvironment:
        hector = HectorHardware(config)
        hector.finger(0)
        hector.arm_in()
        for i in range(hector.numValves):
            print("close valve %d = channel %d" % (i, hector.valveChannels[i]))
            hector.valve_close(hector.valveChannels[i])
        input("Bitte Glas auf die Markierung stellen")
        # hector.ping(1)
        hector.valve_dose(1, 100)
        hector.valve_dose(3, 20)
        hector.finger(1)
        hector.valve_dose(11, 100)
        hector.ping(3)
        hector.finger(0)
        hector.cleanAndExit()
        print("done.")
