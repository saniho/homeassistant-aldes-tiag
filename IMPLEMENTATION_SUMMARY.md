# Résumé des Changements - Diagnostics & Logging

## 📋 Vue d'ensemble
Implémentation complète des améliorations de diagnostics et logging pour l'intégration Aldes.

## 🔧 Fichiers Modifiés

### 1. `custom_components/aldes/api.py`
**Changements:**
- ✅ Ajout de la méthode `_log_api_performance()` pour tracer la durée des requêtes API
- ✅ Enrichissement de `_api_request()` avec timestamps et metrics de performance
- ✅ Ajout de la méthode `get_diagnostic_info()` exposant l'état complet du client API
- ✅ Logging amélioré des erreurs avec contexte (durée, type d'erreur, fallback utilisé)

**Nouvelles Fonctionnalités:**
```python
# Logging de performance pour chaque requête
API GET products completed with status 200 in 123.45 ms

# Infos de diagnostic exposées
api.get_diagnostic_info() -> {
    'api_url_base': '...',
    'cache': {'cached_endpoints': 3, 'cache_details': [...]},
    'token': {'token_present': True, 'token_expires': '...', ...},
    'queue_active': True
}
```

### 2. `custom_components/aldes/sensor.py`
**Nouveaux Capteurs Diagnostic (5 entités):**

| Capteur | Unique ID | État | Attributs |
|---------|-----------|------|-----------|
| **AldesApiHealthSensor** | `{serial}_api_health` | "connected" / "disconnected" | cache_endpoints, queue_active, last_updated |
| **AldesDeviceInfoSensor** | `{serial}_device_info` | "TONE_AIR (T.One® AIR)" | reference, type, serial_number, modem, thermostats_count, has_filter, filter_wear |
| **AldesThermostatsCountSensor** | `{serial}_thermostats_count` | 3 | thermostats: [id, name, number, current_temp, temp_set, ...] |
| **AldesTemperatureLimitsSensor** | `{serial}_temperature_limits` | "H: 10°C-28°C, C: 20°C-32°C" | heat_min, heat_max, cool_min, cool_max, main_temperature |
| **AldesSettingsSensor** | `{serial}_settings` | "configured" / "unconfigured" | household_composition, antilegio_cycle, kwh_creuse, kwh_pleine |

**Catégories:**
- Tous les capteurs sont en catégorie `DIAGNOSTIC`
- 4 sur 5 ne sont pas visibles par défaut (non sensibles pour l'utilisateur final)
- AldesApiHealthSensor reste visible pour une vue rapide de la santé API

### 3. `custom_components/aldes/diagnostics.py` (NOUVEAU)
**Création d'un nouveau fichier pour Home Assistant Diagnostics.**

**Fonctionnalité:**
- Fonction `async_get_config_entry_diagnostics()` appelée via l'interface HA
- Agrège TOUTES les données disponibles de l'intégration
- Exportable en JSON pour partage avec support

**Accès:** Paramètres → Appareils & Services → Aldes → [Appareil] → Options (⋮) → Télécharger les diagnostiques

**Contenu exporté:**
```
- Statut du coordinator (last_update, update_interval)
- Infos device (référence, type, serial, modem, connectivité)
- État de l'indicateur (température, modes, limites, vacances)
- Liste complète des thermostats avec paramètres
- Paramètres utilisateur (composition, anti-légionelle, tarifs)
- Plannings (nombre d'éléments par programme)
- Infos API (cache, token, queue)
```

## 📊 Structure des Données Exposées

### Capteur API Health
```python
State: "connected"
Attributes:
  cache_endpoints: 3
  queue_active: true
  last_updated: "2026-01-24T10:30:00Z"
```

### Capteur Device Info
```python
State: "TONE_AIR (T.One® AIR)"
Attributes:
  reference: "TONE_AIR"
  type: "T.One® AIR"
  serial_number: "XX1A2B3C"
  modem: "MOD123456"
  is_connected: true
  thermostats_count: 3
  has_filter: true
  filter_wear: false
```

### Capteur Thermostats Count
```python
State: 3
Attributes:
  thermostats:
    - {id: 1, name: "Salon", number: 1, current_temperature: 21.5, temperature_set: 21}
    - {id: 2, name: "Chambre", number: 2, current_temperature: 20.0, temperature_set: 20}
    - {id: 3, name: "Bureau", number: 3, current_temperature: 22.0, temperature_set: 22}
```

### Capteur Temperature Limits
```python
State: "H: 10°C-28°C, C: 20°C-32°C"
Attributes:
  heat_min: 10
  heat_max: 28
  cool_min: 20
  cool_max: 32
  main_temperature: 21.5
```

### Capteur Settings
```python
State: "configured"
Attributes:
  household_composition: "FOUR"
  antilegio_cycle: 1
  kwh_creuse: 0.150
  kwh_pleine: 0.200
```

## 🔍 Améliorations de Logging

### Avant
```
ERROR (MainThread) [custom_components.aldes.api] Failed to fetch data
ERROR (MainThread) [custom_components.aldes.api] API request failed with status 401
```

### Après
```
DEBUG (MainThread) [custom_components.aldes.api] API GET products completed with status 200 in 145.32 ms
DEBUG (MainThread) [custom_components.aldes.api] API POST commands completed with status 200 in 234.12 ms
ERROR (MainThread) [custom_components.aldes.api] API request failed with status 401 in 50.15 ms
WARNING (MainThread) [custom_components.aldes.api] Using cached data as fallback due to error: TimeoutError (age: 0:02:30)
```

## 📈 Métriques Exposées

**Cache API:**
- Nombre d'endpoints en cache
- Âge de chaque entrée en cache
- Utilisation du fallback en cas d'erreur

**Token:**
- Présence du token
- Longueur du token
- Date d'expiration du token
- Date d'émission du token

**Queue:**
- État de la queue de traitement des températures
- Nombre de requêtes en attente (via monitoring logs)

**Performance:**
- Durée de chaque requête API (ms)
- Statut HTTP reçu
- Endpoint appelé
- Méthode HTTP utilisée

## 🎯 Cas d'Usage

### Pour les Utilisateurs
1. **Troubleshooting**: Télécharger les diagnostiques pour support
2. **Monitoring**: Vérifier l'état API via AldesApiHealthSensor
3. **Configurateur**: Visualiser les limites de température disponibles

### Pour les Développeurs
1. **Debug**: Activer logs DEBUG pour voir performance en temps réel
2. **Analyse**: Consulter les diagnostiques exportés pour pattern d'erreurs
3. **Performance**: Identifier les requêtes lentes via logs de performance

## 🚀 Activation

**Les nouveaux capteurs sont automatiquement créés lors du setup.**

Pour voir les diagnostiques:
```yaml
# configuration.yaml - OPTIONNEL (logs sont silencieux par défaut)
logger:
  logs:
    custom_components.aldes.api: debug
    custom_components.aldes: debug
```

## ✅ Testing

Tous les fichiers ont été validés:
- ✅ Syntaxe Python vérifiée (`py_compile`, `ast`)
- ✅ Imports vérifiés
- ✅ Structure JSON diagnostics correcte
- ✅ Pas de références cassées

## 📝 Documentation

Voir `DIAGNOSTICS.md` pour la documentation complète:
- Guide d'utilisation des diagnostiques
- Interprétation des logs
- Troubleshooting
- Évolutions futures

## 🔄 Pas de Breaking Changes

- ✅ Entités existantes inchangées
- ✅ Coordinateur inchangé
- ✅ API client backward compatible
- ✅ Nouveaux capteurs = ajout uniquement
