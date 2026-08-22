# Security Documentation

## 1. Authentication Strategy

ZenFit implements a robust, custom Email/Password authentication system backed by JWT (JSON Web Tokens).

- **Token Types**: The system issues short-lived Access Tokens (e.g., 15 minutes) and long-lived Refresh Tokens.
- **Validation**: Every protected endpoint validates the JWT signature and expiration.
- **Revocation**: Password resets and explicit logouts increment a user token version in the database, effectively invalidating previously issued refresh tokens.

## 2. Password Handling

- Passwords are never stored in plain text.
- Passwords are hashed using the strong `bcrypt` algorithm before insertion into the database.
- The backend verification process securely compares the hashed values.

## 3. Secret Management

- **Environment Variables**: All sensitive configuration, including database credentials, JWT secret keys, and external API tokens, are managed strictly via environment variables.
- **No Hardcoded Secrets**: Secrets are never hardcoded in the source code or committed to version control.
- **.gitignore**: Files containing local environment overrides (e.g., `.env`, `.env.local`) are explicitly ignored by Git.

## 4. Input Validation & Protection

- **Schema Validation**: The FastAPI backend utilizes Pydantic schemas to rigorously validate all incoming request bodies and query parameters. Malformed or unexpected data is rejected automatically with a `422 Unprocessable Entity` response.
- **SQL Injection Prevention**: The use of SQLAlchemy ORM provides inherent protection against SQL injection attacks by using parameterized queries.

## 5. Network Security & Headers

- **CORS (Cross-Origin Resource Sharing)**: The backend is configured to accept requests only from explicitly permitted frontend origins. This prevents unauthorized web clients from interacting with the API.
- **Rate Limiting**: Critical endpoints (like login and password reset) can be rate-limited using Redis to mitigate brute-force attacks.

## 6. Sensitive Data Handling

- **Data Isolation**: Database queries are strictly scoped by the authenticated user's ID. Users cannot access or modify records belonging to other users.
- **Health Data Privacy**: Personal health and fitness metrics are treated as sensitive data and are transmitted only over secure, encrypted channels (HTTPS/WSS) in production environments.

## 7. Known Risks & Considerations

- **Client-Side Storage**: JWTs are currently stored in the browser's `localStorage`. While standard, this requires strict protection against Cross-Site Scripting (XSS) vulnerabilities in the frontend application.
- **Deployment**: Production deployments must ensure that the application is served over HTTPS to protect data in transit and token integrity.
