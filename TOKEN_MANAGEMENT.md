# 🔐 Gestion du Token d'Authentification

## Flux d'authentification complet

```
┌─────────────────────────────────────────┐
│ 1. Menu Test Standalone                 │
│    (test_standalone.py)                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 2. Utilisateur choisit Option 1         │
│    "S'authentifier"                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 3. Input: Email + Mot de passe          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 4. AldesTestMenu.authenticate()         │
│    → AldesApi.authenticate()            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 5. Appel API: POST /oauth2/token        │
│    Envoie: {grant_type, username, pwd} │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 6. API Aldes retourne: {access_token}   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 7. Token sauvegardé dans:               │
│    self._token = "eyJ0eXAi..."          │
└──────────────┬──────────────────────────┘
               │
               ▼
       ✓ Authentification OK
```

---

## Étape 2: Récupération des données

```
┌─────────────────────────────────────────┐
│ 1. Utilisateur choisit Option 2         │
│    "Récupérer les données du compte"    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 2. AldesTestMenu.fetch_data()           │
│    → AldesApi.fetch_data()              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 3. AldesApi._api_request(GET, /products)│
└──────────────┬──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ 4. VÉRIFICATION: Token existe?           │
│    if not self._token:                   │
│       raise AuthenticationError          │
└──────────────┬─────────────────────────┘
               │
         ✓ OUI (token trouvé)
               │
               ▼
┌──────────────────────────────────────────┐
│ 5. Construction des headers:             │
│    Authorization: Bearer {self._token}   │
└──────────────┬─────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ 6. Appel API:                            │
│    GET /aldesoc/v5/users/me/products     │
│    Headers: {Authorization: Bearer ...}  │
└──────────────┬─────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ 7. API valide le token et retourne:      │
│    {modem, device_type, rooms, ...}      │
└──────────────┬─────────────────────────┘
               │
               ▼
       ✓ Données reçues avec succès
```

---

## Code: Où le token est utilisé?

### 1. **Dans `authenticate()` (aldes_api_standalone.py:130-145)**

```python
async def authenticate(self) -> None:
    """Récupère le token et le sauvegarde."""
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": self._USER_AGENT,
        "apikey": self._API_KEY,
        # ...
    }
    
    # Appel à l'API Aldes
    async with self._session.post(
        self._API_URL_TOKEN,
        data=data,
        headers=headers,
        timeout=self._timeout
    ) as response:
        if response.status == 200:
            json_resp = await response.json()
            # ✓ SAUVEGARDE DU TOKEN
            self._token = json_resp["access_token"]
            _LOGGER.info("Successfully authenticated")
```

**Token sauvegardé dans:** `self._token`

---

### 2. **Dans `_api_request()` (aldes_api_standalone.py:155-180)**

```python
async def _api_request(self, method: str, url: str, **kwargs: Any):
    """Utilise le token pour les requêtes ultérieures."""
    
    # ✓ VÉRIFICATION: Token existe?
    if not self._token:
        raise AuthenticationError(
            "Token not available. Please authenticate first."
        )
    
    # Préparation des headers
    headers = kwargs.get("headers", {})
    # ✓ AJOUT DU TOKEN AUX HEADERS
    headers["Authorization"] = f"Bearer {self._token}"
    kwargs["headers"] = headers
    
    # Exécution de la requête avec le token
    async with request_func(url, **kwargs) as response:
        # ...
```

**Utilisation du token:** `Authorization: Bearer {self._token}`

---

### 3. **Dans `fetch_data()` (aldes_api_standalone.py:216-230)**

```python
async def fetch_data(self) -> dict[str, Any] | None:
    """Récupère les données du compte."""
    _LOGGER.debug("Fetching data from Aldes API...")
    try:
        # Appel à _api_request avec le token
        # ✓ _api_request utilise self._token automatiquement
        data = await self._api_request("get", self._API_URL_PRODUCTS)
    except (ClientError, TimeoutError):
        _LOGGER.exception("Failed to fetch data")
        return None
```

---

## Sécurité: Où le token est protégé?

### ✓ Masquage dans les logs

```python
def _log_request_details(self, method: str, url: str, headers: dict, data: Any = None):
    """Les headers sensibles ne sont pas loggés."""
    safe_headers = {
        k: v for k, v in headers.items() 
        if k.lower() != "authorization"  # ✓ Token masqué!
    }
    _LOGGER.debug("Headers: %s", safe_headers)
```

