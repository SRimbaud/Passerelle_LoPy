from machine import unique_id
from crypto import AES
import crypto

# On va utiliser une classe qui implémente de manière générale un noeud que ce
# soit une gateway ou un endPoint device. En effet l'héritage n'est pas fonctionnel
# à 100% en microPython on va donc créer des objets possédant le Node_Core.
# Leurs méthodes feront appels aux méthodes du Node_core et géreront les exceptions
# et erreurs à leur façon selon le comportement que l'on cherche.
#Les clefs et noms sont enregistrées sur 16 octets quoiqu'il arrive. 
#Complété par des 0 ou tranché s'il faut.
#Permettre de créer avec un clef de notre choix (utiliser **kwargs)


class Node_Core(object):
    """Core class for a node"""
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

    def getNodes(self):
        return(self.nodes)

    def getUnknownNodes(self):
        return(self.unknown_nodes)

    def getMyName(self):
        return(self.nom)

    def getMyKey(self):
        return(self.key.decode())

    def setNodeName(self,name):
        """Change node name, return effective save name"""
        name = set_size(name)
        self.nom = name
        return(self.name)
    
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
        cipher = AES(key, AES.MODE_CFB, data[:16])
        return(cipher.decrypt(data[16:]))

    def _translateIntoKey(self, string, state ='receive'):
        """Give the key corresponding to the node named by string.
        The name should be known and associated with a key (see AddNode)
        State indicator is usefull for Gw mode. It indicates if a message
        is send or received in case if we are communicating with in unknown node."""
        #Nécessite gestion des returns si jamais pas de clef !
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

    def rebootKey(self):
        """Generate a key with the machine id. Use it only if you've
        changed the key and need the old one"""
        self.setMyKey(unique_id())

    def addNode(self,name,key):
        """Add a new node with her key, if the name already
        exist return 1(see changeNodeKey).
        Return name added or 1 if name already exist"""
        key = set_size(key);
        name = set_size(name)
        if(name not in self.nodes):
            self.nodes[name] = key
            return(name);
        else :
            return(1);

    def changeNodeKey(self, name, key):
        """Change the key of a known node. Return key added
        and 1 if the node doesn't exist (see addNode)"""
        key = set_size(key);
        if(name not in self.nodes):
            return(1);
        else :
            self.nodes[name] = key
            return(key);

    def buildMsg(self, data, dest):
        """Build a package for dest. Should be a key. Can raise a KeyError if
        data is send to an unknown device"""
        #On encode la taille du message sur 4 octets juste après le nom.
        dest = set_size(dest)
        #Chiffrement data
        data = self._crypt(data, self.key)
        #Ajout identité émetteur au début du message.
        data = self.nom + data ;
        #Cryptage émetteur.
        clef = self._translateIntoKey(dest, state = 'send')
        data = self._crypt(data,clef )
        return(data)

    def readMsg(self, data):
        """Read a data message.
        Can raise KeyError if data is send from an unknown
        device and node core is created for a Gateway.
        Return a list with sender's name and message."""
        data = self._decrypt(data, self.key)
        #On regarde si la trame vient de quelqu'un de connu
        name = data[:16]
        clef = self._translateIntoKey(name, state='receive')
        msg = self._decrypt(data[16:], clef )
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


