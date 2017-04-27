from network import WLAN 
from simple import MQTTClient 
import machine 
import time 
from gateway import Gateway
import pycom

 


def settimeout(duration): 
	pass

pycom.heartbeat(False)
time.sleep(0.5) 
wlan = WLAN(mode=WLAN.STA) 

pycom.rgbled(0x000055)
time.sleep(0.5)
wlan.antenna(WLAN.EXT_ANT) 


wlan.connect("AndroidAP", auth=(WLAN.WPA2, "xpov4176"), timeout=5000) 
 	



while not wlan.isconnected(): 
	machine.idle()

pycom.rgbled(0x000000)
time.sleep(0.5) 

print("Connected to Wifi\n") 
client = MQTTClient(client_id="6073", server="mqtt.opensensors.io", user="quentinthse", password="hc9aTF0W", port=1883) 
client.settimeout = settimeout 
client.connect() 

	
 
lopy =  b'effe' # nom de la lopy
node = b'f00a' # nom de la node (deuxième lopy )
cle_node = b'$\n\xc4\x00\xef\xfe'


#initialisation 
gw = Gateway(lopy)
gw.addNewNode(node,cle_node )
gw.startLoRa()
chaine = "vide"
while True : 
	try :
		if ( gw.recvMsg() ) :
			data = gw.popOldestMsg()
			print(data)
			#chaine = data[0].decode() + " : " + data[1].decode()
			chaine = data[1]
			pycom.rgbled(0xffffff)
			client.publish("/users/quentinthse/test", chaine, qos = 0) 
				
				
		else :
			pycom.rgbled(0xff0000)


	except Exception as e:
		client.publish("/users/quentinthse/test", "erreur", qos = 0)
		pass
	pycom.rgbled(0x000000)
	chaine = "vide"
