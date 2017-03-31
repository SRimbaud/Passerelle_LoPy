# Ensemble de scripts python pour la Lopy

Architecture du dossier :

- Bibliothèques : Modules pour implémenter les nœuds et Gateway.
- Codes\_basiques : Ensemble de codes de test.
- tutorial\_pycom : Fichiers python copiés/collés depuis la documentation.
- Fichiers\_Main : Ensemble de fichiers à la nomination *main.py*.
- Raspberry : Codes utilisés dans la Raspberry.


## Protocole

### Liaison LoRa

Une trame est chiffrée avec la clef du destinataire.
Dans cette trame se trouve le *nom* de l'émetteur (16 premiers octets, soit 26 puissance 16 noms)
suivit du message en lui même *pas de taille fixée pour l'instant (avec notre configuration
il semblerait que la taille totale d'une trame ne peut pas dépasser 64 octets.*
Une LoPy possède une clef et un nom. Le nom est utilisé pour faciliter la manipulation par
un humain. Aucun lien entre le nom et la clef (on pourrait en imposer un).
Ceci est aussi fait pour éviter la transmission à chaque trame des clefs de chiffrement. On transmet son nom au lieu de transmettre sa clef. 
Cela implique que chaque LoPy possède un [dictionnaire](https://openclassrooms.com/courses/apprenez-a-programmer-en-python/les-dictionnaires-2)
dont les clefs sont les noms des autres LoPy et les valeurs les clefs de chiffrement.
Une combinaison Nom/clef de Chiffrement est entrée par l'utilisateur (qui à priori est le seul à connaitre la clef).

![Schéma principe protocole](https://github.com/SRimbaud/Passerelle_LoPy/blob/master/scripts/Sch%C3%A9ma_trame.jpg)

Nous avons modifié le protocole afin de pouvoir envoyer une trame non chiffrée.
Dans ce cas nous avons uniquement le nom de l'émetteur dans les 16 premiers 
octets de la trame. Tout le reste de la trame sert à coder le message. 
On conserver cependant la méthode d'authentification faite pour le cryptage.
Si la node avec laquelle on communique ou qui communique avec nous n'a pas
un jeu Nom/clef enregistré on ne considère pas son message.

### Liaison Série :

Afin de faciliter la communication entre la Raspberry et la liaison série nous
avons mis en forme en format de trame simple permettant une lecture rapide 
avec un script.

- Début de trame : Nom sur 16 octets de l'émetteur.
- Séparateur : un \t sépare le nom de l'émetteur du reste de la trame.
- Message : Suit le message réel de la trame.
- Fin de trame : Un \n permet de conclure la trame et de la lire avec un simple

A nouveau l'objet `Gateway` permet un mécanisme d'authentification. Si l'émetteur n'est pas connu
on ne relais pas son message.

### Chiffrement

Pour chiffrer on utilise le code décrit par la [documentation de la LoPy](https://docs.pycom.io/pycom_esp32/library/ucrypto.AES.html ).
Afin de chiffrer correctement un nombre l'*iv* est généré aléatoirement et (nécessite bluetooth et/ou wifi activé, car se base sur le bruit mesuré)
et est placé en clair sur les 16 premiers octets de chaque trame chiffrée. **Il faut une combinaison iv + clef pour déchiffrer pas de panique**.


## Logique d'implémentation :

On n'a pas accès à l'héritage en microPython. On va donc simuler le comportement en créant une classe commune
aux nodes et aux gateway : `Node_Core`. Cette classe possède quelques capacités d'adaptation selon notre envie de
créer une gateway ou une node pour accélérer l'implémentation. Toutes les fonctions communes aux nodes et gateways
doivent être dans cette classe.
Une node et une gateway possèdes un champ qui est une `Node_Core`. Leurs méthodes font appels aux méthodes de cette
`Node_Core` et elles peuvent implémenter d'autres fonctionnalités.

Nous avons également ajouter des fonctions callback qui peuvent être appelées dans un callback aisément en communiquant une
liste d'arguments.

**Pour plus de détails consulter le dossier : Bibliothèques**



Last Edit : Seb 31 Mars 2017 22:16
