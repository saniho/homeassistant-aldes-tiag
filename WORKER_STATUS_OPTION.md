# 🔍 Option 7: Vérifier le statut du worker

## Qu'est-ce que c'est?

C'est une nouvelle option du menu qui affiche:
- ✅ Si le worker de température fonctionne
- ✅ Si la queue a des requêtes en attente
- ✅ Combien de temps avant que les requêtes soient traitées

## Pourquoi c'est utile?

Quand vous changez la température:
1. La requête est mise dans une **queue**
2. Un **worker** traite les requêtes en background
3. Vous voyez "✓ Température modifiée!" immédiatement
4. Mais la requête API peut encore être en queue!

Cette option vous permet de **vérifier que le worker fonctionne réellement**.

## Comment l'utiliser?

```
1. Lancer le test: python test_standalone.py
2. Option 1: S'authentifier
3. Option 2: Récupérer les données
4. Option 3: Changer la température (pour une pièce)
   → Vous verrez "✓ Température modifiée!"
5. Option 7: Vérifier le statut du worker
   → Vous verrez l'état de la queue
```

## Exemple de sortie

### Après avoir changé la température (requête pas encore traitée):

```
==================================================
   STATUT DU WORKER DE TEMPÉRATURE
==================================================

Worker créé: ✓ Oui
Worker actif: ✓ Oui (en cours)
Queue créée: ✓ Oui
Éléments en queue: 1

⚠️  Requêtes en attente:
  (Les requêtes seront traitées par le worker)
  - 1 requête(s) en queue
  - Le worker traite 1 requête tous les 5 secondes
  - ETA: ~5 secondes

ℹ️  Comment ça fonctionne:
  1. Quand vous changez la température → Requête mise en queue
  2. Worker récupère la requête → Appelle l'API
  3. API met à jour → Nouvelle donnée
  4. Prochaine lecture → Données à jour affichées
```

### Après que le worker ait traité:

```
==================================================
   STATUT DU WORKER DE TEMPÉRATURE
==================================================

Worker créé: ✓ Oui
Worker actif: ✓ Oui (en cours)
Queue créée: ✓ Oui
Éléments en queue: 0

✓ Queue vide (aucune requête en attente)

ℹ️  Comment ça fonctionne:
  1. Quand vous changez la température → Requête mise en queue
  2. Worker récupère la requête → Appelle l'API
  3. API met à jour → Nouvelle donnée
  4. Prochaine lecture → Données à jour affichées
```

## Workflow complet

```
Option 1: Authentifier
   ↓
Option 2: Récupérer les données
   ↓
Option 3: Changer température
   → Message: "✓ Température modifiée!"
   → Requête mise en queue (invisible)
   ↓
Option 7: Vérifier worker (immédiat)
   → Affiche: "Éléments en queue: 1"
   ↓
Attendre ~5 secondes (worker traite)
   ↓
Option 7: Vérifier worker à nouveau
   → Affiche: "Éléments en queue: 0" ✓
   ↓
Option 2: Récupérer les données
   → Nouvelle température affichée! ✅
```

## Comprendre le timing

Le worker traite **1 requête toutes les 5 secondes** pour éviter de surcharger l'API.

- Si vous avez 1 requête en queue: ETA ~5 secondes
- Si vous avez 3 requêtes en queue: ETA ~15 secondes
- etc.

## Signification des statuts

| Statut | Signification | Action |
|--------|---|---|
| Worker créé: ✓ | Worker est prêt | Aucune (normal) |
| Worker actif: ✓ | Worker traite les requêtes | Aucune (normal) |
| Queue créée: ✓ | File d'attente existe | Aucune (normal) |
| Éléments: 0 | Aucune requête en queue | Aucune (normal) |
| Éléments: 1+ | Requête(s) en attente | Attendre quelques secondes |

## Problèmes possibles

### "Worker créé: ✗ Non"
- Aucune requête de changement de température n'a été envoyée
- Le worker ne démarre que quand vous changez la température

### "Worker actif: ✗ Non (arrêté)"
- Le worker s'est arrêté prématurément
- Peut indiquer une erreur dans le traitement

### "Queue créée: ✗ Non"
- Aucune requête n'a été envoyée
- Normal si vous n'avez pas changé la température

## Conclusion

Cette option vous permet de **vérifier que le système de file d'attente fonctionne correctement** et que les requêtes sont bien traitées par le worker en background!
