[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

# Intégration Aldes T.One via AldesConnect pour Home Assistant

Cette intégration permet d'ajouter le produit Aldes T.One à Home Assistant via le cloud. Vous devez disposer de la box AldesConnect, connectée à l'appareil, configurée et fonctionnelle dans l'application mobile AldesConnect.

## Fonctionnalités prises en charge

| **Fonctionnalité**                                                                                                                                                                                                             | **T.One® AIR** | **T.One® AquaAIR** |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------: | :----------------: |
| **Mode Air** <br>- Éteint<br>- Chauffage Comfort<br>- Chauffage Eco<br>- Chauffage Prog A<br>- Chauffage Prog B<br>- Rafraîchissement Comfort<br>- Rafraîchissement Boost<br>- Rafraîchissement A<br>- Rafraîchissement Prog B |       ✔️        |         ✔️          |
| **Mode Eau chaude** <br>- Éteint<br>- Allumé<br>- Boost                                                                                                                                                                        |       ❌        |         ✔️          |
| **Connectivité**                                                                                                                                                                                                               |       ✔️        |         ✔️          |
| **Température de la pièce principale**                                                                                                                                                                                         |       ✔️        |         ✔️          |
| **Quantité d'eau chaude disponible**                                                                                                                                                                                           |       ❌        |         ✔️          |
| **Capteur de température pour chaque pièce**                                                                                                                                                                                   |       ✔️        |         ✔️          |
| **Entité thermostat pour chaque pièce**                                                                                                                                                                                        |       ✔️        |         ✔️          |
| **Composition du foyer**                                                                                                                                                                                                       |       ❌        |         ✔️          |
| **Cycle Antilegionelle**                                                                                                                                                                                                       |       ❌        |         ✔️          |
| **Configuration des tarifs électriques**                                                                                                                                                                                       |       ✔️        |         ✔️          |
| **Mode vacances**                                                                                                                                                                                                              |       ✔️        |         ✔️          |
| **Statistiques et coûts**                                                                                                                                                                                                      |       ✔️        |         ✔️          |
| **Surveillance du filtre**                                                                                                                                                                                                     |       ✔️        |         ✔️          |
| **Carte de planning**                                                                                                                                                                                                          |       ✔️        |         ✔️          |
| **Carte de maintenance**                                                                                                                                                                                                       |       ✔️        |         ✔️          |
| **État de santé API**                                                                                                                                                                                                          |       ✔️        |         ✔️          |

## Évolutions v3.5 → v3.7

### Nouveaux capteurs de diagnostic

| Capteur | Rôle |
|---------|------|
| `sensor.<device>_api_health` | État de connexion à l'API Aldes (`online`, `offline`, `degraded`, `retrying`) |
| `sensor.<device>_pending_commands` | File d'attente des commandes + historique succès/échecs |
| `sensor.<device>_system_alert` | État général du système |
| `sensor.<device>_device_info` | Détails techniques (référence, type, modem, filtres...) |
| `sensor.<device>_settings` | Paramètres (composition foyer, antilégionelle, tarifs) |
| `sensor.<device>_temperature_limits` | Limites min/max chauffage et clim |
| `sensor.<device>_thermostats_count` | Liste des thermostats avec leurs températures |

### Carte Lovelace « Maintenance »

Nouvelle carte custom auto-enregistrée. Affiche la file d'active des commandes, l'état de connexion API, et l'historique avec timestamps de mise en file → exécution.

```yaml
type: custom:aldes-maintenance-card
modem_entity: sensor.<device>_pending_commands
connectivity_entity: sensor.<device>_api_health
```

### Auto-enregistrement Lovelace

Les ressources JS des cartes sont automatiquement déclarées dans Lovelace à l'installation. Plus besoin d'ajouter manuellement les ressources dans Paramètres.

### Fiabilité et robustesse

- **Timestamps doubles** : l'historique affiche `14:30:00→14:30:05 - action` (file d'attente → exécution/réel)
- **Capteur API Health** retravaillé pour ne plus rester bloqué en `unavailable` après une erreur réseau passagère
- **Attribut `integration_version`** sur tous les capteurs pour faciliter le diagnostic
- **Éditeur visuel** pour configurer la carte maintenance (plus besoin d'YAML)
- **Champ connectivité** dans la carte : affiche le statut live via `sensor.<device>_api_health`

## Stabilité et Robustesse

Cette intégration a été renforcée pour garantir une connexion stable et sécurisée avec le cloud Aldes :

- **Authentification "Officielle"** : Utilisation des en-têtes (User-Agent, API Key) et de la signature de l'application Android officielle pour éviter les blocages de sécurité (WAF) et garantir la pérennité de l'accès.
- **Résilience Réseau** : Intégration d'un système de réessai automatique (Backoff exponentiel) qui gère les micro-coupures ou les lenteurs de l'API sans faire planter l'intégration.
- **File d'attente intelligente** : Les changements de température multiples (ex: changement de mode global) sont traités séquentiellement via un worker dédié pour ne jamais surcharger l'API Aldes.
- **Sécurité des Logs** : Masquage automatique des mots de passe et données sensibles dans les journaux de débogage.

## Expérience Utilisateur (UX)

- **Zéro Latence (Optimistic State)** : L'interface réagit instantanément à vos commandes. Plus d'effet "flip-flop" où la température revient à l'ancienne valeur pendant quelques secondes. L'intégration maintient l'état souhaité localement en attendant la confirmation du Cloud Aldes.
- **Persévérance (Auto-Retry)** : Si le Cloud Aldes ne prend pas en compte votre commande immédiatement (perte de message silencieuse), l'intégration le détecte automatiquement après 1 minute et renvoie la commande (jusqu'à 3 fois), tout en maintenant l'affichage correct pour l'utilisateur.

