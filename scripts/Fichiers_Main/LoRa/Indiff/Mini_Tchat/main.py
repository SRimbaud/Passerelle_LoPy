"""Fichier surement non fonctionnel pas mis à jour avec les changements
de la dernière maj Pycom"""
import pycom
import time
import socket
from network import LoRa
import os
import struct
pycom.heartbeat(False)

def init_interactive_talk():
    #Config initiale
    lora=LoRa(mode=LoRa.LORA, frequency=863000000, power_mode=LoRa.ALWAYS_ON, tx_power=14, bandwidth=LoRa.BW_250KHZ,  sf=7,  preamble=8,  coding_rate=LoRa.CODING_4_5,  tx_iq=False,  rx_iq=False)    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    s.setblocking(False)
    return(lora, s);


def init_node():
    """Initialisation de la node cf Node code pycom."""
    # A basic package header, B: 1 byte for the deviceId, B: 1 bytes for the pkg size
    _LORA_PKG_FORMAT = "BB%ds"
    _LORA_PKG_ACK_FORMAT = "BBB"
    DEVICE_ID = 0x01


    # Open a Lora Socket, use tx_iq to avoid listening to our own messages
    lora = LoRa(mode=LoRa.LORA, tx_iq=True)
    lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    lora_sock.setblocking(False)
    return(lora, lora_sock, _LORA_PKG_FORMAT, _LORA_PKG_ACK_FORMAT,DEVICE_ID );


def communicate(message, s):
    """Envoie le message (format byte ou string) sur s
    et attend une reponse. Si une réponse est reçue 
    affiche cette réponse.
    Renvoie -1 si attente trop longue
    Renvoie 1 si message reçu et affiché.
    Renvoie 0 si message vide 
    Si attente trop longue termine le process
    s : Le socket de comm"""
    #Version par terrible car besoin d'attente de réponse.
    #Voir autre fonction pour avoir un refresh à chaque envoie.

    if(type(message) is str) :
        message = message.encode('utf-8');
    attente = True;
    compteur = 0;
    if(len(message) ==0 ) :
        return(0);
    s.send(message);
    recp=s.recv(250);

    #boucle de communication

    while(attente):
        if(recp == b''):
            recp=s.recv(250);
        else :
            attente=False;
        compteur += 1
        if(compteur > 30000) : #Ici 30s d'attente ça va.
            attente = False
            print("Waiting time too long");
            return(-1);
        time.sleep(0.001) #attente de 10 ms.

    print("Foreigner : " + recp.decode() )
    return(1);

def interactive_talk(message, s):
    """Envoie un message. Effectue une lecture uniquement avant et après chaque envoie.
    La lecture est récursive et vide le buffer.
    Lit 512 caractères.
    Envoie 0 si ok, -1 si erreur.
    s : Le socket de comm"""

    s.send(message);
    recp = s.recv(512);
    compteur = 0;
    while(recp!=b''):
        print("Foreigner : " + recp.decode());
        recp = s.recv(512);
        #sécurité
        compteur+= 1;
        if(compteur > 20) :
            print("Too many message");
            return(-1);
    return(0)

### Programme ####
def main_talk():
    lora, s = init_interactive_talk();
    print("Welcome in interactive lopy talk ! (__exit__, __help__)")
    boucle = True;
    while(boucle) :
        message = input("Me : ")
        if(message == "__exit__") :
            boucle = False;
            break;
        if (message == "__help__") :
            print("quitter : __exit__");
        else :
            interactive_talk(message, s)
            #Vidage buffer.
            s.recv(1000);


def main_node():
    lora, lora_sock , _LORA_PKG_FORMAT, _LORA_PKG_ACK_FORMAT,DEVICE_ID = init_node();
    print("Starting node mode");
    while(True):
        # Package send containing a simple string
        msg = "Device 1 Here"
        pkg = struct.pack(_LORA_PKG_FORMAT % len(msg), DEVICE_ID, len(msg), msg)
        lora_sock.send(pkg)

        # Wait for the response from the gateway. NOTE: For this demo the device does an infinite loop for while waiting the response. Introduce a max_time_waiting for you application
        waiting_ack = True
        while(waiting_ack):
            recv_ack = lora_sock.recv(256)

            if (len(recv_ack) > 0):
                device_id, pkg_len, ack = struct.unpack(_LORA_PKG_ACK_FORMAT, recv_ack)
                if (device_id == DEVICE_ID):
                    if (ack == 200):
                        waiting_ack = False
                        # If the uart = machine.UART(0, 115200) and os.dupterm(uart) are set in the boot.py this print should appear in the serial port
                        print("ACK")
                    else:
                        waiting_ack = False
                        # If the uart = machine.UART(0, 115200) and os.dupterm(uart) are set in the boot.py this print should appear in the serial port
                        print("Message Failed")

        time.sleep(5)
