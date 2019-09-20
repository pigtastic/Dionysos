#!/usr/bin/env python3

import sys, time
from HectorConfig import config
from HectorHardware import HectorHardware

hardware = True

if hardware:
    h = HectorHardware(config)

print("VENTILE SCHLIESSEN")
print("")

if hardware:
    h.light_on()
    time.sleep(3)
    h.arm_in()

    h.pump_stop()
    for vnum in range(12):
            print("Ventil %d wird geschlossen" % (vnum,))
            time.sleep(1)
            h.valve_close(vnum)

h.light_off()

print("fertig.")


