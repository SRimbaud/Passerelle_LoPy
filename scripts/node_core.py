from machine import unique_id
from crypto import AES
import crypto

# On va utiliser une classe qui implémente de manière générale un noeud que ce
# soit une gateway ou un endPoint device. En effet l'héritage n'est pas fonctionnel
# à 100% en microPython on va donc créer des objets possédant le Node_Core.
# Leurs méthodes feront appels aux méthodes du Node_core et géreront les exceptions
# et erreurs à leur façon selon le comportement que l'on cherche.


class _Node_Core(object):
    """Gateway class connected to a node"""
    #Classe mère pour Gateway et Node

    def __init__(self,nom="moi", mode='G', nodes= {}) :
        """ Initialisation
         - [Node dictionnary : [key] = "name" ]"""
        #Création clef chiffrement à partir id machine.
        #Initialisation dictionnaire de nodes avec leur clef.
        self.mode= mode
        self.key = set_size(unique_id())
        self.nodes = nodes
        if(mode=='G'):
            self.unknown_nodes = {}
        #Répertorie le nom des nodes qui ont communiquées avec
        # nous et dont on ne connait pas le nom. Chaque nom est
        # associé à un entier indiquant le nombre de fois qu'elles ont tentées
        # de communiquer.
        #Initialisation du nom
        self.nom = set_size(nom)
        if(self.nom == -1):
            raise AttributeError("nom should be a string or a byte or a convertible type to byte")

    def _crypt(self, data, key):
        """Crypt a data with the key, key.
        add the iv at the beginning of the message"""
        iv = crypto.getrandbits(128)
        cipher = AES(key, AES.MODE_CFB, iv)
        return(iv + cipher.encrypt(data))

    def _decrypt(self, data, key):
        """Decrypt a message"""
        iv = data[:16]
        cipher = AES(key, AES.MODE_CFB, data[:16])
        return(cipher.decrypt(data[16:]))

    def _translateIntoKey(self, string):
        """Give the key corresponding to the node named by string.
        The name should be known and associated with a key (see AddNode)"""
        #Nécessite gestion des returns si jamais pas de clef !
        if(string in self.nodes):
            return(self.nodes[string])
        elif(self.mode == 'G'):
            if(string in self.unknown_nodes):
                self.unknown_nodes[string] += 1;
            else:
                self.unknown_nodes[string] = 1;
        else :
            raise KeyError("Message received from unknown Node")
        raise KeyError("Message received from unknown Node")

    def rebootKey(self ):
        """Generate a key with the machine id. Use it only if you've
        changed the key and need the old one"""
        self.key = set_size(unique_id())

    def addNode(self,name,key):
        """Add a new node with her key, if the name already
        exist return 1(see changeNodeKey).
        Return 0 if node is added
        Modify the key to have a 16 bytes key"""
        key = set_size(key);
        if(name not in self.nodes):
            self.nodes[name] = key
            return(0);
        else :
            return(1);

    def changeNodeKey(self, name, key):
        """Change the key of a known node. Return 0
        and 1 if the node doesn't exist (see addNode)"""
        key = set_size(key);
        if(name not in self.nodes):
            return(1);
        else :
            self.nodes[name] = key
            return(0);

    def buildMsg(self, data, dest):
        """Build a package for dest. Should be a key. Can raise a KeyError if
        data is send to an unknown device"""
        #Chiffrement data
        data = self._crypt(data, self.key)
        #Ajout identité émetteur au début du message.
        data = self.nom + data ;
        #Cryptage émetteur.
        clef = self._translateIntoKey(dest)
        data = self._crypt(data,clef )
        return(data)

    def readMsg(self, data):
        """Read a data message. Return 0 if sender is
        unknown. Can raise KeyError if data is send from an unknown
        device."""
        data = self._decrypt(data, self.key)
        #On regarde si la trame vient de quelqu'un de connu
        if(data[:16] not in self.nodes):
            return(0); #Émetteur inconnu
        else :
            clef = self._translateIntoKey(data[:16])
            data = self._decrypt(data[16:], clef )
            return(data);



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

