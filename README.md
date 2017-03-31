# Projet Passerelle Wifi/LoRa/Bluetooth.

Vous pouvez trouver la documentation du code source [ici](https://srimbaud.github.io/Passerelle\_LoPy/)
Vous trouverez dans le dossier scripts de la branche master tous les scripts et informations nécessaire
à la mise en place de la passerelle.

On trouve également le [Dépôt Github de Congduc Pham](https://github.com/CongducPham/LowCostLoRaGw) pour
s'aider.

## Utilisation de LoPy avec carte de prototypage Pycom :


* [Installer l'IDE Pymakr](https://www.pycom.io/pymakr/)
* [Utiliser Pymakr](https://docs.pycom.io/pycom_esp32/pycom_esp32/toolsandfeatures.html#pymakr-ide)


## Utilisation de LoPy sans carte de prototypage Pycom :

### Se connecter à la LoPy :

* Alimenter la Lopy en 5V.
* Se connecter à son réseau Wifi mdp : www.pycom.io
* Dans un shell lancer : telnet 192.168.4.1
	* login : micro
	* mdp : python

On a un shell python sur la LoPy.

### Pour éditer les fichiers de la LoPy avec FileZilla :

* Depuis le gestionnaire de site demander une connection.
* Une fois connecté naviguer dans votre arborescence ou
celle de la LoPy.
*  On ouvre le dossier Flash dans lequel
apparaît boot.py et main.py. On ne **SUPPRIME PAS** boot.py.
On peut ajouter de nouveaux fichiers.

Pour éditer boot.py ou main.py 

* Créer des fichiers du même nom dans votre arborescence.
* Double cliquer sur celui dans votre ordi.
* Choisir remplacer. (Un back up est utile pour pas
perdre celui sur votre ordi si mauvaise manip.)

On peut ajouter des modules à la LoPy qu'on l'on pourra
importer dans le main ou le boot ou le shell.


### Configuration FileZilla :

* Utiliser filezilla.
* Fichier>Gestionnaire de site (Ou Ctrl + S)
* Nouveau Site
* Hôte 192.168.4.1 Port (laisser vide, ou choisir le port que vous voulez.)
* Protocole : FTP
* Chiffrement : Connexion FTP simple (non sécurisée).
* Autres paramètres au choix (Testé) : 
	 * Demander mot de passe
	 * avec login "micro"
* Onglet paramètre de transfert 
	* Passif
	* Limiter le nombre de connection simultannée à 1.

* Onglet Jeu de caractères
	* Detection auto (j'ai pas testé le reste)




Tuteur(s) : Sylvain Huet.


Last edit : Seb 16 Mars 2017
