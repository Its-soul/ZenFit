# API Documentation

## Overview

The ZenFit backend exposes a RESTful API versioned at `/api/v1`. All endpoints return JSON responses.

## Authentication

Most endpoints require authentication. Clients must provide a valid JWT access token in the `Authorization` header:

```http
Authorization: Bearer <your_access_token>
```

If a token is invalid, expired, or missing, the API responds with a `401 Unauthorized` status.

## Standard Responses

### Success (2xx)

```json
{
  "status": "success",
  "data": { ... }
}
```

### Error (4xx, 5xx)

```json
{
  "detail": "Descriptive error message here."
}
```

## API Categories

### 1. Auth `/api/v1/auth`

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/register` | Register a new user account. | No |
| `POST` | `/login` | Authenticate and obtain JWT tokens. | No |
| `POST` | `/refresh` | Obtain a new access token using a refresh token. | No (Requires Refresh Token) |
| `GET`  | `/me` | Retrieve the currently authenticated user's profile. | Yes |
| `POST` | `/logout` | Invalidate current session tokens. | Yes |

### 2. Workouts `/api/v1/workouts`

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET`  | `/` | List user's workout sessions. | Yes |
| `POST` | `/` | Create a new workout session log. | Yes |
| `GET`  | `/{id}` | Get specific workout details. | Yes |
| `PUT`  | `/{id}` | Update an existing workout. | Yes |
| `DELETE`| `/{id}` | Delete a workout record. | Yes |

### 3. Nutrition `/api/v1/nutrition`

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET`  | `/` | Retrieve logged meals for a specific date range. | Yes |
| `POST` | `/` | Log a new meal. | Yes |
| `POST` | `/analyze` | Analyze a meal description or image payload. | Yes |
| `GET`  | `/targets` | Retrieve daily macronutrient targets. | Yes |

### 4. Recovery & Sleep `/api/v1/recovery`

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET`  | `/` | Retrieve sleep and readiness logs. | Yes |
| `POST` | `/sleep` | Log a sleep session. | Yes |
| `POST` | `/checkin` | Submit a daily recovery check-in. | Yes |

### 5. Recommendations `/api/v1/recommendations`

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET`  | `/` | Retrieve current personalized recommendations. | Yes |
| `POST` | `/{id}/feedback` | Submit feedback (e.g., accepted, rejected) on a recommendation. | Yes |

## WebSocket API

The backend provides a realtime WebSocket endpoint for live updates.

- **Endpoint**: `ws://<host>/ws/dashboard?token=<jwt_access_token>`
- **Connection**: Requires passing the JWT access token as a query parameter for initial handshake authentication.
- **Usage**: Used for pushing live data updates (e.g., background job completion, urgent notifications) to the frontend client.
