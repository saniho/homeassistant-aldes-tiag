# Guide de Déploiement et Testing

## ✅ Checklist de Testing

### 1. Vérification des Imports
- [ ] `python -m py_compile custom_components/aldes/api.py`
- [ ] `python -m py_compile custom_components/aldes/sensor.py`
- [ ] `python -m py_compile custom_components/aldes/diagnostics.py`

### 2. Home Assistant Integration
- [ ] Démarrer Home Assistant
- [ ] Aller dans Paramètres → Appareils & Services
- [ ] Vérifier la présence de l'intégration Aldes
- [ ] Cliquer sur le device Aldes

### 3. Nouveaux Capteurs Diagnostic
Vérifie que les 5 nouveaux capteurs sont créés:
- [ ] `sensor.aldes_XXXXX_api_health` → État: "connected" ou "disconnected"
- [ ] `sensor.aldes_XXXXX_device_info` → État: "TONE_AIR (T.One® AIR)"
- [ ] `sensor.aldes_XXXXX_thermostats_count` → État: nombre de thermostats
- [ ] `sensor.aldes_XXXXX_temperature_limits` → État: "H: 10°C-28°C, C: 20°C-32°C"
- [ ] `sensor.aldes_XXXXX_settings` → État: "configured"

### 4. Attributs des Capteurs
- [ ] **API Health**: Affiche cache_endpoints, queue_active, last_updated
- [ ] **Device Info**: Affiche reference, type, serial_number, modem, thermostats_count
- [ ] **Thermostats Count**: Liste tous les thermostats avec détails
- [ ] **Temperature Limits**: Affiche heat_min, heat_max, cool_min, cool_max
- [ ] **Settings**: Affiche household_composition, antilegio_cycle, tarifs

### 5. Page de Diagnostic
- [ ] Outils de développement → États → Chercher "aldes"
- [ ] Cliquer sur le device Aldes
- [ ] Options (⋮) → "Télécharger les diagnostiques"
- [ ] Vérifier que le JSON contient:
  - [ ] coordinator_status
  - [ ] device (reference, type, serial_number, etc.)
  - [ ] indicator (main_temperature, modes, limites)
  - [ ] thermostats (liste complète)
  - [ ] settings (tarifs, composition)
  - [ ] api (cache, token, queue)

### 6. Logs de Performance
- [ ] Configuration YAML:
  ```yaml
  logger:
    logs:
      custom_components.aldes.api: debug
  ```
- [ ] Relancer Home Assistant
- [ ] Vérifier les logs: `home-assistant.log`
- [ ] Chercher les patterns:
  - [ ] `API GET products completed with status 200 in XXX ms`
  - [ ] `API POST commands completed with status 200 in XXX ms`
  - [ ] `Stored data in emergency cache`

### 7. Tests d'Erreur
- [ ] Désactiver la connexion Internet
- [ ] Vérifier que l'état passe à "disconnected"
- [ ] Vérifier que les logs affichent: `Using cached data as fallback`
- [ ] Réactiver la connexion
- [ ] Vérifier que l'état repasse à "connected"

