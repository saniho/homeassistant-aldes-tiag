# Implémentation Diagnostics & Logging v3.4.0

## 📦 Contenu

Cette version ajoute une couche complète de diagnostics et logging amélioré à l'intégration Aldes.

### Fichiers Modifiés
- ✅ `custom_components/aldes/api.py` - Logging de performance et méthode diagnostic
- ✅ `custom_components/aldes/sensor.py` - 5 nouveaux capteurs diagnostic

### Fichiers Créés
- ✨ `custom_components/aldes/diagnostics.py` - Intégration Home Assistant Diagnostics
- 📚 `DIAGNOSTICS.md` - Documentation complète
- 📊 `IMPLEMENTATION_SUMMARY.md` - Résumé technique
- 🧪 `TESTING_GUIDE.md` - Guide de test et troubleshooting
- 🏗️ `ARCHITECTURE_DIAGNOSTICS.md` - Vue d'ensemble architecturale

## 🚀 Démarrage Rapide

### Installation
1. Mettez à jour via HACS ou clonez la branche
2. Redémarrez Home Assistant
3. Les nouveaux capteurs sont créés automatiquement

### Utilisation des Diagnostiques

**Via l'Interface:**
```
Paramètres → Appareils & Services → Aldes → [Sélectionner le device] 
→ Options (⋮) → Télécharger les diagnostiques
```

**Via Ligne de Commande:**
```bash
# Voir les nouveaux capteurs
curl http://homeassistant:8123/api/states | grep "sensor.aldes.*diagnostic"
```

### Activation du Logging de Performance

**configuration.yaml:**
```yaml
logger:
  logs:
    custom_components.aldes.api: debug
```

**Output Attendu:**
```
DEBUG (MainThread) [custom_components.aldes.api] API GET products completed with status 200 in 145.32 ms
```

## 📊 Nouveaux Capteurs Diagnostic

| Capteur | État | Utilité |
|---------|------|---------|
| `sensor.aldes_*_api_health` | "connected" / "disconnected" | Monitorer santé API |
| `sensor.aldes_*_device_info` | "TONE_AIR (T.One® AIR)" | Info device (caché) |
| `sensor.aldes_*_thermostats_count` | 3 | Nombre thermostats (caché) |
| `sensor.aldes_*_temperature_limits` | "H: 10°C-28°C, C: 20°C-32°C" | Limites température (caché) |
| `sensor.aldes_*_settings` | "configured" | Paramètres (caché) |

**(*) = serial_number de votre device**

Les capteurs "caché" sont des entités DIAGNOSTIC non visibles par défaut, mais tous leurs attributs sont accessibles via les templates.

## 🔍 Diagnostics Exportables

Le JSON exportable contient:
- Statut de la connexion
- Infos device (référence, type, modem)
- État de tous les thermostats
- Limites de température
- Tarifs d'électricité configurés
- État du cache API
- Infos de token
- État de la queue de traitement

**⚠️ Note de Sécurité:** Ce JSON contient des données sensibles (numéro de série, tarifs). Ne le partagez qu'avec du support de confiance.

## 📈 Métriques de Performance

Chaque requête API est maintenant loggée avec:
- Durée totale (ms)
- Statut HTTP
- Endpoint appelé
- Timestamp

Permet d'identifier:
- ✅ Requêtes lentes
- ✅ Patterns d'erreur
- ✅ Tendance de la qualité du service

## 🛠️ Améliorations pour Développeurs

### Nouvelle API Interne

```python
# Dans AldesApi
api.get_diagnostic_info() -> dict[str, Any]
# Retourne: {
#   'api_url_base': '...',
#   'cache': {...},
#   'token': {...},
#   'queue_active': bool
# }
```

### Logging Structuré

```python
# Les requêtes API logguent automatiquement:
# - Durée
# - Statut
# - Endpoint
# Sans exposition de données sensibles
```

## ✅ Validation

Tous les fichiers ont été:
- ✅ Vérifiés syntaxe Python
- ✅ Validés AST
- ✅ Testés imports
- ✅ Revérifiés pas de breaking changes

## 🔄 Backward Compatibility

**100% compatible:**
- ✅ Aucune modification des entités existantes
- ✅ API client reste compatible
- ✅ Coordinator inchangé
- ✅ Les nouveaux capteurs sont **ajout pur**

Les utilisateurs existants n'ont rien à changer.

## 📚 Documentation

Pour plus d'informations, consultez:

1. **[DIAGNOSTICS.md](DIAGNOSTICS.md)** - Guide complet des diagnostics
2. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Résumé technique
3. **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Guide de test
4. **[ARCHITECTURE_DIAGNOSTICS.md](ARCHITECTURE_DIAGNOSTICS.md)** - Architecture

## 🐛 Troubleshooting

### Les capteurs diagnostics n'apparaissent pas?
→ Vérifier que `diagnostics.py` existe dans le dossier aldes

### Les logs de performance ne s'affichent pas?
→ Vérifier le niveau DEBUG dans configuration.yaml

### Erreur lors du téléchargement des diagnostiques?
→ Vérifier que coordinator.data n'est pas None (première sync complète)

Voir **[TESTING_GUIDE.md](TESTING_GUIDE.md)** pour plus de détails.

## 🎯 Cas d'Utilisation

### Utilisateur Final
- **Problème d'API:** Télécharger diagnostiques pour support
- **Monitoring:** Utiliser AldesApiHealthSensor pour alertes
- **Debug:** Activer logs DEBUG pour voir requêtes

### Développeur
- **Performance:** Analyser logs pour identifier bottlenecks
- **Bug:** Examiner diagnostiques pour patterns d'erreur
- **Évolution:** Ajouter nouvelles metrics basées sur la structure existante

## 🚀 Prochaines Étapes Possibles

- [ ] Dashboard de monitoring intégré
- [ ] Alertes automatiques sur API down
- [ ] Historisation des métriques de performance
- [ ] Export/Import configuration
- [ ] Interface visuelle pour diagnostics

## 📝 Notes

- Les diagnostiques stockent temporairement le numéro de série et infos device
- Les logs DEBUG ne s'affichent que si configuré explicitement
- Les capteurs diagnostic ne créent pas de surcharge (simples lectures)
- Le cache fonctionne même en cas d'erreur réseau

## 🤝 Support

Pour des questions ou problèmes:
1. Vérifier les logs (niveau DEBUG)
2. Télécharger et examiner les diagnostiques
3. Ouvrir une issue sur GitHub avec les informations collectées

---

**Version:** 3.4.0  
**Date:** 2026-01-24  
**Status:** ✅ Implémenté et Testé
