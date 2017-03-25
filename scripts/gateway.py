#Le module implémentant une gateway.

from node_core import Node_Core, set_size
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

    def sendMsg(self, data, target):
        """Send a message to target. Target should be a known
        node return number of bytes sended."""
# On bloque antenne pour pas recevoir pendant émission.
        try :
            data = self.core.buildMsg(data, target)
        except KeyError  :
            return(0)
        else :
            return(self.loraSocket.send(data))

    def recvMsg(self):
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
            name, data = self.core.readMsg(data)
        except KeyError :
            return(False)

        self._addRcvMsg(name, data)
        return(True)
