#Programme de mesure de valeur d'en potentiomètre

from gateway import Gateway
import machine
from machine import Timer
import time

def readPin(arg_list):
    """
    @type arg_list : list
    @param arg_list : Contient un pin et une Gateway (dans cet ordre)

    Utilisée pour un callback, permet de lire sur un pin ADC et
    d'émettre la valeur lue en LoRa.
    """
    apin = (arg_list[0]);
    gw = (arg_list[1]);
    
    #Lecture de la valeur.
    try :
        val = apin()
        # Rélge de 3 pour avoir une tension
        val = val * 3.16/4096 # (4096 = 2**12 -1 ==> Pas)
        gw.sendMsg("Potentiomètre : " + str(val) + " V");
        
        return True
    except Exception :
        print("Error in readPin, Alarm off")
        alarme.cancel()
        return False
    return False

#Alarme en variable globale
global alarme

#Initialisation Gateway
mylopy = "f00a"
noeud = "effe"
gw = Gateway(mylopy)
gw.addNewNode(noeud, b'NotaSecureKey')
gw.startLoRa()

#Initialisation convertisseur Analogique numérique.
adc = machine.ADC() # create ADC object
#adc.init()
apin = adc.channel(pin='P17', attn=3)

# On vient de tout initialiser.
# On crée une alarme chargée de tout lire puis envoyer sur le LoRa.
args = [apin, gw]
alarme = Timer.Alarm(readPin, 2.00, arg=args, periodic=True)

# typedef enum {
#     ADC_ATTEN_0DB = 0,
#     ADC_ATTEN_3DB, // 1
#     ADC_ATTEN_6DB, // 2
#     ADC_ATTEN_12DB, // 3
#     ADC_ATTEN_MAX, // 4
# } adc_atten_t;
