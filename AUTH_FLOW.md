# Authentication Flow Documentation

## Overview

Authentication is custom email/password auth implemented in FastAPI with JWT bearer tokens. There are no external auth providers.

Auth provider:

```text
Custom local email/password provider
```

No Firebase Auth, Supabase Auth, Auth.js/NextAuth, OAuth, SAML, Magic Link, Redux auth slice, Zustand store, or React Context auth provider exists.

## Backend Auth Files

| File | Responsibility |
|---|---|
| `backend/app/modules/auth/routes.py` | Register, login, current-user endpoints. |
| `backend/app/modules/auth/service.py` | Auth business logic, password verification, token response. |
| `backend/app/modules/auth/repository.py` | User database queries. |
| `backend/app/modules/auth/models.py` | `User` SQLAlchemy model. |
| `backend/app/modules/auth/schemas.py` | Auth request/response schemas. |
| `backend/app/core/security.py` | Password hashing, password verification, JWT creation/decoding. |
| `backend/app/dependencies.py` | `get_current_user` dependency using HTTP bearer auth. |
| `backend/app/realtime/routes.py` | WebSocket token validation. |

## Frontend Auth Files

| File | Responsibility |
|---|---|
| `frontend/app/auth/login/page.js` | Login form and redirect. |
| `frontend/app/auth/register/page.js` | Register form and redirect. |
| `frontend/app/onboarding/page.js` | Protected onboarding page. |
| `frontend/lib/authStorage.js` | `localStorage` token/user helpers. |
| `frontend/hooks/useAuth.js` | Client auth state and protected-route redirect. |
| `frontend/services/authService.js` | Auth API calls and session persistence. |
| `frontend/services/apiClient.js` | Adds `Authorization: Bearer <token>` to API requests. |
| `frontend/hooks/useWebSocket.js` | Sends JWT as WebSocket query parameter. |

## Backend Login/Register Flow

Register:

```text
POST /api/v1/auth/register
  -> AuthService.register
  -> UserRepository.get_by_email
  -> hash_password
  -> UserRepository.create
  -> UserProfileRepository.create_for_user
  -> create_access_token
  -> TokenResponse
```

Login:

```text
POST /api/v1/auth/login
  -> AuthService.login
  -> UserRepository.get_by_email
  -> verify_password
  -> create_access_token
  -> TokenResponse
```

Current user:

```text
GET /api/v1/auth/me
  -> get_current_user
  -> decode_access_token
  -> UserRepository.get_by_id
  -> UserResponse
```

## JWT Details

JWT creation is in `backend/app/core/security.py`:

```python
def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expires_at}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
```

JWT claims:

| Claim | Meaning |
|---|---|
| `sub` | User UUID string. |
| `exp` | Expiration timestamp. |
| `email` | Extra claim added during token creation. |

JWT settings:

| Setting | File | Default |
|---|---|---|
| `JWT_SECRET_KEY` | `backend/app/config.py` | `change-this-in-production` |
| `JWT_ALGORITHM` | `backend/app/config.py` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `backend/app/config.py` | `1440` |

## Password Handling

Password hashing is in `backend/app/core/security.py`:

```python
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

Stored field:

```text
users.hashed_password
```

The plain password is never stored by the auth service. Demo seed passwords are hashed before insertion in `backend/app/demo/seeder.py`.

## Frontend Token Storage

Exact storage keys are defined in `frontend/lib/authStorage.js`:

```javascript
const TOKEN_KEY = "fitness_os_token";
const USER_KEY = "fitness_os_user";
```

Storage locations:

| Data | Browser Storage | Key | Set In | Cleared In |
|---|---|---|---|---|
| JWT access token | `localStorage` | `fitness_os_token` | `saveAuthSession` | `clearAuthSession` |
| User JSON | `localStorage` | `fitness_os_user` | `saveAuthSession` | `clearAuthSession` |

No `sessionStorage` keys exist.

No application cookies are set.

## API Auth Header

`frontend/services/apiClient.js` injects the bearer token:

```javascript
apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

Backend reads it via FastAPI `HTTPBearer` in `backend/app/dependencies.py`.

## Protected Routes

There is no Next.js middleware file.

Protection is client-side through `useAuth({ requireAuth: true })`.

Files using protected auth flow:

| File | Protection |
|---|---|
| `frontend/components/layout/ProtectedFeaturePage.js` | Calls `useAuth({ requireAuth: true })`. |
| `frontend/app/dashboard/page.js` | Calls `useAuth({ requireAuth: true })`. |
| `frontend/app/onboarding/page.js` | Calls `useAuth({ requireAuth: true })`. |

Routes wrapped by `ProtectedFeaturePage`:

- `/workouts`
- `/nutrition`
- `/recovery`
- `/sleep`
- `/coach`
- `/analytics`
- `/settings`

If `/auth/me` fails and `requireAuth` is true, `useAuth` clears auth storage and redirects to `/auth/login`.

## Login, Logout, Register UI Flow

Register:

```text
frontend/app/auth/register/page.js
  -> register(form)
  -> POST /auth/register
  -> saveAuthSession
  -> router.replace("/onboarding")
```

Login:

```text
frontend/app/auth/login/page.js
  -> login(form)
  -> POST /auth/login
  -> saveAuthSession
  -> onboarding_complete ? /dashboard : /onboarding
```

Logout:

```text
AppShell Logout button
  -> useAuth.logout
  -> authService.logout
  -> clearAuthSession
  -> router.replace("/auth/login")
```

## WebSocket Auth

Frontend:

```text
frontend/hooks/useWebSocket.js
```

It connects to:

```text
{NEXT_PUBLIC_WS_URL}/dashboard?token={jwt}
```

Backend:

```text
backend/app/realtime/routes.py
```

The token is decoded with `decode_access_token`, then the user is loaded from PostgreSQL.

## Auth Data Storage Summary

| Data | Location |
|---|---|
| User account | PostgreSQL `users` table. |
| Password hash | PostgreSQL `users.hashed_password`. |
| User profile | PostgreSQL `user_profiles` table. |
| JWT secret | Environment variable `JWT_SECRET_KEY`. |
| JWT token in browser | `localStorage.fitness_os_token`. |
| Stored user in browser | `localStorage.fitness_os_user`. |
| Session cookie | None. |
| Refresh token | None. |
| Redux/Zustand/context auth state | None. |
| React runtime auth state | `frontend/hooks/useAuth.js`. |

## Security Notes

- `localStorage` JWT storage is simple but XSS-sensitive.
- `JWT_SECRET_KEY=change-this-in-production` is unsafe outside local development.
- `ACCESS_TOKEN_EXPIRE_MINUTES=1440` is long-lived.
- WebSocket token in query string may appear in logs.
- There is no server-side Next.js middleware protection.
- There is no refresh token or revocation system.

