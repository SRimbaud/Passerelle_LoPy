# Ensemble de scripts python pour la Lopy

## Protocole

Une trame est chiffrée avec la clef du destinataire.
Dans cette trame se trouve le *nom* de l'émetteur (16 premiers octets, soit 26 puissance 16 noms)
suivit du message en lui même *pas de taille fixée pour l'instant*
Une LoPy possède une clef et un nom. Le nom est utilisé pour faciliter la manipulation par
un humain. Aucun lien entre le nom et la clef (on pourrait en imposer un).
Ceci est aussi fait pour éviter la transmission à chaque trame des clefs de chiffrement. On transmet son nom au lieu de transmettre sa clef. 
Cela implique que chaque LoPy possède un [dictionnaire](https://openclassrooms.com/courses/apprenez-a-programmer-en-python/les-dictionnaires-2)
dont les clefs sont les noms des autres LoPy et les valeurs les clefs de chiffrement.
Une combinaison Nom/clef de Chiffrement est entrée par l'utilisateur (qui à priori est le seul à connaitre la clef).

![Schéma principe protocole](https://github.com/SRimbaud/Passerelle_LoPy/blob/master/scripts/Sch%C3%A9ma_trame.jpg)

### Chiffrement

Pour chiffrer on utilise le code décrit par la [documentation de la LoPy](https://docs.pycom.io/pycom_esp32/library/ucrypto.AES.html ).
Afin de chiffrer correctement un nombre l'*iv* est généré aléatoirement et (nécessite bluetooth et/ou wifi activé, car se base sur le bruit mesuré)
et est placé en clair sur les 16 premiers octets de chaque trame chiffrée. **Il faut une combinaison iv + clef pour déchiffrer pas de panique**.


## Gateway

Le code est disponible pas encore testé. 


## Node

Code non écrit, très fortement basé sur celui de la gateway (copié/collé).
On évite l'héritage MicroPython supporte mal.
Devrait être disponible d'ici ce soir.
