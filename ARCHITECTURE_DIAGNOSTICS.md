# Diagramme d'Architecture - Diagnostics & Logging

## 📐 Vue d'Ensemble de l'Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Home Assistant                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         Intégration Aldes                           │  │
│  │                                                     │  │
│  │  ┌─────────────────┐      ┌──────────────────────┐ │  │
│  │  │   Coordinator   │──────│   AldesApi Client    │ │  │
│  │  │                 │      │                      │ │  │
│  │  │ Update Interval │      │ • authenticate()     │ │  │
│  │  │ = 1 minute      │      │ • fetch_data()       │ │  │
│  │  │                 │      │ • change_mode()      │ │  │
│  │  │ Data:           │      │ • set_temperature()  │ │  │
│  │  │ • DataApiEntity │      │ • get_statistics()   │ │  │
│  │  │ • last_update   │      │ • get_diagnostic_    │ │  │
│  │  │ • status        │      │   info() ✨ NEW      │ │  │
│  │  └──────┬──────────┘      └──────────┬───────────┘ │  │
│  │         │                            │              │  │
│  │    Calls every                    Metrics:          │  │
│  │    60 seconds                    • Performance      │  │
│  │                                  • Cache State      │  │
│  │                                  • Token Info       │  │
│  │                                  • Queue Status     │  │
│  │                                                     │  │
│  └──────────────┬────────────────────────────────────┘  │
│                 │                                        │
│  ┌──────────────▼────────────────────────────────────┐  │
│  │         Sensor Platform                          │  │
│  │                                                   │  │
│  │  Existing:                                        │  │
│  │  • AldesThermostatSensorEntity                   │  │
│  │  • AldesMainRoomTemperatureEntity                │  │
│  │  • AldesWaterEntity (AquaAir only)               │  │
│  │  • AldesPlanningEntity (x4)                      │  │
│  │  • AldesFilterDateSensorEntity                   │  │
│  │  • BaseStatisticsSensor (x6)                     │  │
│  │  • AldesHolidaysStartSensor                      │  │
│  │  • AldesHolidaysEndSensor                        │  │
│  │  • AldesHorsGelSensor                            │  │
│  │                                                   │  │
│  │  ✨ NEW DIAGNOSTIC SENSORS:                       │  │
│  │  • AldesApiHealthSensor ◄────────────┐           │  │
│  │  • AldesDeviceInfoSensor              │           │  │
│  │  • AldesThermostatsCountSensor        │           │  │
│  │  • AldesTemperatureLimitsSensor       │           │  │
│  │  • AldesSettingsSensor                │           │  │
│  │                                        │           │  │
│  │  All query: coordinator.data &        │           │  │
│  │  api.get_diagnostic_info() ◄──────────┘           │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Diagnostics Module ✨ NEW                        │  │
│  │                                                   │  │
│  │  async_get_config_entry_diagnostics()            │  │
│  │  • Aggregates all data                           │  │
│  │  • Called via Aldes device → Options → Download  │  │
│  │  • Exports comprehensive JSON                    │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │  Aldes Cloud    │
                  │  API v5         │
                  └─────────────────┘
```

## 🔄 Flux de Données - Diagnostics

```
┌──────────────────┐
│  User clicks     │
│  "Download       │
│  Diagnostics"    │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────┐
│ async_get_config_entry_diagnostics │
│  (diagnostics.py)                  │
└──────────────────┬─────────────────┘
         │
         │ Gathers from:
         │
         ├─ coordinator.data (DataApiEntity)
         ├─ coordinator.api.get_diagnostic_info()
         └─ coordinator properties
         │
         ▼
┌────────────────────────────────────┐
│  JSON Structure:                   │
│  • coordinator_status              │
│  • device info                     │
│  • indicator data                  │
│  • thermostats                     │
│  • settings                        │
│  • plannings                       │
│  • api diagnostic info             │
└──────────────────┬─────────────────┘
         │
         ▼
   User downloads JSON file
   (Sent via browser)
```

## 📊 Flux de Performance Logging

```
API Request Made
       │
       ├─ Start Time: datetime.now(UTC)
       │
       ▼
_api_request() called
       │
       ├─ Execute request via aiohttp
       │
       ▼
Response Received
       │
       ├─ Duration = datetime.now(UTC) - start_time
       ├─ Duration in ms = duration.total_seconds() * 1000
       │
       ▼
_log_api_performance()
       │
       ├─ DEBUG: "API GET products completed with status 200 in 145.32 ms"
       │
       ▼
Cache Updated
       │
       └─ Stored in self._cache for fallback
```

## 🏗️ Structure des Données Diagnostic

```
api.get_diagnostic_info()
│
├─ api_url_base: str
│
├─ cache: dict
│  ├─ cached_endpoints: int
│  └─ cache_details: list[dict]
│     ├─ key: str
│     └─ age_seconds: float
│
├─ token: dict
│  ├─ token_present: bool
│  ├─ token_length: int
│  ├─ token_expires: str (ISO8601)
│  ├─ token_issued_at: str (ISO8601)
│  └─ token_decode_error: str (if error)
│
└─ queue_active: bool
```

## 🔍 Entity Diagnostic Information

```
AldesApiHealthSensor
├─ state: "connected" | "disconnected"
└─ attributes:
   ├─ cache_endpoints: int
   ├─ queue_active: bool
   └─ last_updated: ISO8601

AldesDeviceInfoSensor
├─ state: "TONE_AIR (T.One® AIR)"
└─ attributes:
   ├─ reference: str
   ├─ type: str
   ├─ serial_number: str
   ├─ modem: str
   ├─ is_connected: bool
   ├─ thermostats_count: int
   ├─ has_filter: bool
   └─ filter_wear: bool

