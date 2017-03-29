import serial
import sys
import string
import time

#un fichier qui sefface et un fichier qui conserve toutes les instructions envoyees aux differentes node

#ouverture fichier serveur et port serie
fichier = open("/var/lib/owncloud/data/admin/files/ecriture/CommandeCapteur.txt","r")
ser = serial.Serial('/dev/ttyAMA0', baudrate = 9600)

#ecriture du fichier entier du serveur sur le capteur
data = fichier.read()
print data
ser.write(data)
ser.close()
fichier.close()



