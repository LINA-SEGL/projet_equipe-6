# Projet de session Eté 2025
## MGA802 - Sujet spéciaux en aéronautique

Le projet suivant à été développé dans le cadre du cours de MGA802 - Sujet spéciaux en aéronautique, axé sur la programmation Python.
C'est un projet réalisé en équipe, lors de ce cours intensif sur une période de 1 semaine.


A remplir:

Introduction au code (contexte, utilité, pertinence, cadre d’utilisation)
• Fonctionnalités
• Aspects généraux
• Instructions d’installation et d’utilisation (dépendances particulières)
• Utilisation d’un exemple fourni avec le code
• Autres informations pertinentes sur le code
• Adressés aux utilisateurs et développeurs

## A propos, Utilité et cadre d'utilisation

Ce programme s'adresse aux personnes en lien avec l'aéronautique, et notamment dans le design conceptuel d'aéronefs, étape primaire nécessaire au dimensionnement "théorique" des aéronefs qui se base principalement sur les ailes.

Ce programme est utile à toute personne qui souhaite évaluer rapidement et simplement les performances d'un profil d'aile dans des conditions réelles.

Ce programme s’adresse ainsi à:

- Des étudiant·e·s ou ingénieur·e·s en aéronautique
- Toute personne souhaitant évaluer simplement un profil NACA dans un contexte réel
- Des concepteurs cherchant une base pour une étude de design préliminaire

# Programme Python: Générateur et calculateur de performance de profils d'ailes d'aéronefs.

Le programme permet de tracer des profils d'ailes de type NACA. Ils peuvent être soient importés du site [AirfoilTools](http://airfoiltools.com/airfoil/naca4digit) ou alors généré selon les paramètres rentrés par l'utilisateur.
Il est ensuite possible dans un cas ou dans l'autre de calculer les performances aérodynamiques du profil (coefficient de traînée $C_D$, de portance $C_L$ et de moment $C_M$ en fonction de l'angle d'attaque. 
Un sous-programme appelé : [XFoil](https://web.mit.edu/drela/Public/web/xfoil/) est exécuté dans le cas ou les courbes n'existent pas dans la base de données de [AirfoilTools](http://airfoiltools.com/airfoil/naca4digit).

Les coordonnées du profil et les données de performances aérodynamiques sont enregistrées dans une database créée localement qui est peuplée à chaque nouvelle création/importation de profils NACA.
Ce projet utilise les données procurées par le programme [OpenSky](https://github.com/joostlek/python-opensky), dont il faut télécharger les packages pour l'utilisation complète.

Il est possible de sélectionner un vol issu de OpenSky, et grâce aux paramètres atmosphériques de ce vol, de calculer les performances du profil étudié dans des conditions réelles, afin d'avoir une estimation (les performances d'un profil 2D ne sont pas les mêmes quand 3D). Il est envisageable d'améliorer ce programme avec une fonctionnalité permettant de passer d'un profil 2D à un profil 3D, connaissant les équations.

## Requis

Le projet de ce cours à été mis en oeuvre selon certains requis:
- Utiliser et manipuler des bases de données avec des bibliothèques scientifiques de Python.
- Réaliser une série de tâches sur ces données en les traitant avec le maximum de moyens permis par Python (écriture de fichier, filtrage, fonctions mathématiques...)
- Structuré dans une programmation orientée objet, mis sous la forme d'un module installable, documenté et fourni avec un exemple.

## Installation

Pour utilise le programme il faut faire les étapes suivantes (par exemple sur PyCharm):

- cloner le projet GitHub à partir de l'url : https://github.com/LINA-SEGL/projet_equipe-6
    - OU faire : ```git clone https://github.com/LINA-SEGL/projet_sessionE2025.git```
- Définir un environnement virtuel .venv
- Dans la console éxécuter la commande suivante:
```
pip install -e .
```
- Installer Xfoil, si le fichier xfoil.exe n'est pas présent lors du clonage, il doit se trouver dans le même dossier que le main.py (Dans le dossier : projet_session_E2025)
- Il faut absolument définir le dossier src comme fichier source.
    - Pour cela dans Pycharm faites clic-droit / Mark Directory as / Sources Root (le fichier devrait être bleu).

Installez également si cela n'est pas fait automatiquement dans l'installation précédente:

```
pip install python-opensky
```

## Utilisation

Si l'installation c'est bien passé, ce qui devrait être le cas vous devriez pouvoir lancer le main à partir du fichier main.py.

Cela lancera le programme de la même manière que l'exemple fourni.

Vous pouvez également lancer une interface web streamlit en faisant :

```
streamlit run src/projet_sessionE2025/app.py
```

DISCLAIMER:

Cependant l'interface fonctionne mais le lancement de xfoil peut ne pas fonctionner à cause des chemins d'accès aux dossiers nécessaires.
Pour le moment il est préférable d'utiliser l'interface tkinter du main.py.


## Dépendances:

- Python ≥ 3.9
- numpy
- matplotlib
- requests
- pandas
- sqlite3
- XFoil (doit être installé et accessible dans le PATH)
- OpenSky Python SDK : python-opensky

## Contribution

Ce projet est open-source. Il est ouvert à qui veut bien y contribuer.

Merci de votre implication! :heart_eyes:

## Paramétrer l'environnement

Vous aurez besoin de:
- XFoil
- Numpy
- Pandas

## Documentation

La documentation est disponible en faisant:

```
pip install -r requirements.txt
make html ou ./make.bat html sous Windows. 
```
## Architecture

L'architecture du projet est le suivant:

```
projet_equipe-6/
├── docs/ # Documentation du projet
├── src/ # Code source principal
│ ├── projet_sessionE2025/ # Package principal
│ │ ├── aero/ # calcul des performances aérodynamiques
│ │ ├── airfoil/ # Gestion des profils NACA
│ │ ├── BaseDonnees/ # Base de données
│ │ ├── donnees_vol/ # Données de vol (OpenSky)
│ │ ├── Interface/ # Interface utilisateur
│ │ ├── init.py # Fichier d'initialisation du package
│ │ ├── app.py # Point d'entrée de l'application Streamlit
│ │ └── main.py # Script principal
│ │
│ └── xfoil.exe # Binaire XFoil (nécessaire pour les calculs)
│
├── data/ # Données persistantes (profils, résultats)
├── projet_equipe_6.egg-info/ # Métadonnées du package (généré automatiquement)
│
├── EXEMPLE/ #Exemple documenté du programme
├── .gitignore # Fichiers à ignorer par Git
├── LICENSE.md
├── pyproject.toml # Configuration du package
├── README.md # Documentation actuelle
└── requirements.txt # Dépendances Python
```

## Auteurs du projet
Le projet à été développé par 3 membres:
- Lina Seghilani
- Noé Morance
- Cyril Traineau

## License

## Remerciements
- Prof. [Marlène Sanjosé]
- Prof. [Ilyass Tabiai]
- LINA-SEGL
