# Test Autonome Aldes API

Ce fichier vous permet de tester l'intégration Aldes **sans Home Assistant**, avec une interface de menu interactive.

## Fonctionnalités

✔️ **S'authentifier** avec vos identifiants Aldes Connect
✔️ **Récupérer** les informations de votre compte
✔️ **Afficher** les thermostats et pièces disponibles
✔️ **Modifier** la température de chaque thermostat
✔️ **Changer** le mode air (Confort, Éco, Programme, etc.)
✔️ **Contrôler** le mode eau chaude (pour T.One AquaAIR)

## Installation des dépendances

```bash
# Windows
python -m pip install -r requirements.txt

# Linux/MacOS
python3 -m pip install -r requirements.txt
```

## Utilisation

### Lancer le test interactif

```bash
# Windows
python test_standalone.py

# Linux/MacOS
python3 test_standalone.py
```

### Menu principal

Une fois lancé, vous verrez le menu suivant:

```
==================================================
   MENU DE TEST ALDES API
==================================================
1. S'authentifier
2. Récupérer les données du compte
3. Changer la température d'un thermostat
4. Changer le mode air
5. Changer le mode eau chaude
6. Afficher les informations du compte
7. Quitter
==================================================
```

## Étapes typiques

### 1️⃣ S'authentifier (option 1)

```
Nom d'utilisateur: votre.email@exemple.com
Mot de passe: ••••••••

✓ Authentification réussie!
```

Utilisez les mêmes identifiants que pour l'application **AldesConnect** mobile.

### 2️⃣ Récupérer les données (option 2)

```
Récupération des données...

✓ Données récupérées avec succès!

==================================================
   INFORMATIONS DU COMPTE
==================================================

--- Appareil principal ---
Modem: MODEM123
Type d'appareil: T.One AIR

--- Pièces disponibles ---
1. Salon
   ID: room1
   Température: 20°C
   Température actuelle: 21.5°C

2. Chambre
   ID: room2
   Température: 18°C
   Température actuelle: 19.2°C

--- Thermostats disponibles ---
1. Thermostat 1
   ID: 1
   Température définie: 20°C
   Température actuelle: 21.5°C

2. Thermostat 2
   ID: 2
   Température définie: 18°C
   Température actuelle: 19.2°C

--- Mode global ---
Mode air: heat_comfort
```

### 3️⃣ Modifier la température (option 3)

```
==================================================
   CHANGER LA TEMPÉRATURE
==================================================

Thermostats disponibles:
1. Thermostat 1 (ID: 1, Température actuelle: 21.5°C)
2. Thermostat 2 (ID: 2, Température actuelle: 19.2°C)

Sélectionnez un thermostat (numéro): 1
Nouvelle température (°C): 22

Changement de la température de Thermostat 1 à 22°C...

✓ Température modifiée!
```

### 4️⃣ Changer le mode air (option 4)

```
==================================================
   CHANGER LE MODE AIR
==================================================

Modes disponibles:
1. Éteint
2. Chauffage Confort
3. Chauffage Éco
4. Chauffage Programme A
5. Chauffage Programme B
6. Rafraîchissement Confort
7. Rafraîchissement Boost
8. Rafraîchissement Programme A
9. Rafraîchissement Programme B

Sélectionnez un mode (numéro): 2

Changement du mode à Chauffage Confort...

✓ Mode modifié!
```

### 5️⃣ Changer le mode eau chaude (option 5)

**⚠️ Disponible uniquement pour T.One AquaAIR**

```
==================================================
   CHANGER LE MODE EAU CHAUDE
==================================================

Modes disponibles:
1. Éteint
2. Allumé
3. Boost

Sélectionnez un mode (numéro): 3

Changement du mode eau chaude à Boost...

✓ Mode eau chaude modifié!
```

## Dépannage

### Erreur: `ModuleNotFoundError: No module named 'homeassistant'`

C'est normal! Cet outil fonctionne **sans** Home Assistant.

### Erreur d'authentification

- Vérifiez que votre adresse email et mot de passe sont corrects
- Assurez-vous d'avoir une connexion Internet active
- Vérifiez que votre compte Aldes Connect est actif

### Aucune donnée reçue

- L'API Aldes peut être temporairement indisponible
- Essayez l'option "Récupérer les données" (option 2) à nouveau
- Vérifiez votre connexion réseau

### Erreur lors du changement de température

- Assurez-vous que la température est entre 5°C et 40°C
- La box AldesConnect doit être alimentée et connectée
- L'appareil doit être actif

## Architecture

Le script utilise les mêmes composants que l'intégration Home Assistant:

- **AldesApi**: Client API Aldes avec authentification et résilience
- **DataApiEntity**: Structure de données pour les informations du compte
- **aiohttp**: Client HTTP asynchrone
- **asyncio**: Framework asynchrone Python

## Notes de sécurité

⚠️ **Important:**
- Ne partagez jamais vos identifiants Aldes
- Ce script stocke vos identifiants en mémoire pendant la session
- Les données d'authentification ne sont pas sauvegardées sur le disque
- Fermez la session une fois terminé (option 7)

## Aide et Support

Pour des problèmes ou des questions:
- 📖 Consultez le README principal du projet
- 🐛 Signalez les bugs sur GitHub
- 💬 Posez vos questions dans les discussions

## Licence

Cette intégration n'est pas officielle et n'est pas liée à Aldes.
Utilisez-la à vos risques et périls.
