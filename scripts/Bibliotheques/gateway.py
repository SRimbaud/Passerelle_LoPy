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
from machine import Timer
from machine import UART
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
        @type nom: String
        @param nom : Name given to the node.
        @type nodes: dictionnary
        @param nodes : Known nodes (dictionnary) at creation. Avoid to use it use L{addNewNode}.
        """
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
        @type name : String or byte 
        @param name : Corresponding to name emitter.
        @type msg : String or byte 
        @param msg : Corresponding to received message.

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
        return(self.core.getUnknownNodes())

    def getName(self):
        """@return: Name of the Gateway """
        return(self.core.getMyName())

    def getKey(self):
        """@return: Key of the Gateway"""
        return(self.core.getMyKey())
    
    def setName(self, name):
        """
        @type name : String or bytes
        @param name : New name of your gateway
        @return: New name of the Gateway.
        """
        return(self.core.setNodeName(name))

    def setKey(self, key):
        """
        @type key: Should be a bytes (It has to or you will have troubles)
        @param key : The new key of the gateway
        @return: New key of the Gateway
        """
        return(self.core.setMyKey(key))
    
    def addNewNode(self, name, key):
        """
        @type name : String or bytes
        @param name: Name of the node
        @type key: Bytes (It has to be or you will have trouble)
        @param key: Key of the node. 

        Add a node to list of the known nodes. You are able to receive
        and send messages only to theses nodes.
        If you try to communicate (send or receive message) from a node
        which is not in this list, the name of the node which you are trying
        to communicate with is saved in a list of unknown node. You can read
        this list with L{getUNodes}.
        If the node already exist in the list of known nodes no change
        is performed and the function return C{False}, otherwise it returns
        C{True}.
        
        Note that the key is not important if you communicate without encryption.
        Both name and key lenght is set to 16.See L{set_size}

        @return: C{True} if key changed Otherwise C{False}

        see L{setNodeKey}


        B{Example} :

        >>> gw = Gateway("effe")
        >>> gw.addNewNode("f00a", b'Akey')
        True
        >>> gw.getNodes()
        {b'f00a000000000000' : b'Akey000000000000'}
        """
        return(self.core.addNode(name,key))

    def setNodeKey(self, name, key):
        """
        @type name: String or bytes
        @param name: Name of the node you to want to change the key
        @type key: Should be a bytes. (Important)
        @param key : The new key of the node

        Modify the key of a node saved in the known nodes.

        @return: True if suceed otherwise False.
        """
        return(self.core.changeNodeKey(name, key))

    def startLoRa(self):
        """Init a LoRa connection with LoRa and LoRa socket."""
        self.lora = LoRa(mode=LoRa.LORA, frequency=863000000, power_mode=LoRa.ALWAYS_ON, tx_power=14, bandwidth=LoRa.BW_250KHZ,  sf=7,  preamble=8,  coding_rate=LoRa.CODING_4_5,  tx_iq=False,  rx_iq=False)
        self.loraSocket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.loraSocket.setblocking(False)


    def stopLoRa(self):
        """Close a LoRa connection return C{True} if closed C{False} if
        exception. Exception could be raise if LoRa is already
        closed
        
        B{There is a bug it always return False. But it looks like LoRa is
        off}
        """
        try :
            self.loraSocket.close()
            self.lora.close()
            return(True)
        except :
            return(False)

    def sendMsg(self, data, target, encryption=False):
        """
        @type data: Bytes or String
        @param data : Message you want to send (48 bytes long max)
        @type target: String or Bytes
        @param target : Name of the node you want to send the message.
        @type encryption: Boolean
        @param encryption: Activte or not encryption. Default :C{False}


        Send a message to target. Target should be saved in the known node
        list.

        @return: Return the number of bytes sended. It returns False if
        the node is not in the list of known nodes or 0 if the message
        is too long (64 bytes ==> 16 bytes for name, 48 for message)
        
        """
        try :
            data = self.core.buildMsg(data, target, encryption)
        except KeyError  :
            return(False)
        else :
            return(self.loraSocket.send(data))

    def recvMsg(self,  encryption=False):
        """
        @type encryption: Boolean
        @param encryption: Enable or disable encryption.

        Check if there is any received messages. If it's the case
        read it. You cannot read a crypted message if you don't set
        encryption to C{True}
        When a message is received name of sender and the payload is
        stored in the FIFO. You can get the last received message
        with :

         - L{getOldestMsg}
         - L{popOldestMsg}
         - L{getSenders}

        @return: C{True} if message is received. Returns False if no data is
        read or if data is received from unknown nodes, (in this case 
        sender's will be saved in the list of unknown nodes see 
        L{getUNodes})
        """
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

