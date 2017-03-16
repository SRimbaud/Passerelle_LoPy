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


## Logique d'implémentation :

On n'a pas accès à l'héritage en microPython. On va donc simuler le comportement en créant une classe commune
aux nodes et aux gateway : `_Node_Core`. Cette classe possède quelques capacités d'adaptation selon notre envie de
créer une gateway ou une node pour accélérer l'implémentation. Toutes les fonctions communes aux nodes et gateways
doivent être dans cette classe.
Une node et une gateway possèdes un champ qui est une `_Node_Core`. Leurs méthodes font appels aux méthodes de cette
`_Node_Core` et elles peuvent implémenter d'autres fonctionnalités.

### Node\_Core

Classe "mère" pour nos gateways et node. Testée et fonctionnelle.

### Gateway

Code non disponible


### Node

Code non disponible




Last Edit : Seb 16 Mars 2017 22:16
