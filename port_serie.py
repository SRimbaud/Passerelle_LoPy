from machine import UART
import pycom

com = UART(1, 9600)

com.init(baudrate=9600, bits=8, parity=None,stop=1, pins=("P3","P4"))

#com.write("données") pour écire.
