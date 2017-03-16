from machine import unique_id
from crypto import AES
import crypto

class Gateway(object):
    """Gateway class connected to a node"""
    #Classe mère pour Gateway et Node

    def __init__(self,nom="moi", nodes= {}) :
        """ Initialisation
         - [Node dictionnary : [key] = "name" ]"""
        #Création clef chiffrement à partir id machine.
        #Initialisation dictionnaire de nodes avec leur clef.
        self.key = set_size(unique_id())
        self.nodes = nodes
        self.unknown_nodes = {}
        #Répertorie le nom des nodes qui ont communiquées avec
        # nous et dont on ne connait pas le nom. Chaque nom est
        # associé à un entier indiquant le nombre de fois qu'elles ont tentées
        # de communiquer.
        #Initialisation du nom
        if(type(nom) is str):
            nom = nom.encode()
            self.nom = set_size(nom)
        elif(type(nom) is not bytes):
            raise AttributeError("Argument 'nom' should be string or bytes")
        else :
            self.nom = set_size(nom) ;


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
        """Effectue la traduction entre un nom de LoPy et sa
        clef si celle-ci est connue par la LoPy"""
        if(string in self.nodes):
            return(self.nodes[string])
        else:
            if(string in self.unknown_nodes):
                self.unknown_nodes[string] += 1;
            else:
                self.unknown_nodes[string] = 1;

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
        """Build a package for dest. Should be a key"""
        #Chiffrement data 
        data = self._crypt(data, self.key)
        #Ajout identité émetteur au début du message.
        data = self.nom + data ;
        #Cryptage émetteur.
        data = self._crypt(data, self._translateIntoKey(dest))
        return(data)

    def readMsg(self, data):
        """Read a data message. Return 0 if sender is
        unknown."""
        data = self._decrypt(data, self.key)
        #On regarde si la trame vient de quelqu'un de connu
        if(data[:16] not in self.nodes):
            return(0); #Émetteur inconnu
        else :
            data = self._decrypt(data[16:], self._translateIntoKey(data[:16]))
            return(data);

def set_size(byte, size=16):
    """Force byte having the size size (default 16)"""
    i = size - len(byte)
    if(i==0):
        return(byte)
    elif(i>0):
        for e in range(i):
            byte += b'0'
        return(byte)
    else :
        return(byte[:16])


