import serial
import sys
import string
import time

ser = serial.Serial('/dev/ttyAMA0', baudrate = 9600)
ser.flushInput()
#Attention tempo 12ms a l'envoi por reception optimale = quantim de temps debian jessie(raspPi3) = 10 ms

def set_size(byte, size=16):
    """Force byte having the size size (default 16) return -1 if byte is
    not a byte a type wich can be convert into byte"""
    #Check byte type.
    if(type(byte) is not bytes):
        try :
            byte = byte.encode()
        except Exception :
            return(-1)

    i = size - len(byte)
    if(i==0):
        return(byte)
    elif(i>0):
        for e in range(i):
            byte += b'0'
        return(byte)
    else :
        return(byte[:16])

while True :
    try :
        trame = ser.readline()
        data = trame.split('\t')
#       print set_size("effe")
#       print data[0]        

        if data[0] == "b'"+set_size("effe")+ "\'":
            fichier = open("/var/lib/owncloud/data/admin/files/lecture/effeVersServeur.txt","a")
            fichier.write(data[1])
            print data

        elif data[0] == "b'"+set_size("f00a")+"\'":
            fichier = open("/var/lib/owncloud/data/admin/files/lecture/f00aVersServeur.txt","a")
            fichier.write(data[1])
            print data

        else :
            fichier = open("/var/lib/owncloud/data/admin/files/lecture/InconnuVersServeur.txt","a")
            fichier.write("Message venant de " + data[0] + " data :" + '\n')
            fichier.write(data[1])
            print data
    except:
        print "Unexpected Error :" , sys.exc_info()




