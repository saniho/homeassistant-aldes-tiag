[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/tiagfernandes/homeassistant-aldes)](https://github.com/tiagfernandes/homeassistant-aldes/releases)
[![License](https://img.shields.io/github/license/tiagfernandes/homeassistant-aldes)](LICENSE)

# Intégration Aldes T.One via AldesConnect pour Home Assistant

Cette intégration permet d'ajouter le produit Aldes T.One à Home Assistant via le cloud. Vous devez disposer de la box AldesConnect, connectée à l'appareil, configurée et fonctionnelle dans l'application mobile AldesConnect.

## Table des matières

- [Installation](#installation)
- [Fonctionnalités](#fonctionnalités)
- [Configuration](#configuration)
- [Services](#services)
- [Stabilité et Robustesse](#stabilité-et-robustesse)
- [Expérience Utilisateur](#expérience-utilisateur)
- [Capteurs de diagnostic](#capteurs-de-diagnostic)
- [FAQ / Dépannage](#faq--dépannage)
- [Changelog](#changelog)
- [Avertissement Légal](#avertissement-légal)
- [Crédits](#crédits)

## Installation

Dans HACS, ajoutez le dépôt personnalisé :

```
https://github.com/tiagfernandes/homeassistant-aldes
```

Sélectionnez la catégorie **Intégration**, puis cliquez sur **Télécharger**.

Après installation, redémarrez Home Assistant et configurez l'intégration via **Paramètres → Appareils et services → Ajouter une intégration → Aldes**.

> **Mise à jour depuis v3.5.0** : L'intégration s'auto-enregistre et les nouvelles entités apparaissent automatiquement après redémarrage. Aucune action manuelle n'est requise.

## Fonctionnalités

| **Fonctionnalité** | **T.One® AIR** | **T.One® AquaAIR** |
|---|---|---|
| **Mode Air** (Éteint, Chauffage Comfort/Eco/Prog A/B, Rafraîchissement Comfort/Boost/Prog A/B) | ✔️ | ✔️ |
| **Mode Eau chaude** (Éteint, Allumé, Boost) | ❌ | ✔️ |
| **Connectivité** | ✔️ | ✔️ |
| **Température de la pièce principale** | ✔️ | ✔️ |
| **Quantité d'eau chaude disponible** | ❌ | ✔️ |
| **Capteur de température pour chaque pièce** | ✔️ | ✔️ |
| **Entité thermostat pour chaque pièce** | ✔️ | ✔️ |
| **Composition du foyer** | ❌ | ✔️ |
| **Cycle Antilegionelle** | ❌ | ✔️ |
| **Configuration des tarifs électriques** | ✔️ | ✔️ |
| **Mode vacances** | ✔️ | ✔️ |
| **Statistiques et coûts** | ✔️ | ✔️ |
| **Surveillance du filtre** | ✔️ | ✔️ |
| **Carte de planning** | ✔️ | ✔️ |
| **Carte de maintenance** | ✔️ | ✔️ |
| **État de santé API** | ✔️ | ✔️ |

## Configuration

### Carte Lovelace « Maintenance »

Une fois l'intégration installée, ajoutez une carte manuelle ou utilisez l'éditeur visuel (cliquez sur "Modifier" dans le coin droit de la carte).

**Fonctionnalités de l'éditeur :**
- Sélecteur d'entité avec liste déroulante des sensors disponibles
- Champ connectivité pour le statut live API
- Toggles pour afficher/masquer chaque section (Historique, Échecs, En attente)

```yaml
type: custom:aldes-maintenance-card
modem_entity: sensor.<device>_pending_commands
connectivity_entity: sensor.<device>_api_health
show_history_detail: true
show_failed_detail: true
show_pending_detail: true
```

### Carte de planning interactive

Pour utiliser la carte de planning avec grille éditable :

1. **Déclarer la ressource Lovelace** — Paramètres → Tableaux de bord → Ressources → Ajouter :
   ```yaml
   url: /aldes_planning_card.js
   type: module
   ```

2. **Ajouter la carte** avec auto-découverte ou entités explicites :
   ```yaml
   type: custom:aldes-planning-card
   ```

   Ou :
   ```yaml
   type: custom:aldes-planning-card
   entities:
     - sensor.aldes_XXXX_planning_heating_prog_a
     - sensor.aldes_XXXX_planning_heating_prog_b
     - sensor.aldes_XXXX_planning_cooling_prog_c
     - sensor.aldes_XXXX_planning_cooling_prog_d
   ```

3. **Fonctionnalités** : Sélecteur de programme (A/B/C/D), grille interactive (clic pour basculer Confort ↔ Eco ou Confort ↔ Off), envoi automatique via service, indicateur de chargement, légende des modes avec code couleur.

📖 [Documentation complète](custom_components/aldes/lovelace/LOVELACE_SETUP.md)

## Services

| Service | Description |
|---|---|
| `aldes.set_week_planning` | Envoie un programme hebdomadaire personnalisé à un appareil |

Le nom d'utilisateur et le mot de passe demandés lors de la configuration sont les mêmes que ceux de l'application mobile Aldes Connect.

## Stabilité et Robustesse

- **Authentification "Officielle"** : Utilisation des en-têtes (User-Agent, API Key) et de la signature de l'application Android officielle pour éviter les blocages de sécurité (WAF) et garantir la pérennité de l'accès.
- **Résilience Réseau** : Intégration d'un système de réessai automatique (Backoff exponentiel) qui gère les micro-coupures ou les lenteurs de l'API sans faire planter l'intégration.
- **File d'attente intelligente** : Les changements de température multiples sont traités séquentiellement via un worker dédié pour ne jamais surcharger l'API Aldes.
- **Sécurité des Logs** : Masquage automatique des mots de passe et données sensibles dans les journaux de débogage.
- **Timestamps doubles** : L'historique affiche `14:30:00→14:30:05 - action` (file d'attente → exécution/réel).

## Expérience Utilisateur

- **Zéro Latence (Optimistic State)** : L'interface réagit instantanément à vos commandes. Plus d'effet "flip-flop". L'intégration maintient l'état souhaité localement en attendant la confirmation du Cloud Aldes.
- **Persévérance (Auto-Retry)** : Si le Cloud Aldes ne prend pas en compte votre commande immédiatement, l'intégration le détecte automatiquement après 1 minute et renvoie la commande (jusqu'à 3 fois), tout en maintenant l'affichage correct.

## Capteurs de diagnostic

| Capteur | Rôle |
|---|---|
| `sensor.<device>_api_health` | État de connexion à l'API Aldes (`online`, `offline`, `degraded`, `retrying`) |
| `sensor.<device>_pending_commands` | File d'attente des commandes + historique succès/échecs |
| `sensor.<device>_system_alert` | État général du système |
| `sensor.<device>_device_info` | Détails techniques (référence, type, modem, filtres...) |
| `sensor.<device>_settings` | Paramètres (composition foyer, antilégionelle, tarifs) |
| `sensor.<device>_temperature_limits` | Limites min/max chauffage et clim |
| `sensor.<device>_thermostats_count` | Liste des thermostats avec leurs températures |

## FAQ / Dépannage

**Q : Les capteurs restent sur "unavailable" après installation.**
R : Vérifiez votre connexion internet et que l'application AldesConnect mobile fonctionne. Redémarrez Home Assistant.

**Q : La carte maintenance n'affiche aucune donnée.**
R : Assurez-vous que les entités `sensor.<device>_pending_commands` et `sensor.<device>_api_health` existent dans votre installation.

**Q : Les températures mettent du temps à se mettre à jour.**
R : L'intégration utilise une file d'attente et un système de persévérance. Les changements peuvent prendre jusqu'à 1 minute pour se propager.

**Q : Comment signaler un bug ou suggérer une amélioration ?**
R : Ouvrez une issue sur [GitHub](https://github.com/tiagfernandes/homeassistant-aldes/issues).

**Q : "Aucune pièce trouvée" / "Aucun thermostat trouvé" dans le test autonome.**
R : Exécutez `python debug_api_response.py` pour diagnostiquer, puis `python autofix_parse.py` pour corriger automatiquement. Consultez `QUICK_FIX.md` pour plus de détails.

## Changelog

Consultez [CHANGELOG.md](CHANGELOG.md) pour l'historique complet des modifications.

## Avertissement Légal

**Cette intégration n'est pas officielle et n'a aucun lien avec Aldes.** Elle est développée et maintenue par la communauté. Les créateurs et contributeurs de cette intégration ne sont pas responsables des dysfonctionnements, pertes de données, dommages matériels ou immatériels qui pourraient résulter de son utilisation. Utilisez-la à vos risques et périls.

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
