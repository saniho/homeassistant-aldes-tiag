# Changelog

## Évolutions v3.5 → v3.8

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

Nouvelle carte custom auto-enregistrée avec éditeur visuel complet. Affiche la file d'attente des commandes, l'état de connexion API, et les détails configurables.

**Fonctionnalités de l'éditeur :**
- Sélecteur d'entité avec liste déroulante des sensors disponibles
- Champ connectivité pour le statut live API
- Toggles pour afficher/masquer chaque section :
  - **Historique** : dernières commandes exécutées
  - **Échecs** : commandes en échec
  - **En attente** : commandes dans la file

```yaml
type: custom:aldes-maintenance-card
modem_entity: sensor.<device>_pending_commands
connectivity_entity: sensor.<device>_api_health
show_history_detail: true
show_failed_detail: true
show_pending_detail: true
```

### Éditeur visuel Carte Planning

Nouvel éditeur pour la carte planning avec découverte automatique des entités et sélection manuelle par cases à cocher.

### Corrections v3.8.1

- **Planning entity** : ne retourne plus `unknown` quand la liste de planning est vide (affiche `"0 items"`)
- **Attributs planning** : `planning_data` toujours présent même quand vide → la carte planning détecte correctement l'entité
- **API Health** : correction de `_temperature_task` → `_worker_task` dans `get_diagnostic_info()`

### Auto-enregistrement Lovelace

Les ressources JS des cartes sont automatiquement déclarées dans Lovelace à l'installation.

### Fiabilité et robustesse

- **Timestamps doubles** : l'historique affiche `14:30:00→14:30:05 - action` (file d'attente → exécution/réel)
- **Capteur API Health** retravaillé pour ne plus rester bloqué en `unavailable` après une erreur réseau passagère
- **Attribut `integration_version`** sur tous les capteurs
- **Éditeur visuel** maintenance avec sélecteurs d'entités et toggles
- **Champ connectivité** dans la carte : statut live via `sensor.<device>_api_health`

## v3.5.0

- Amélioration du système Retry/Perseverance
- Corrections diverses
