from network import LoRa
import socket
import time
import binascii

def main():
# Initialize LoRa in LORAWAN mode.
    lora = LoRa(mode=LoRa.LORAWAN)

# create an OTAA authentication parameters
    app_eui = binascii.unhexlify('AD A4 DA E3 AC 12 67 6B'.replace(' ',''))
    app_key = binascii.unhexlify('11 B0 28 2A 18 9B 75 B0 B4 D2 D8 C7 FA 38 54 8B'.replace(' ',''))

# join a network using OTAA (Over the Air Activation)
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

# wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        print('Not yet joined...')

# create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)

# send some data
    s.send(bytes([0x01, 0x02, 0x03]))

# make the socket non-blocking
# (because if there's no data received it will block forever...)
    s.setblocking(False)

# get any data received (if any...)
    data = s.recv(64)
    print(data)
