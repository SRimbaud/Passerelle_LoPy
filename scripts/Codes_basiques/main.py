# main.py -- put your code here!
from machine import  UART 
from network import LoRa
import socket
#import machine
#import time

# initialize LoRa in LORA mode
# more params can also be given, like frequency, tx power and spreading factor
lora = LoRa(mode=LoRa.LORA, frequency=863000000, power_mode=LoRa.ALWAYS_ON, tx_power=14, bandwidth=LoRa.BW_250KHZ,  sf=7,  preamble=8,  coding_rate=LoRa.CODING_4_5,  tx_iq=False,  rx_iq=False)

# create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
com  = UART(1, 9600)
com.init(9600, bits = 8, parity=None,  stop = 1,  pins = ("P3", "P4") )
while True :
    if( com.any() > 0 ) :
            # send some data)
        print("Liaison UART detecté")  
        lecture = com.readall()
        print (lecture)
        if(type(lecture) is bytes):
            s.setblocking(True)
            print(lecture.decode())
            s.send(lecture)

    # get any data received...
#    s.setblocking(False)
#    data = s.recv(64)
#    print(data)

    # wait a random amount of time
#    time.sleep(machine.rng() & 0x0F)
