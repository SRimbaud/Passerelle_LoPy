#Le module implémentant une gateway.

from node_core import Node_Core
import pycom
import socket
from network import LoRa
import os
import struct


class Gateway(object):

    def __init__(self, nom="moi", nodes={}):
        """Initialise un objet en utilisant le mode gateway de node
        Core."""
        self.core = Node_Core(nom, 'G', nodes)
        self.lora = 0;
        self.loraSocket = 0;
        self.loraMsg = {} #Key are nodes names and they store array of received
        #message from the node

    def addNewNode(self, name, key):
        return(self.core.addNode(name,key))

    def setNodeKey(self, name, key):
        return(self.core.changeNodeKey(name, key))

    def starLoRa(self):
        """Init a LoRa connection with LoRa and LoRa socket."""
        self.lora = LoRa(mode LoRa.LORA, frequency= 863000000)
        self.loraSocket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.loraSocket.setblocking(False)


    def sendMsg(self, data, target):
        """Send a message to target. Target should be a known
        node"""
        try :
            data = self.core.buildMsg(data, target)
        except KeyError as e :
            print("Message sended to unknown node")
        else :
            self.loraSocket.send(data);

    def recvMsg(self):
        """Check received message and read it return read
        data in an array, store readed messages in self.loraMsg"""
        cmpt = 0
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
        return(slef.loraMsg[name][:-1])

    def getFirstReadedMsg(self, name):
        """Return older readed message for node name"""
        return(self.loraMsg[name][0])

    def delLastReadedMsg(self,name):
        """Return and delete last readed message from node called name"""
        return(self.loraMsg[name].pop(-1))

    def delFirstReadedMsg(self,name):
        """Return and delete last readed message from node called name"""
        return(self.loraMsg[name].pop(0))
