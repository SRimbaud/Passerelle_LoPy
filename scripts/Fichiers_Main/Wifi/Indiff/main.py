"""Test script for connection to wifi network"""

import machine
from network import WLAN
fichier = open("data.txt", "rw")

# configure the WLAN subsystem in station mode (the default is AP)
wlan = WLAN(mode=WLAN.STA)
# go for fixed IP settings (IP, Subnet, Gateway, DNS)

fichier.write(wlan.scan())     # scan for available networks
wlan.connect(ssid='LoPy', auth=(WLAN.WPA2, 'www.pycom.io'))
while not wlan.isconnected():
    pass
fichier.write(wlan.ifconfig())


