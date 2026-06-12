# PhyloGames

Vulgarisation Scientifique : Arbres Phylogénétiques

# PhyloGames

## Prérequis

* Python 3.11
* Flask
* ETE3
* PyQt5

## Installation

Installer les dépendances :

```bash
pip install flask ete3 pyqt5
```

## Lancement

Depuis le dossier du projet :

```bash
python server.py
```

Le serveur démarre sur :

```text
http://127.0.0.1:5000
```

Ouvrir cette adresse dans un navigateur.

## Structure principale

```text
server.py      # serveur Flask
prune.py       # génération de l'arbre phylogénétique
taxid.nwk      # arbre de référence
templates/     # pages HTML
static/        # JavaScript, images et fichiers générés
```
