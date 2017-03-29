#Le module implémentant une gateway.

from node_core import Node_Core, set_size
from machine import Timer
from machine import UART
import pycom
import socket
from network import LoRa
import os
import struct

#Permettre création avec clef de notre choix **kwargs
#Il intégrer une taille trame pour bien lire comme il faut tout et pas 
#découper les trames cf liaison série.

class Gateway(object):

    def __init__(self, nom="moi", nodes={}):
        """Initialise un objet en utilisant le mode gateway de node
        Core."""
        self.core = Node_Core(nom, 'G', nodes)
        self.lora = 0;
        self.loraSocket = 0;
        self.sender = [] # List wich store tuple with senders and message.
        self.serialPort = UART(1, 9600)

    def getSerial(self):
        return(self.serialPort)

    def initSerial(self, baudrate=9600, bits=8, parity=None,stop=1,
            pin=("P3", "P4")):
# timeou_char semble ne pas marcher.
        self.serialPort.init(baudrate=baudrate,bits=bits,parity=parity,
                stop=stop,pins=pin)

    def deinitSerial(self):
        self.serialPort.deinit()

    def writeSerial(self, data, target):
        """Write data on serial port. Target is the name of destinatory
        (usefull for relaying messages between devices.
        sended message has the following format :
        "target\tdata\n" It could be catch with a readline.
        As for lora return False if target is unknown node.
        """
        try :
            self.core._translateIntoKey(set_size(target))
        except KeyError :
            return(False)

        self.serialPort.write(str(target))
        self.serialPort.write('\t')
        self.serialPort.write(str(data) + '\n')
        return(True)

    def readSerial(self):
        """Read a line with format described by writeSerial
        return false if no data available"""
        if (not self.serialPort.any()):
            return(False)
        data = self.serialPort.readline()
        if(data != None):
            data = data.split('\t')
            return(data[0], data[1])
        else :
            return(False)


    def getSenders(self):
        return(self.sender)

    def getOldestMsg(self):
        """Return oldest name, message received, see popOldestMsg"""
        if(self.sender != []):
            return(self.getSenders()[0])
        else :
            return([])

    def popOldestMsg(self):
        """Return and delete oldest name, message received, see popOldestMsg"""
        if(self.sender != []):
            tmp = self.getSenders()
            return(tmp.pop(0))
        else :
            return([])

    def _addRcvMsg(self, name, msg):
        self.getSenders().append([name, msg])

    def getNodes(self):
        return(self.core.getNodes())

    def getUNodes(self):
        """Return list of unknown nodes"""
        return(self.core.getUnknownNodes())

    def getName(self):
        return(self.core.getMyName())

    def getKey(self):
        return(self.core.getMyKey())
    
    def setName(self, name):
        return(self.core.setNodeName(name))

    def setKey(self, key):
        return(self.core.setMyKey(key))
    
    def addNewNode(self, name, key):
        return(self.core.addNode(name,key))

    def setNodeKey(self, name, key):
        return(self.core.changeNodeKey(name, key))

    def startLoRa(self):
        """Init a LoRa connection with LoRa and LoRa socket."""
        self.lora = LoRa(mode=LoRa.LORA, frequency=863000000, power_mode=LoRa.ALWAYS_ON, tx_power=14, bandwidth=LoRa.BW_250KHZ,  sf=7,  preamble=8,  coding_rate=LoRa.CODING_4_5,  tx_iq=False,  rx_iq=False)
        self.loraSocket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.loraSocket.setblocking(False)


    def stopLoRa(self):
        """Close a LoRa connection return True if closed false if
        exception. Exception could be raise if LoRa is already
        closed"""
        try :
            self.loraSocket.close()
            self.lora.close()
            return(True)
        except :
            return(False)

    def sendMsg(self, data, target, encryption=False):
        """Send a message to target. Target should be a known
        node return number of bytes sended."""
# On bloque antenne pour pas recevoir pendant émission.
        try :
            data = self.core.buildMsg(data, target, encryption)
        except KeyError  :
            return(False)
        else :
            return(self.loraSocket.send(data))

    def recvMsg(self,  encryption=False):
        """Check received message and read it return read
        data in an array, store readed messages in self.sender
        return True if non empty message is received"""
        # On réactive l'antenne pour la réception.
        data = self.loraSocket.recv(512)
# On une limite de taille à la réception la voilà la fameuse limite. Je mesure une
#limite 64
        if(len(data) == 0):
            return(False)
        try :
            name, data = self.core.readMsg(data,  encryption)
        except KeyError :
            return(False)

        self._addRcvMsg(name, data)
        return(True)

        # Function adapted for callback use :

    def callbackSendMsg(self, arg):
        """ arg is a liste containing 3 args
        data to send, target and the encryption mode"""
        print(self.sendMsg(arg[0], arg[1], arg[2]))

    def callbackWriteSerial(self, arg):
        """Arg is a list wich contains data to send, and the target.
        see writeSerial.
        """
        print(self.writeSerial(arg[0],arg[1]))

