""" Module de la LoPy effe, elle joue le rôle du serveur bluetooth"""

from network import Bluetooth
bluetooth = Bluetooth()
bluetooth.set_advertisement(name='Effe', service_uuid=b'1234567890123456')

def conn_cb (bt_o):
    events = bt_o.events() # this method returns the flags and clears the internal registry
    if events & Bluetooth.CLIENT_CONNECTED:
        print("Client connected")
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        print("Client disconnected")

bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)

bluetooth.advertise(True)

srv1 = bluetooth.service(uuid=b'1234567890123456', isprimary=True)

chr1 = srv1.characteristic(uuid=b'ab34567890123456', value=5)

def char1_cb(chr):
    print("Write request with value = {}".format(chr.value()))

char1_cb = chr1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=char1_cb)

srv2 = bluetooth.service(uuid=1234, isprimary=True)

chr2 = srv2.characteristic(uuid=4567)
