#Le module implémentant une gateway.

from node_core import Node_Core
import pycom
import socket
from network import LoRa
import os
import struct

#Permettre création avec clef de notre choix **kwargs

class Gateway(object):

    def __init__(self, nom="moi", nodes={}):
        """Initialise un objet en utilisant le mode gateway de node
        Core."""
        self.core = Node_Core(nom, 'G', nodes)
        self.lora = 0;
        self.loraSocket = 0;
        self.loraMsg = {} #Key are nodes names and they store array of received
        #message from the node

    def getNodes(self):
        return(self.core.getNodes())

    def getUNodes(self):
        return(self.core.getUnknownNodes())

    def getName(self):
        return(self.core.getMyName())

    def getKey(self):
        return(self.core.getMyKey())
    
    def setName(self, name):
        return(self.core.setNodeName(name))

    def setKey(self, key):
        return(self.core.setNodeKey(key))
    
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
        try :
            self.loraSocket.close()
        except :
            print("Socket deja ferme")

    def sendMsg(self, data, target):
        """Send a message to target. Target should be a known
        node"""
        self.loraSocket.setblocking(True)
# On bloque antenne pour pas recevoir pendant émission.
        try :
            data = self.core.buildMsg(data, target)
        except KeyError  :
            print("Message sended to unknown node")
        else :
            print(self.loraSocket.send(data))
# On réactive l'antenne pour la réception.
        self.loraSocket.setblocking(False)
            

    def recvMsg(self):
        """Check received message and read it return read
        data in an array, store readed messages in self.loraMsg"""
        cmpt = 0
        data = self.loraSocket.recv(512)
        while(data !=b'' or cmpt > 50):
            data = self.loraSocket.recv(512)
            name, data = self.core.readMsg(data)
            self.loraMsg[name].append(data) ;
            cmpt+=1
        return(self.loraMsg)

    def del_Msg(self, name):
        """Delete all messages readed for the node called name"""
        self.loraMsg[name] = []

    def getLastReadedMsg(self, name):
        """Return the last received message from the node called name"""
        return(self.loraMsg[name][:-1])

    def getFirstReadedMsg(self, name):
        """Return older readed message for node name"""
        return(self.loraMsg[name][0])

    def delLastReadedMsg(self,name):
        """Return and delete last readed message from node called name"""
        return(self.loraMsg[name].pop(-1))

    def delFirstReadedMsg(self,name):
        """Return and delete last readed message from node called name"""
        return(self.loraMsg[name].pop(0))