## 🧪 Test Autonome (Sans Home Assistant)

Pour tester l'intégration **sans Home Assistant**, un outil de menu interactif est disponible :

### Démarrage rapide

**Windows:**
```cmd
python test_standalone.py
```

**Linux/MacOS:**
```bash
python3 test_standalone.py
```

### Fonctionnalités

✔️ S'authentifier avec Aldes Connect  
✔️ Récupérer les informations du compte  
✔️ Afficher les thermostats et pièces  
✔️ Modifier la température  
✔️ Changer le mode air (Confort, Éco, Programme...)  
✔️ Contrôler le mode eau chaude (T.One AquaAIR)

### 🆘 Pas de données affichées?

Si vous voyez "Aucune pièce trouvée" ou "Aucun thermostat trouvé":

1. **Diagnostiquer:** `python debug_api_response.py`
2. **Corriger automatiquement:** `python autofix_parse.py`
3. **Documenter:** Consultez `QUICK_FIX.md`

## Installation

Dans HACS, ajoutez le dépôt personnalisé <https://github.com/tiagfernandes/homeassistant-aldes> et sélectionnez la catégorie Intégration.

### Mise à jour depuis v3.5.0

L'intégration s'auto-enregistre et les nouvelles entités (API Health, Pending Commands, etc.) apparaissent automatiquement après redémarrage. Aucune action manuelle n'est requise.

## ⚠️ Avertissement Légal

**Cette intégration n'est pas officielle et n'a aucun lien avec Aldes.** Elle est développée et maintenue par la communauté. Les créateurs et contributeurs de cette intégration ne sont pas responsables des dysfonctionnements, pertes de données, dommages matériels ou immatériels qui pourraient résulter de son utilisation. Utilisez-la à vos risques et périls.

## Configuration

Le nom d'utilisateur et le mot de passe demandés lors de la configuration sont les mêmes que ceux que vous utilisez pour l'application mobile Aldes Connect.

### Carte de maintenance

Une fois l'intégration installée, ajoutez une carte manuelle :

```yaml
type: custom:aldes-maintenance-card
modem_entity: sensor.aldes_XXXX_pending_commands
connectivity_entity: sensor.aldes_XXXX_api_health
```

Vous pouvez aussi utiliser l'éditeur visuel : cliquez sur "Modifier" dans le coin droit de la carte.

### Carte de planning interactive (optionnel)

Pour utiliser la carte de planning avec grille éditable :

1. **Déclarer la ressource Lovelace**
   Allez dans **Paramètres → Tableaux de bord → Ressources** et ajoutez :
   ```yaml
   url: /aldes_planning_card.js
   type: module
   ```

2. **Ajouter la carte à votre tableau de bord**
   Configuration minimale (auto-découverte des plannings) :
   ```yaml
   type: custom:aldes-planning-card
   ```

   Ou avec entités explicites :
   ```yaml
   type: custom:aldes-planning-card
   entities:
     - sensor.aldes_XXXX_planning_heating_prog_a
     - sensor.aldes_XXXX_planning_heating_prog_b
     - sensor.aldes_XXXX_planning_cooling_prog_c
     - sensor.aldes_XXXX_planning_cooling_prog_d
   ```

3. **Fonctionnalités**
   - Sélecteur de programme (A/B/C/D)
   - Grille interactive : clic pour basculer Confort ↔ Eco (chauffage) ou Confort ↔ Off (climatisation)
   - Envoi automatique via service `aldes.set_week_planning`
   - Indicateur de chargement et confirmation/erreur
   - Légende des modes avec code couleur

📖 [Documentation complète de la carte](custom_components/aldes/lovelace/LOVELACE_SETUP.md)

## Crédits

- [Base du projet](https://github.com/guix77/homeassistant-aldes)
- [API doc](https://community.jeedom.com/t/aldes-connect-api/57068)
- [Swagger Aldes](https://aldesiotsuite-aldeswebapi.azurewebsites.net/swagger/index.html?urls.primaryName=V5)
- [Exemples d'authentification et d'appel API](https://github.com/aalmazanarbs/hassio_aldes)
- [Plus de documentation API](https://community.jeedom.com/t/aldes-t-one-api-php/94269)
- [Blueprint d'intégration](https://github.com/custom-components/integration_blueprint)

## Voir aussi

- <https://github.com/guix77/esphome-aldes-tone> : Connexion du produit T.One avec ESPHome
- <https://github.com/Fredzxda/homeassistant-aldes> : EASYHOME PureAir Compact CONNECT

<a href="https://www.buymeacoffee.com/tiagfernandes" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;"></a>
