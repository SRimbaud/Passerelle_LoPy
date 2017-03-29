#Le module implementant une gateway.
"""
Module implementing gateway
===========================
Gateway object should be created giving a name
with a string which allows it to be human
readable.
This name correspond to device name in a LoRa
network.

Exemple
=======

>>> #Gateway code.
>>> gw = Gateway("effe") #Creating gateway named effe formated for 16 bytes long.
>>> gw.getName() 
b'effe000000000000' 
>>> gw.startLoRa() # Start LoRa service in the device.
>>> gw.addNewNode("f00a", b'NotSecureKey') #Add a device to the network.
>>> gw.sendMsg("Hello", "f00a") # Send message to device named f00a.
5

>>> # Node Code
>>> gw = Gateway("f00a")
>>> gw.addNewNode("effe", b'AnOtherSecureKey') # Add the gateway to known nodes.
>>> gw.startLoRa()
>>> gw.recvMsg() #message is saved in a FIFO.
True
>>> gw.popOldestMsg() # return a list with senders and message received.
[b'effe', b'Hello']

Default configuration doesn't crypt your data.
See L{Gateway.sendMsg} for encryption.
Each time you want to communicate you have to be sure that
the Node is saved by the gateway with method L{Gateway.addNewNode}.

"""
from node_core import Node_Core, set_size
import pycom
import socket
from network import LoRa
import os
import struct


class Gateway(object):
    """ Object which implements interface between device and LoRa network.
    This network is customized and doesn't with LoRaWAN standard.
    Each time Gateway object read a message, this message is added to
    a FIFO. Each time you want to get a message you have to pop received
    message.
    """

    def __init__(self, nom="moi", nodes={}):
        """Initialise a new Gateway.
        @param nom : Name (string) given to the node.
        @param nodes : Known nodes (dictionnary) at creation. Avoid to use it use L{addNewNode}.
        """
        self.core = Node_Core(nom, 'G', nodes)
        self.lora = 0;
        self.loraSocket = 0;
        self.sender = [] # List wich store tuple with senders and message. 

    def getSenders(self):
        """ 
        Return the entire received message FIFO.
        Should not be used except in specific case,
        prefer getOldestMsg().
        @return: Return the entire FIFO.
        """
        return(self.sender)

    def getOldestMsg(self):
        """
        @return: A list containing 2 bytes : name of senders and the
        received data.
        """
        if(self.sender != []):
            return(self.getSenders()[0])
        else :
            return([])

    def popOldestMsg(self):
        """
        This function delete the last received message. If you don't
        want to delete it use L{getOldestMsg}
        @return: A liste containing 2 bytes name of senders and data
        received.
        """
        if(self.sender != []):
            tmp = self.getSenders()
            return(tmp.pop(0))
        else :
            return([])

    def _addRcvMsg(self, name, msg):
        """
        @param name : String or byte corresponding to name emitter.
        @param msg : String or byte corresponding to received message.
        Add message to the list of senders.
        """
        self.getSenders().append([name, msg])

    def getNodes(self):
        """
        @return: Return known nodes in a dictionnary
        """
        return(self.core.getNodes())

    def getUNodes(self):
        """
        Unknown nodes is a dictionnary containing names of node which tryed
        to communicate. For each node there is a number of received and
        sended messages.
        @return: Dictionnary of non saved node from which messages have been
        received or sended.
        """
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
# On bloque antenne pour pas recevoir pendant emission.
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
        # On reactive l'antenne pour la reception.
        data = self.loraSocket.recv(512)
# On une limite de taille a la reception la voila la fameuse limite. Je mesure une
#limite 64
        if(len(data) == 0):
            return(False)
        try :
            name, data = self.core.readMsg(data,  encryption)
        except KeyError :
            return(False)

        self._addRcvMsg(name, data)
        return(True)
