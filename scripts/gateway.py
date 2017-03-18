#Le module implémentant une gateway.

from node_core import Node_Core
import pycom
import socket
from network import LoRa
import os
import struct


class Gateway(object):
   
    def __init__(self, nom="moi", nodes={}):
        self.core = Node_Core(nom, 'G', nodes)
        self.lora = 0;
        self.loraSocket = 0;

    def addNewNode(self, name, key):
        return(self.core.addNode(name,key))
    
    def setNodeKey(self, name, key):
        return(self.core.changeNodeKey(name, key))

    def starLoRa(self):
        """Init a LoRa connection"""
        self.lora = LoRa(mode LoRa.LORA, frequency= 863000000)
        self.loraSocket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.loraSocket.setblocking(False)


    def sendMsg(self, data, target):
        data = self.core.buildMsg(data, target)
        self.loraSocket.send(data);

    def recvMsg(self):
        data = self.loraSocket.recv(512)
        data = self.core.readMsg(data)
        return(data)


