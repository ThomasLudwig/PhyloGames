# PhyloGames

Vulgarisation Scientifique : Arbres Phylogénétiques

## Prérequis

* Python 3.10
* six
* ETE3
* scipy

## Installation

Installer les dépendances :

```bash
pip install six
pip install ete3
pip install scipy
```

## Lancement

Depuis le dossier du projet :

```bash
python phylogenie.py
```

Le serveur démarre sur :

```text
http://localhost:8000
```

Ouvrir cette adresse dans un navigateur.

## Structure principale

| Fichier/Répertoire | Fonction |
|---|---|
| install.windows.bat | Installation des dépendances pour windows dans un environnement virtuel |
| start.windows.bat   | Démarrage du jeu depuis l'environnement virtuel |
| phylogenie.py       | serveur python |
| index.html          | page principale (vide) |
| data/               | données phylogénétique |
| html/               | pages HTML, CSS, JavaScript |
| python/             | Scripts Python |

