# 🔧 Guide de Dépannage

Solutions aux problèmes courants lors de l'utilisation du test autonome.

## 🔴 Problèmes de démarrage

### Erreur: "ModuleNotFoundError: No module named 'aiohttp'"

**Cause:** Les dépendances ne sont pas installées.

**Solution:**
```bash
# Option 1: Installation automatique
python setup_test.py

# Option 2: Installation manuelle
pip install -r requirements.txt

# Option 3: Installation spécifique
pip install aiohttp backoff voluptuous
```

**Vérification:**
```bash
python -c "import aiohttp; print('✓ aiohttp OK')"
python -c "import backoff; print('✓ backoff OK')"
```

---

### Erreur: "ModuleNotFoundError: No module named 'homeassistant'"

**Cause:** C'est NORMAL! Cet outil fonctionne sans Home Assistant.

**Solution:** Aucune action requise - c'est volontaire.

---

### Erreur: "Python command not found"

**Cause:** Python n'est pas dans le PATH.

**Solution Windows:**
1. Réinstaller Python avec "Add to PATH"
2. Ou utiliser le chemin complet: `C:\Python314\python.exe test_standalone.py`
3. Ou utiliser la version Microsoft Store de Python

**Solution Linux/MacOS:**
```bash
# Vérifier l'installation
which python3
python3 --version

# Ou installer python3
sudo apt install python3  # Ubuntu/Debian
brew install python3      # MacOS
```

---

### Erreur: "Permission denied" (Linux/MacOS)

**Cause:** Le fichier n'est pas exécutable.

**Solution:**
```bash
chmod +x run_test.sh
chmod +x test_standalone.py
./test_standalone.py
```

---

## 🔴 Problèmes d'authentification

### Erreur: "Authentication failed with status 401"

**Cause:** Email ou mot de passe incorrect.

**Solution:**
1. Vérifier l'email (sensible à la casse)
2. Vérifier le mot de passe
3. S'assurer que le compte Aldes Connect existe
4. Réessayer après 30 secondes

**Debug:**
```python
# Vérifier que c'est bien vos identifiants
email = input("Email: ")
password = input("Password: ")
print(f"Email: {email}")
print(f"Password: {'*' * len(password)}")
```

---

### Erreur: "Connection timeout"

**Cause:** Pas de connexion Internet ou API Aldes indisponible.

**Solution:**
1. Vérifier connexion Internet: `ping 8.8.8.8`
2. Attendre 1 minute et réessayer
3. Vérifier que l'API Aldes est accessible:
   ```bash
   curl https://aldesiotsuite-aldeswebapi.azurewebsites.net/swagger/index.html
   ```

---

### Erreur: "Connection refused"

**Cause:** Firewall ou proxy bloquant la connexion.

**Solution:**
1. Désactiver temporairement le firewall
2. Configurer le proxy si nécessaire
3. Utiliser un VPN pour contourner les blocages
4. Essayer en utilisant des données mobiles

---

## 🔴 Problèmes de récupération de données

### Message: "Aucune donnée reçue de l'API"

**Cause:** L'API retourne une liste vide.

**Solution:**
1. Vérifier que l'appareil T.One est configuré
2. Vérifier que la box AldesConnect est alimentée
3. Vérifier que AldesConnect est connectée à Internet
4. Vérifier dans l'app mobile AldesConnect que tout marche
5. Attendre quelques minutes et réessayer

---

### Message: "Aucune pièce trouvée"

**Cause:** L'appareil n'a pas de pièces configurées.

**Solution:**
1. Ouvrir l'app AldesConnect
2. Ajouter au moins 1 pièce dans "Configuration"
3. Sauvegarder et attendre la synchronisation
4. Réessayer dans le test autonome

---

### Message: "Aucun thermostat trouvé"

**Cause:** L'appareil n'a pas de thermostats configurés.

**Solution:**
1. Vérifier que des thermostats sont associés à l'appareil
2. Vérifier dans l'app AldesConnect: "Appareils → Thermostats"
3. Ajouter des thermostats si nécessaire
4. Attendre la synchronisation et réessayer

---

## 🔴 Problèmes de changement de température

### Erreur: "La température doit être entre 5°C et 40°C"

**Cause:** La valeur saisie est en dehors des limites.

**Solution:**
- Entrer une valeur entre 5 et 40
- Vérifier qu'il n'y a pas d'espace après le nombre
- Utiliser un point (.) pour les décimales: `22.5`

---

### Erreur: "ValueError: could not convert string to float"

**Cause:** Saisie invalide (caractères non numériques).

**Solution:**
- Entrer un nombre valide: `22`
- Ou nombre décimal: `22.5`
- Ne pas utiliser de texte: `vingt-deux` ❌

---

### Message: "Température modifiée!" mais aucun changement visible

**Cause:** Changement envoyé mais pas confirmé immédiatement.

**Solution:**
1. Attendre 30 secondes (le worker traite les demandes)
2. Vérifier la température dans l'app AldesConnect
3. Vérifier que la box AldesConnect est connectée
4. Réessayer si c'est un timeout réseau

