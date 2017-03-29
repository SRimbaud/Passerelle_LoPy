from machine import unique_id
from crypto import AES
import crypto

# On va utiliser une classe qui implemente de manière generale un noeud que ce
# soit une gateway ou un endPoint device. En effet l'heritage n'est pas fonctionnel
# a 100% en microPython on va donc creer des objets possedant le Node_Core.
# Leurs methodes feront appels aux methodes du Node_core et gereront les exceptions
# et erreurs a leur façon selon le comportement que l'on cherche.
#Les clefs et noms sont enregistrees sur 16 octets quoiqu'il arrive. 
#Complete par des 0 ou tranche s'il faut.
#Permettre de creer avec un clef de notre choix (utiliser **kwargs)


class Node_Core(object):
    """Core class for a node"""
    #Classe mère pour Gateway et Node

    def __init__(self,nom="moi", mode='G', nodes= {}) :
        """ Initialisation
         - [Node dictionnary : [key] = "name" ]"""
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
        return(self.nodes)

    def getUnknownNodes(self):
        return(self.unknown_nodes)

    def getMyName(self):
        return(self.nom)

    def getMyKey(self):
        return(self.key)

    def setNodeName(self,name):
        """Change node name, return effective save name"""
        name = set_size(name)
        self.nom = name
        return(self.nom)

    def setMyKey(self, key):
        """Change node name, return effective save key"""
        key = set_size(key)
        self.key = key
        return(self.key)

    def _crypt(self, data, key):
        """Crypt a data with the key, key.
        add the iv at the beginning of the message"""
        iv = crypto.getrandbits(128)
        cipher = AES(key, AES.MODE_CFB, iv)
        return(iv + cipher.encrypt(data))

    def _decrypt(self, data, key):
        """Decrypt a message"""
        print(data[:16])
        cipher = AES(key, AES.MODE_CFB, data[:16])
        return(cipher.decrypt(data[16:]))

    def _translateIntoKey(self, string, state ='receive'):
        """Give the key corresponding to the node named by string.
        The name should be known and associated with a key (see AddNode)
        State indicator is usefull for Gw mode. It indicates if a message
        is send or received in case if we are communicating with in unknown node."""
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
        """Change the key of a known node. Return True if succeed
        and False if the node doesn't exist (see addNode)"""
        name = set_size(name)
        key = set_size(key);
        if(name not in self.nodes):
            return(False);
        else :
            self.nodes[name] = key
            return(True);

    def buildMsg(self, data, dest, encryption = False):
        """Build a package for dest. Should be a key. Can raise a KeyError if
        data is send to an unknown device"""
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
        """Read a data message.
        Can raise KeyError if data is send from an unknown
        device and node core is created for a Gateway.
        Return a list with sender's name and message."""
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