### ✓ Token jamais affiché

```python
# ✗ MAUVAIS - Jamais fait
_LOGGER.debug(f"Token: {self._token}")  # ✗ DANGER!

# ✓ BON - Token masqué
headers["Authorization"] = f"Bearer {self._token}"
# Seuls les logs montrent: "Authorization: Bearer ****"
```

---

## Gestion des erreurs

### Erreur: "Token not available"

```
Cause: Vous avez essayé fetch_data() sans vous authentifier d'abord

Solution:
1. Sélectionner Option 1 (S'authentifier)
2. Entrer vos identifiants
3. Attendre le succès
4. Puis sélectionner Option 2 (Récupérer données)

Code qui lève l'erreur:
if not self._token:
    raise AuthenticationError(
        "Token not available. Please authenticate first."
    )
```

### Erreur: "Authentication failed with status 401"

```
Cause: Token expiré ou invalide lors d'une requête

Solution:
1. Vous authentifier à nouveau (Option 1)
2. Le nouveau token remplace l'ancien
3. Réessayer la requête (Option 2)
```

---

## Checkpoints de validation

Voici comment vérifier que le token est bien géré:

### ✅ Checkpoint 1: Token après authentification

```python
# Dans test_standalone.py après authenticate()
async def authenticate(self) -> bool:
    # ...
    await self.api.authenticate()
    print("\n✓ Authentification réussie!")
    # À ce point: self.api._token contient le token JWT
    return True
```

**Vérifier:**
- `api._token` n'est pas vide
- `api._token` commence par "eyJ"
- Pas d'exception levée

### ✅ Checkpoint 2: Token utilisé dans fetch_data

```python
async def fetch_data(self) -> bool:
    # ...
    raw_data = await self.api.fetch_data()
    # À ce point:
    # - Si raw_data est None → Token invalide ou expiré
    # - Si raw_data est dict → Token valide et accepté par API
```

**Vérifier:**
- Si `raw_data` est présent → Token était valide
- Si erreur "Token not available" → Oubli authentification
- Si erreur 401 → Token expiré ou invalide

### ✅ Checkpoint 3: Token dans les headers

```python
# Dans _api_request(), avant la requête:
headers["Authorization"] = f"Bearer {self._token}"

# Vérifier avec logs:
_LOGGER.debug("Headers: %s", safe_headers)
# Output: Headers: {'Content-Type': '...', 'Accept': '...'}
# ✓ Authorization n'est pas affichée (masquée pour sécurité)
```

---

## Résumé: Token lifecycle

| Étape | Token Status | Qué se passe? |
|-------|--------------|---------------|
| 1. Démarrage | ❌ Vide | `self._token = ""` |
| 2. Authentification | ✅ Reçu | `self._token = "eyJ0eXAi..."` |
| 3. Fetch Data | ✅ Utilisé | `Authorization: Bearer eyJ0eXAi...` |
| 4. Succès | ✅ Valide | Données reçues |
| 5. Nouveau test | ✅ Réutilisable | Même token pour autres requêtes |
| 6. Expiration (1h) | ❌ Expiré | Re-authentifier (Option 1) |

---

## Code de test: Vérifier le token

Créez un fichier `test_token.py`:

```python
import asyncio
import aiohttp
from aldes_api_standalone import AldesApi

async def main():
    async with aiohttp.ClientSession() as session:
        api = AldesApi("email@example.com", "password", session)
        
        # Avant authentification
        print(f"1. Avant auth: token = '{api._token}'")  # ''
        
        # Authentification
        await api.authenticate()
        print(f"2. Après auth: token = '{api._token[:20]}...'")  # 'eyJ0eXAi...'
        
        # Fetch data (utilise le token)
        data = await api.fetch_data()
        if data:
            print(f"3. Fetch data: OK (token valide)")
            print(f"   Modem: {data.get('modem')}")
        else:
            print(f"3. Fetch data: FAILED (token invalide)")

asyncio.run(main())
```

Lancez:
```bash
python test_token.py
```

---

## Conclusion

✅ **OUI, le token est bien géré:**

1. **Sauvegardé** après authentification dans `self._token`
2. **Vérifié** avant chaque requête (`if not self._token`)
3. **Utilisé** dans chaque requête API (`Authorization: Bearer {token}`)
4. **Protégé** dans les logs (masqué)
5. **Gestion d'erreur** complète si token invalide/expiré

Le flux est sécurisé et suit les bonnes pratiques OAuth2.
