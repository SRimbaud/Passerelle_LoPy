""" Client qui essaie de se connecter au serveur"""
from network import Bluetooth
import time
bt = Bluetooth()
bt.start_scan(5)

def Bluetooth_loo():
  adv = bt.get_adv()
  if adv and bt.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL) == 'Glucose':
      try:
          print("Connection...")
          conn = bt.connect(adv.mac)
          print("Connected, starting reading service...")
          services = conn.services()
          print("Service readed ....") 
          for service in services:
              time.sleep(0.050)
              if type(service.uuid()) == bytes:
                  print('Reading chars from service = {}'.format(service.uuid()))
              else:
                  print('Reading chars from service = %x' % service.uuid())
              chars = service.characteristics()
              for char in chars:
                  if (char.properties() & Bluetooth.PROP_READ):
                      print('char {} value = {}'.format(char.uuid(), char.read()))
          conn.disconnect()
          return
      except:
          print("Error while connecting or reading from the BLE device")
          return
  else:
      time.sleep(0.050)