### 8. Performances
- [ ] Les requêtes API réussissent généralement en < 500ms
- [ ] Les logs de performance affichent temps réalistes
- [ ] Pas de lag UI en utilisant les nouveaux capteurs
- [ ] Cache fonctionne (visible en cas d'erreur API)

## 🔍 Exemples d'Utilisation

### Créer une Automatisation Basée sur l'État API

**YAML:**
```yaml
automation:
  - alias: "Alert API Aldes Down"
    trigger:
      platform: state
      entity_id: sensor.aldes_XXXXX_api_health
      to: "disconnected"
      for:
        minutes: 5
    action:
      - service: notify.telegram
        data:
          message: "🚨 API Aldes indisponible depuis 5 minutes!"
```

### Afficher les Informations Device

**Template pour Frontend:**
```jinja2
{{ state_attr('sensor.aldes_XXXXX_device_info', 'reference') }}
{{ state_attr('sensor.aldes_XXXXX_device_info', 'thermostats_count') }}
```

### Script pour Exporter Diagnostiques

**Python:**
```python
import json
import requests

# Récupérer l'entity_id du device Aldes
# Puis appeler le service diagnostic
# Les données sont disponibles en JSON

# Exemple via HASS API:
# GET http://homeassistant:8123/api/integration/aldes/diagnostics
```

### Dashboard Card Custom

**card-mod exemple:**
```yaml
type: entities
entities:
  - entity: sensor.aldes_XXXXX_api_health
    secondary_info: last-updated
  - entity: sensor.aldes_XXXXX_thermostats_count
    secondary_info: state-label
  - entity: sensor.aldes_XXXXX_temperature_limits
    secondary_info: attribute
    attribute: heat_min
```

## 🐛 Troubleshooting

### Les capteurs diagnostics n'apparaissent pas
1. Vérifier que les fichiers sont au bon endroit
2. Relancer Home Assistant complètement
3. Vérifier les logs pour erreurs d'import
4. Vérifier qu'il existe une config entry Aldes active

### Les logs de performance ne s'affichent pas
1. Vérifier le niveau DEBUG dans configuration.yaml
2. Faire une requête API (changer mode, température)
3. Relancer Home Assistant après changement de logging
4. Vérifier le fichier `home-assistant.log`

### JSON diagnostiques vide
1. Vérifier que le coordinator a des données
2. Vérifier que `coordinator.data` n'est pas None
3. Vérifier qu'une première sync API a réussi

### Erreur lors du téléchargement diagnostiques
1. Vérifier que `diagnostics.py` est présent
2. Vérifier pas d'erreurs Python au startup
3. Redémarrer Home Assistant
4. Vérifier les logs pour exceptions

## 📊 Métriques de Performance Attendues

| Métrique | Valeur Attendue | Seuil d'Alerte |
|----------|-----------------|---|
| Fetch Data | 100-300 ms | > 1000 ms |
| Change Mode | 150-400 ms | > 2000 ms |
| Set Temperature | 200-500 ms | > 2000 ms |
| Get Statistics | 300-800 ms | > 3000 ms |
| Cache Hit | < 10 ms | - |

## 🔐 Données Sensibles

**Masquées dans les logs:**
- ✅ Mots de passe
- ✅ Tokens d'authentification
- ✅ Détails de la requête auth

**Exposées en diagnostiques (JSON):**
- ⚠️ Numéro de série device
- ⚠️ ID modem
- ⚠️ Noms de thermostats
- ⚠️ Tarifs d'électricité
- ⚠️ Configuration household

**Recommandation:** Ne pas partager les diagnostiques publiquement si vous voulез masquer ces infos.

## 🚀 Déploiement

### En Développement
```bash
cd /config/custom_components/aldes
python -m py_compile *.py
# Redémarrer Home Assistant
```

### En Production (HACS)
1. L'utilisateur clone depuis GitHub
2. HACS détecte les nouveaux fichiers
3. Installation automatique après redémarrage

### Rollback (Si besoin)
```bash
# Supprimer les fichiers ajoutés:
rm custom_components/aldes/diagnostics.py

# Restaurer la version précédente de sensor.py et api.py
git checkout api.py sensor.py

# Redémarrer
```

## 📝 Logs Attendus au Startup

```
INFO (MainThread) [homeassistant.loader] loading custom_components.aldes
DEBUG (MainThread) [custom_components.aldes] Setting up aldes
INFO (MainThread) [custom_components.aldes.coordinator] Fetching data from Aldes API...
DEBUG (MainThread) [custom_components.aldes.api] API GET products completed with status 200 in 234.56 ms
DEBUG (MainThread) [custom_components.aldes.sensor] DataApiEntity initialized - Device: TONE_AIR...
INFO (MainThread) [homeassistant.setup] Setup of domain aldes took X seconds
```

## ✨ Bonnes Pratiques

1. **Activer DEBUG seulement si nécessaire** - Impact sur performance
2. **Nettoyer les anciens caches** si nombreuses erreurs
3. **Exporter diagnostiques régulièrement** pour comparaison
4. **Monitorer les logs** pour patterns d'erreurs
5. **Alerter sur API Health** pour notifier en cas de problème

## 📞 Support

Si problème:
1. Récupérer les diagnostiques via HASS UI
2. Activer DEBUG logging
3. Reproduire l'erreur
4. Partager les diagnostiques JSON + logs
5. Ouvrir une issue sur GitHub
