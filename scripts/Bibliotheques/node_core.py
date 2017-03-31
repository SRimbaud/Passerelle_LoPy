from machine import unique_id
from crypto import AES
import crypto
# On va utiliser une classe qui implemente de maniere generale un noeud que ce
# soit une gateway ou un endPoint device. En effet l'heritage n'est pas fonctionnel
# a 100% en microPython on va donc creer des objets possedant le Node_Core.
# Leurs methodes feront appels aux methodes du Node_core et gereront les exceptions
# et erreurs a leur façon selon le comportement que l'on cherche.
#Les clefs et noms sont enregistrees sur 16 octets quoiqu'il arrive. 
#Complete par des 0 ou tranche s'il faut.
#Permettre de creer avec un clef de notre choix (utiliser **kwargs)


class Node_Core(object):
    """
    B{Class which implements a gateway core}.
    

    This module has all the function to manage a LoRa connection.
    We usually use legacy but in mircoPython this functionnality 
    doesn't work porperly. We have an object which gives all
    LoRa management a frame management for sending frames on
    a LoRa custom network.

    Never use this Module alone, use L{Gateway}
    """
    #Classe mere pour Gateway et Node

    def __init__(self,nom="moi", mode='G', nodes= {}) :
        """
        @type nom: String or bytes
        @param nom: Name of the node we want to create.
        @type mode: Char
        @param mode : Define the core mode Gateway or not. Put
        default is set to 'G' to have a  gateway core.
        @type nodes : Dictionnary
        @param nodes : Allow you to add a list of known node at creation.
        Avoid to use it.

        Init a Node_Core object. You can init a Gateway core or a classic
        core. The gateway core is able to manage a list of unknown Node
        which are trying to communicate with the gateway.
        When a Node_Core object is created a unique key is created
        from the id of the device. According to Pycom documentation this
        id is unique : U{https://docs.pycom.io/pycom_esp32/library/machine.html#machine.unique_id}
        """
        #Creation clef chiffrement a partir id machine.
        #Initialisation dictionnaire de nodes avec leur clef.
        self.mode= mode
        self.key = set_size(unique_id())
        self.nodes = nodes
        if(mode=='G'):
            self.unknown_nodes = {}
        #Repertorie le nom des nodes qui ont communiquees avec
        # nous et dont on ne connait pas le nom. Chaque nom est
        # associe a un entier indiquant le nombre de fois qu'elles ont tentees
        # de communiquer.
        #Initialisation du nom
        self.nom = set_size(nom)
        if(self.nom == -1):
            raise AttributeError("nom should be a string or a byte or a convertible type to byte")

    def getNodes(self):
        """
        @return: List of known nodes.
        """
        return(self.nodes)

    def getUnknownNodes(self):
        """
        This method is useless if you haven't created the Node_Core
        with the Gateway mode.
        Avoid to use this function or use L{Gateway} object.
        @return: List of unknown nodes.
        """
        return(self.unknown_nodes)

    def getMyName(self):
        """
        @return: Name of the node.
        """
        return(self.nom)

    def getMyKey(self):
        """
        @return: Key of the Node
        """
        return(self.key)

    def setNodeName(self,name):
        """
        @type name: String or Bytes.
        @param name: New name of your node.
        Change node name. 
        @return: effective save name
        """
        name = set_size(name)
        self.nom = name
        return(self.nom)

    def setMyKey(self, key):
        """
        @type key: Bytes
        @param key : New key.
        Change node key.
        @return: effective save key"""
        key = set_size(key)
        self.key = key
        return(self.key)

    def _crypt(self, data, key):
        """
        @type data: Bytes
        @param data: Data you want to crypt.
        @type key : 16 Bytes.
        @param key: Encryption key.

        Crypt a message with the Advanced Encryption Standard.
        It uses CFB mode : U{https://docs.pycom.io/pycom_esp32/library/ucrypto.AES.html#ucrypto.AES}
        @return: Encrypted message.
        """
        iv = crypto.getrandbits(128)
        cipher = AES(key, AES.MODE_CFB, iv)
        return(iv + cipher.encrypt(data))

    def _decrypt(self, data, key):
        """
        @type data: Bytes
        @param data : Data you want to decrypt.
        @type key : 16 Bytes
        @param key: encryption Key.

        Decrypt a message. The 16 first Bytes should correspond
        to the iv used for encryption.
        """
        print(data[:16])
        cipher = AES(key, AES.MODE_CFB, data[:16])
        return(cipher.decrypt(data[16:]))

    def _translateIntoKey(self, string, state ='receive'):
        """
        @type string: 16 Bytes.
        @param string: Name of the node you want to get the key.
        @type state: string
        @param state: 'receive' (default) or 'send".


        Give the key corresponding to the node named by string.
        The name should be known and associated with a key (see AddNode)
        State indicator is usefull for Gw mode. It indicates if the translation
        is used for emition or reception. In both case if the node name
        is unknown the list of Unknown Nodes will updated
        
        @return: Key if it exists otherwise it raises KeyError exception.
        """
        #Necessite gestion des returns si jamais pas de clef !
        if(string in self.nodes):
            return(self.nodes[string])

        elif(self.mode == 'G'):
            if(string in self.unknown_nodes):
                self.unknown_nodes[string][state] += 1;
            else:
                self.unknown_nodes[string]= {};
                self.unknown_nodes[string]['send'] = 0;
                self.unknown_nodes[string]['receive'] = 0;
                self.unknown_nodes[string][state] += 1;
        else :
            raise KeyError("Message"+ state +" from unknown Node")
        raise KeyError("Message"+ state +" from unknown Node")

    def rebootKey(self):
        """Generate a key with the machine id. Use it only if you've
        changed the key and need the old one"""
        self.setMyKey(unique_id())

    def addNode(self,name,key):
        """Add a new node with her key, if the name already
        exist return 1(see changeNodeKey).
        Return True or False if name already exist"""
        key = set_size(key);
        name = set_size(name)
        if(name not in self.nodes):
            self.nodes[name] = key
            return(True);
        else :
            return(False);

    def changeNodeKey(self, name, key):
        """
        @type name: String or Bytes
        @param name: Name of known node you want to change the key
        @type key: Bytes.
        @param key: New Node Key.  

        Change the key of a known node. Key and name are automaticly
        resized to a 16 Bytes. It cuts the string or add 0.
        
        @return: True if succeed
        and False if the node doesn't exist (see addNode)"""
        name = set_size(name)
        key = set_size(key);
        if(name not in self.nodes):
            return(False);
        else :
            self.nodes[name] = key
            return(True);

    def buildMsg(self, data, dest, encryption = False):
        """
        @type data: String or Bytes.
        @param data: Data you want to send.
        @type dest: String or Bytes.
        @param dest: Name of the destinatory node.
        @type encryption: Boolean.
        @param encryption: Enable or disable encryption.

        Build a formatted message which can be transmitted with the
        custom LoRa network. 

        See U{https://github.com/SRimbaud/Passerelle_LoPy/blob/master/scripts/Sch%C3%A9ma_trame.jpg} for frame format.

        Note that when you want to crypt your message you need 32 
        Bytes for transmitting iv.
        @return: Built message. Can raise KeyError exception if 
        C{dest} is an unknown node (see L{_translateIntoKey})
        """
        #Voir si pas d'erreur entre byte et string pour data et dest.
        dest = set_size(dest)
        if(encryption):
            #Chiffrement data
            data = self._crypt(data, self.key)
            #Ajout identite emetteur au debut du message.
            data = self.nom + data ;
            #Cryptage emetteur.
            clef = self._translateIntoKey(dest, state = 'send')
            data = self._crypt(data,clef )
        else :
            # On traduit quand même en clef pour conserver le 
            #mecanisme d'identification.
            clef = self._translateIntoKey(dest, state = 'send')
            data = self.nom + data
        return(data)

    def readMsg(self, data, encryption = False):
        """
        @type data: Bytes.
        @param data: Data you want to read.
        @type encryption: Boolean.
        @param encryption: Param to activate decryption methods or not.

        Decrypt a frame built with L{buildMsg}. If the frame was built
        with encryption mode you have to read it with encryption mode.
        Note that if the senders of the message is unknown the list
        of unknown node will be updated and a KeyError will be raised.

        @return: list of name of senders and message sended.
        """
        name = ""
        msg = ""
        if(encryption):
            data = self._decrypt(data, self.key)
            #On regarde si la trame vient de quelqu'un de connu
            name = data[:16]
            clef = self._translateIntoKey(name, state='receive')
            msg = self._decrypt(data[16:], clef )
        else :
            # Conservation mecanisme d'identification
            name = data[:16]
            clef = self._translateIntoKey(name, state='receive')
            msg = data[16:]
        return(name, msg);



def set_size(byte, size=16):
    """
    @type byte: Bytes or String.
    @param byte : Data you want to fix the size.
    @type size: int
    @param size: Size of the output (default 16)

    Force byte having the size C{size} (default 16). It cuts the string if
    its length is superior to size or add zero in the opposite case.
    Doesn't affect the C{byte} argument if it has good size.

    Convert strings into Bytes.

    @return: -1 if byte is not a type wich can be convert into Bytes
    """
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