AldesThermostatsCountSensor
├─ state: int (number of thermostats)
└─ attributes:
   └─ thermostats: list[dict]
      ├─ id: int
      ├─ name: str
      ├─ number: int
      ├─ current_temperature: float
      └─ temperature_set: int

AldesTemperatureLimitsSensor
├─ state: "H: 10°C-28°C, C: 20°C-32°C"
└─ attributes:
   ├─ heat_min: int
   ├─ heat_max: int
   ├─ cool_min: int
   ├─ cool_max: int
   └─ main_temperature: float

AldesSettingsSensor
├─ state: "configured" | "unconfigured"
└─ attributes:
   ├─ household_composition: str | None
   ├─ antilegio_cycle: int
   ├─ kwh_creuse: float
   └─ kwh_pleine: float
```

## 🔐 Logging Flow with Error Handling

```
API Request
│
├─ Normal Response
│  ├─ Status 200
│  ├─ Parse JSON
│  ├─ Store in cache
│  └─ _log_api_performance() ✅
│
├─ HTTP Error
│  ├─ Status != 200
│  ├─ Log error with status & duration
│  └─ Try to use cache ⚠️
│
└─ Network Error
   ├─ ClientError | TimeoutError
   ├─ Log exception with type
   ├─ Calculate duration
   ├─ Try to use cache ⚠️
   └─ "Using cached data as fallback due to error: TimeoutError (age: 0:02:30)"
```

## 📈 Métriques Collectées

```
Pour chaque requête API:
├─ Timestamp démarrage (UTC)
├─ Méthode HTTP (GET, POST, PATCH)
├─ URL endpoint
├─ Statut HTTP reçu
├─ Durée totale (ms)
├─ Raison d'erreur (si applicable)
├─ Cache utilisé (fallback) (si applicable)
└─ Age du cache (si utilisé)
```

## 🎯 Cas d'Usage des Diagnostics

```
UTILISATEUR FINAL
│
├─ Problème: "API semble lente"
│  └─ Solution: Télécharger diagnostiques
│     └─ Voir: cache_endpoints, token_expires
│     └─ Voir: logs avec timestamps
│
├─ Problème: "Thermostat ne répond pas"
│  └─ Solution: Télécharger diagnostiques
│     └─ Voir: thermostats list
│     └─ Voir: api health
│     └─ Voir: is_connected status
│
└─ Problème: "Tarifs incorrects"
   └─ Solution: Télécharger diagnostiques
      └─ Voir: kwh_creuse / kwh_pleine
      └─ Voir: settings status

DÉVELOPPEUR
│
├─ Amélioration: Performance
│  └─ Analyser: Logs de durée API
│  └─ Identifier: Bottlenecks
│
├─ Bug: Cache ne fonctionne pas
│  └─ Analyser: Cache details
│  └─ Voir: Age du cache, hit rate
│
└─ Feature: Monitoring
   └─ Ajouter: Alertes sur api health
   └─ Tracker: Disponibilité API
```

## 🚀 Intégration avec Home Assistant

```
Standard Home Assistant Diagnostic API:
├─ Chaque intégration peut exposer diagnostics()
├─ Appelée via UI: Device → Options → Download
├─ Retourne dict[str, Any]
├─ Home Assistant serialise en JSON
├─ Utilisateur peut télécharger et partager
└─ Support peut analyser pour troubleshooting
```

## 🔄 Cycle de Mise à Jour

```
Home Assistant Startup
│
├─ Load all integrations
│  └─ Load aldes integration
│     └─ Import diagnostics module ✅
│
├─ Run setup_entry()
│  └─ Créer AldesApi instance
│     └─ _diagnostic_info initialized to {}
│
├─ Run async_setup_entry() (sensors)
│  └─ Créer tous les capteurs
│     ├─ Capteurs existants (12)
│     └─ 5 nouveaux capteurs diagnostic ✅
│
├─ Coordinator starts update loop
│  └─ Every 60 seconds:
│     └─ fetch_data() from API
│        └─ _log_api_performance() ✅
│        └─ _diagnostic_info updated
│
└─ Sensors update from coordinator
   └─ Display latest data
   └─ Display diagnostic attributes
```

## 📝 Événements de Logging

```
[STARTUP]
DEBUG: Loading custom_components.aldes.diagnostics ✅

[EVERY REQUEST]
DEBUG: API GET products completed with status 200 in X ms ✅

[ON ERROR]
ERROR: API request failed with status 401 ✅
WARNING: Using cached data as fallback due to error: TimeoutError ✅

[PERFORMANCE]
DEBUG: API POST commands completed with status 200 in 234 ms ✅

[CACHE HIT]
DEBUG: Stored data in emergency cache for get:...api... ✅
```

## 🎓 Exemple Complet: Utilisateur Rapporte Bug

```
Étape 1: Utilisateur déclare "API freeze depuis 5 min"
├─ Vous: "Télécharge diagnostiques via UI"
│
Étape 2: Utilisateur envoie JSON
├─ coordinator_status: "ok"
├─ last_update: true
├─ device.is_connected: true
├─ api.cache.cached_endpoints: 0 ⚠️  (Aucun cache!)
└─ token.token_expires: "2026-01-24T10:30:00Z" (Expiré dans 1h ✅)

Étape 3: Vous analysez
├─ Cache vide → API requests failing?
├─ Activer DEBUG logging
├─ Voir logs: "Using cached data as fallback"
├─ Diagnostiquer: Problème réseau intermittent

Étape 4: Solution
└─ Redémarrer Home Assistant
   └─ Relancer intégration Aldes
      └─ Revérifier diagnostiques
         └─ Cache rempli ✅
            └─ Issue résolu ✅
```
