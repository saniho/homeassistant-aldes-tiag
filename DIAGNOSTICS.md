# Diagnostics et Logging - Documentation

## Améliorations Implémentées

### 1. Amélioration du Logging dans l'API (`api.py`)

#### Nouvelles Fonctionnalités :

**Logging de Performance**
- Nouvelle méthode `_log_api_performance()` qui enregistre:
  - Durée de chaque requête API (en millisecondes)
  - Statut HTTP reçu
  - Endpoint appelé
  - Méthode HTTP (GET, POST, PATCH)

- Les logs sont enregistrés au niveau DEBUG pour ne pas surcharger les logs normaux
- Format: `API GET products completed with status 200 in 123.45 ms`

**Amélioration des Logs d'Erreur**
- Les messages d'erreur incluent maintenant:
  - Type d'erreur précis (ClientError, TimeoutError, KeyError, ValueError)
  - Durée écoulée avant l'erreur
  - Âge du cache en cas d'utilisation du fallback

**Diagnostic API Amélioré**
- Nouvelle méthode `get_diagnostic_info()` qui retourne:
  - État du cache (nombre d'endpoints, âge de chaque entrée)
  - Informations du token (présence, longueur, date d'expiration)
  - État de la queue de température
  - URL de base de l'API

### 2. Nouveaux Capteurs de Diagnostic (`sensor.py`)

#### AldesApiHealthSensor
- **Unique ID**: `{serial_number}_api_health`
- **État**: `connected` ou `disconnected`
- **Catégorie**: DIAGNOSTIC
- **Attributs**:
  - `cache_endpoints`: Nombre d'endpoints en cache
  - `queue_active`: État de la queue de traitement
  - `last_updated`: Heure dernière mise à jour

#### AldesDeviceInfoSensor
- **Unique ID**: `{serial_number}_device_info`
- **État**: Référence et type du device (ex: "TONE_AIR (T.One® AIR)")
- **Catégorie**: DIAGNOSTIC (non visible par défaut)
- **Attributs**:
  - `reference`: Modèle du device
  - `type`: Type de device
  - `serial_number`: Numéro de série
  - `modem`: ID du modem
  - `is_connected`: Statut de connexion
  - `thermostats_count`: Nombre de thermostats
  - `has_filter`: Présence de filtre
  - `filter_wear`: État d'usure du filtre

#### AldesThermostatsCountSensor
- **Unique ID**: `{serial_number}_thermostats_count`
- **État**: Nombre de thermostats (entier)
- **Catégorie**: DIAGNOSTIC (non visible par défaut)
- **Attributs**: Liste détaillée de chaque thermostat avec:
  - `id`, `name`, `number`
  - `current_temperature`
  - `temperature_set`

#### AldesTemperatureLimitsSensor
- **Unique ID**: `{serial_number}_temperature_limits`
- **État**: Résumé des limites (ex: "H: 10°C-28°C, C: 20°C-32°C")
- **Catégorie**: DIAGNOSTIC (non visible par défaut)
- **Attributs**:
  - `heat_min`, `heat_max`: Limites chauffage
  - `cool_min`, `cool_max`: Limites climatisation
  - `main_temperature`: Température principale actuelle

#### AldesSettingsSensor
- **Unique ID**: `{serial_number}_settings`
- **État**: `configured` ou `unconfigured`
- **Catégorie**: DIAGNOSTIC (non visible par défaut)
- **Attributs**:
  - `household_composition`: Composition du foyer
  - `antilegio_cycle`: Jour du cycle anti-légionelle
  - `kwh_creuse`: Prix kWh heures creuses
  - `kwh_pleine`: Prix kWh heures pleines

### 3. Page de Diagnostic Home Assistant (`diagnostics.py`)

Permet d'accéder à des diagnostics complets via l'interface Home Assistant:
**Chemins**: Paramètres → Appareils et Services → Aldes → [Sélectionner] → Options (trois points) → Télécharger les diagnostiques

#### Structure des Diagnostiques:

```json
{
  "coordinator_status": "ok",
  "last_update": true,
  "update_interval": "0:01:00",
  "device": {
    "reference": "TONE_AIR",
    "type": "T.One® AIR",
    "serial_number": "...",
    "is_connected": true,
    "filter_wear": false,
    ...
  },
  "indicator": {
    "main_temperature": 21.5,
    "current_air_mode": "AirMode.HEAT_COMFORT",
    "temperature_limits": {
      "heating_min": 10,
      "heating_max": 28,
      "cooling_min": 20,
      "cooling_max": 32
    },
    "holidays": {
      "start_date": null,
      "end_date": null,
      "frost_protection_enabled": false
    }
  },
  "thermostats": [
    {
      "id": 1,
      "name": "Salon",
      "current_temperature": 21.5,
      "temperature_set": 21
    }
  ],
  "api": {
    "cache": {
      "cached_endpoints": 3,
      "cache_details": [...]
    },
    "token": {
      "token_present": true,
      "token_expires": "2026-01-25T10:30:00+00:00"
    }
  }
}
```

## Utilisation des Diagnostiques

### Pour les utilisateurs
1. Allez dans **Paramètres → Appareils et Services**
2. Sélectionnez l'intégration **Aldes**
3. Cliquez sur le périphérique
4. Cliquez sur le menu (trois points) → **Télécharger les diagnostiques**
5. Envoyez ce fichier JSON au support en cas de problème

### Pour les développeurs
- Vérifier les logs:
  ```bash
  tail -f ~/.homeassistant/logs/home-assistant.log | grep "aldes"
  ```
- Utiliser le développeur HASS pour lire les entités:
  ```
  Outils de développement → États → Chercher "aldes"
  ```

## Logs de Performance

Les logs de performance sont disponibles en mode DEBUG. Pour activer:

**configuration.yaml**:
```yaml
logger:
  logs:
    custom_components.aldes.api: debug
    custom_components.aldes: debug
```

### Exemple de sortie
```
DEBUG (MainThread) [custom_components.aldes.api] API GET products completed with status 200 in 145.32 ms
DEBUG (MainThread) [custom_components.aldes.api] Stored data in emergency cache for get:https://...
DEBUG (MainThread) [custom_components.aldes.api] API POST commands completed with status 200 in 234.12 ms
```

## Troubleshooting

### Diagnostic Utiles:
1. **Cache vide**: Problème de connectivité API → Vérifier l'authentification
2. **Token expiré**: Visible dans `token_expires` → Redémarrer l'intégration
3. **Nombres de thermostats incorrect**: Vérifier si le device est bien synchronisé
4. **Limites de température manquantes**: Device ne retourne pas ces données

## Évolution Future

- [ ] Ajouter des métriques Prometheus pour monitoring avancé
- [ ] Historiser les logs de performance pour analyse de tendance
- [ ] Créer une page de debug visuelle dans l'interface HASS
