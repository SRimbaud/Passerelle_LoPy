from network import WLAN 
from simple import MQTTClient 
import machine 
import time 
from gateway import Gateway

 
def settimeout(duration):  
	pass 

def serialLoop() :

	def settimeout(duration): 
		pass

	a = input("Rentrer quelque chose pour confirmer la connexion au réseau")
 
	wlan = WLAN(mode=WLAN.STA) 
	wlan.antenna(WLAN.EXT_ANT) 
	wlan.connect("AndroidAP", auth=(WLAN.WPA2, "xpov4176"), timeout=5000) 
 

	while not wlan.isconnected(): 
		machine.idle()
 
	print("Connected to Wifi\n") 
	client = MQTTClient(client_id="6073", server="mqtt.opensensors.io", user="quentinthse", password="mQBh69bp", port=1883) 
	client.settimeout = settimeout 
	client.connect() 

 
	lopy =  b'effe' # nom de la lopy
	node = b'f00a' # nom de la node (deuxième lopy )
	cle_node = b'$\n\xc4\x00\xef\xfe'



    #initialisation 
	gw = Gateway(lopy)
	gw.addNewNode(node,cle_node )
	gw.startLoRa()
	#global x 
	while True : 
		gw.recvMsg()
		data = gw.popOldestMsg()
		try :
			if ( data != [] ) :
				#print(data)
				client.publish("/users/quentinthse/test", str(data[0]) + " : " + str(data[1]), qos = 0) 

		except IndexError:
            #print((x))
			pass