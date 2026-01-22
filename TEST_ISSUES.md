# ⚠️ Test Issues - À corriger ultérieurement

## Problèmes identifiés

Les tests actuels ont plusieurs problèmes qui causent des erreurs lors de l'exécution :

### 1. **Lingering Tasks** 🔴
```
Failed: Lingering task after test <Task pending name='Task-19' ...>
```

**Cause** : Les tâches asyncio (`_temperature_worker`, `_verify_temperature_change_after_delay`) ne sont pas correctement annulées à la fin des tests.

**Solution** : Ajouter un fixture pytest pour nettoyer les tâches après chaque test.

### 2. **Mock Context Manager Issues** 🔴
```
TypeError: 'coroutine' object does not support the asynchronous context manager protocol
```

**Cause** : Les mocks async (AsyncMock) ne retournent pas correctement un context manager.

**Solution** : Utiliser `AsyncMock()` correctement avec `__aenter__` et `__aexit__`.

### 3. **Lingering Threads** 🔴
```
AssertionError: assert (False or False) where ... 'Thread-11 (_run_safe_shutdown_loop)'
```

**Cause** : Home Assistant crée des threads de nettoyage qui ne sont pas correctement fermés.

**Solution** : Ajouter un fixture pour nettoyer les threads avant les tests.

## Status Actuel

- ✅ **Ruff** - Tout OK
- ✅ **Black** - Tout OK
- ✅ **Hassfest** - Tout OK
- ⚠️ **Pytest** - Tests en erreur (continue-on-error=true dans CI/CD)

## Prochaines étapes

1. **Corriger les tests localement** :
   - Ajouter un cleanup fixture pour les tâches asyncio
   - Fixer les mocks async
   - Ajouter un cleanup pour les threads

2. **Tester localement** :
   ```bash
   pytest tests -v
   ```

3. **CI/CD** : Les tests ne bloquent pas le pipeline pour l'instant (`continue-on-error: true`)

## Fichiers concernés

- `tests/test_api.py` - Problèmes avec les mocks et les tâches
- `tests/test_climate.py` - Lingering tasks de vérification
- `custom_components/aldes/api.py` - Worker tasks
- `custom_components/aldes/climate.py` - Retry tasks

