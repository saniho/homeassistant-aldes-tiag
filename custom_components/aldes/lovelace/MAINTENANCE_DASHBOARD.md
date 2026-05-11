# Aldes Maintenance Dashboard

Ce tableau de bord affiche l'état de santé complet de ton installation Aldes.

```yaml
type: vertical-stack
cards:
  - type: entity
    entity: sensor.aldes_d427870faaea_api_health
    name: État de Santé API
  - type: entity
    entity: sensor.aldes_d427870faaea_pending_commands
    name: Requêtes en Attente
  - type: entities
    title: Maintenance
    entities:
      - entity: binary_sensor.aldes_d427870faaea_filter_wear
        name: Usure du Filtre
      - entity: sensor.aldes_d427870faaea_last_updated
        name: Dernière Mise à jour
  - type: markdown
    content: >
      ### Commandes Récentes
      {% set history = state_attr('sensor.aldes_d427870faaea_pending_commands', 'history') %}
      | Heure | Action |
      |-------|--------|
      {% for item in history | reverse %}
      | {{ item.split(' - ')[0] }} | {{ item.split(' - ')[1] }} |
      {% endfor %}
```