---

### Erreur: "API request failed with status 400"

**Cause:** La requête est mal formée.

**Solution:**
1. Vérifier que le thermostat existe
2. Vérifier que l'ID du thermostat est correct
3. Contacter le développeur si le problème persiste

---

## 🔴 Problèmes de mode

### Message: "Cet appareil ne supporte pas le contrôle de l'eau chaude"

**Cause:** Vous avez un T.One AIR, pas AquaAIR.

**Solution:**
- Normal! L'eau chaude n'est supportée que sur T.One AquaAIR
- Le menu le détecte automatiquement
- Continuez avec les autres options

---

### Erreur lors du changement de mode

**Cause 1:** Box AldesConnect non connectée
**Solution:** Vérifier que la box est alimentée et connectée

**Cause 2:** Saisie invalide
**Solution:** Entrer un nombre entre 1 et 9 (ou 1 et 3 pour eau chaude)

**Cause 3:** Mode non supporté
**Solution:** Vérifier le type d'appareil (AIR vs AquaAIR)

---

## 🔴 Problèmes de performance

### L'authentification est très lente (> 30 secondes)

**Cause:** Réseau lent ou API Aldes surcharge.

**Solution:**
1. Vérifier votre connexion Internet: `speedtest.net`
2. Attendre quelques minutes
3. Essayer en heures creuses
4. Vérifier l'état de l'API Aldes

---

### Les commandes timeout

**Cause:** Réseau lent ou instable.

**Solution:**
1. Vérifier la connexion Internet
2. Attendre quelques minutes
3. Réessayer
4. Utiliser un VPN pour une meilleure stabilité

---

## 🔴 Problèmes de logs

### Avertissement: "DeprecationWarning: 'asyncio.iscoroutinefunction' is deprecated"

**Cause:** Version de backoff trop ancienne.

**Solution:**
```bash
pip install --upgrade backoff
```

**Note:** Cet avertissement n'affecte pas le fonctionnement.

---

## 🔴 Problèmes de sécurité

### Les identifiants sont visibles dans les logs

**Cause:** Vous avez activé la verbosité avec logging.DEBUG.

**Solution:**
- Ne pas utiliser DEBUG level en production
- Les logs produits par le script masquent automatiquement les données sensibles

**Vérification:**
```python
import logging
# Ne pas faire:
logging.basicConfig(level=logging.DEBUG)
# Faire plutôt:
logging.basicConfig(level=logging.INFO)
```

---

## 🔴 Problèmes de fermeture

### L'application ne ferme pas

**Cause:** Tâche asynchrone encore en cours.

**Solution:**
1. Appuyer sur `Ctrl+C` pour forcer l'arrêt
2. Attendre 10 secondes avant de relancer
3. Vérifier qu'il n'y a pas de processus Python en arrière-plan

---

### Message: "Lingering task after test"

**Cause:** Une tâche asynchrone n'a pas été correctement fermée.

**Solution (développeurs):**
- C'est un problème interne lors de la fermeture
- Utiliser `Ctrl+C` pour forcer l'arrêt propre
- Le script gère automatiquement la fermeture de session

---

## ✅ Vérification de santé

Executez ce script de diagnostic:

```bash
python -c "
import sys
print('Python version:', sys.version)
try:
    import aiohttp
    print('✓ aiohttp OK')
except:
    print('✗ aiohttp FAILED')
try:
    import backoff
    print('✓ backoff OK')
except:
    print('✗ backoff FAILED')
try:
    import asyncio
    print('✓ asyncio OK')
except:
    print('✗ asyncio FAILED')
"
```

---

## 📞 Besoin d'aide?

Si vous ne trouvez pas la solution:

1. **Consultez la documentation:**
   - 📖 README.md
   - 📖 TEST_STANDALONE_README.md
   - 📖 TEST_QUICK_START.md

2. **Vérifiez les logs:**
   - Cherchez "Traceback" ou "ERROR"
   - Notez le message d'erreur complet

3. **Signalez un bug:**
   - GitHub Issues avec les détails
   - Version Python, système d'exploitation
   - Message d'erreur complet
   - Étapes pour reproduire

4. **Ressources utiles:**
   - [Documentation Aldes](https://aldesiotsuite-aldeswebapi.azurewebsites.net/swagger/)
   - [GitHub du projet](https://github.com/tiagfernandes/homeassistant-aldes)
   - [Communauté Jeedom](https://community.jeedom.com)

---

## 🎯 Diagnostic rapide

```
Question: Que se passe-t-il?
├── Problème avant authentification?
│   └── Voir: "Problèmes de démarrage"
├── Erreur lors de l'authentification?
│   └── Voir: "Problèmes d'authentification"
├── Pas de données retournées?
│   └── Voir: "Problèmes de récupération de données"
├── Changement de température échoue?
│   └── Voir: "Problèmes de changement de température"
├── Changement de mode échoue?
│   └── Voir: "Problèmes de mode"
└── Autre?
    └── Voir: "Besoin d'aide?"
```

---

**Bonne chance! 🍀**
