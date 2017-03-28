from machine import UART
from gateway import Gateway
import time
x = 0 
 
def serialLoop() :
    lopy =  b'f00a' # nom de la lopy
    node = b'effe' # nom de la node (deuxième lopy )
    cle_node = b'$\n\xc4\x00\xef\xfe'



    #initialisation 
    com = UART(1, 9600)
    com.init(9600, bits = 8,  parity = None,  stop = 1,  pins =("P3", "P4"))
    gw = Gateway(lopy)
    gw.addNewNode(node,cle_node )
    gw.startLoRa()
    global x 
    while True : 
        #Lopy f00a reception port UART, envoie en LORA
        if(com.any()) : 
            lecture= com.readall()
            print(lecture)
            if(type(lecture) is bytes) :
                print (lecture.decode())
                gw.sendMsg(lecture, node)
               
         #Lopy f00a reception LoRa, emission en UART
        gw.recvMsg()
        data = gw.popOldestMsg()
        try :
            if ( data[1] != b'' ) :
                #print("Connexion etablie : ")
                x +=1
                #print(data[0]+'\t'+data[1]+'\n')
                com.write(str(data[0]))
                com.write('\t')
                com.write(str(data[1])+'\n')
                time.sleep(0.020)
        except IndexError:
            #print((x))
            pass
        
