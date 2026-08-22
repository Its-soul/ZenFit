# Low-Level Design (LLD)

## 1. Module Structure

The ZenFit repository is organized into distinct domain boundaries:

```text
ZenFit/
├── frontend/          # Next.js client application
├── backend/           # FastAPI application
│   ├── app/           # Core application code
│   │   ├── core/      # Security, configuration, database setup
│   │   ├── modules/   # Domain-driven features (Auth, Workouts, Nutrition, etc.)
│   │   └── realtime/  # WebSocket handlers
│   └── scripts/       # Developer utilities
├── data/              # Ephemeral data, uploads, local databases (git-ignored)
└── deployment/        # Deployment configurations
```

## 2. Frontend Modules

The frontend is structured around Next.js App Router conventions:

- **Routing & Pages**: `app/` contains the route definitions. Sub-folders like `auth`, `workouts`, `nutrition`, `sleep`, and `recovery` map to application URLs.
- **Components**: `components/` contains reusable UI elements built with React and styled with Tailwind CSS.
- **Hooks**: `hooks/` contains custom React hooks (e.g., `useAuth`, `useWebSocket`) to encapsulate client-side logic and state management.
- **Services**: `services/` contains API client wrappers (e.g., `apiClient.js`, `authService.js`) to standardize network requests and token injection.

## 3. Backend Modules

The backend implements a Modular Monolith architecture. Each feature is self-contained in `backend/app/modules/`:

- **Auth Module**: Handles registration, login, JWT issuance, and password resets.
- **Workouts Module**: Manages workout plans, exercise logging, and completion status.
- **Nutrition Module**: Tracks daily meals, caloric intake, macros, and interacts with nutrition lookup APIs.
- **Recovery Module**: Logs sleep metrics, readiness scores, and manages daily check-ins.
- **Recommendations Module**: Generates and serves personalized user advice.

Each module typically follows a standard internal structure:
- `models.py`: SQLAlchemy ORM definitions.
- `schemas.py`: Pydantic models for request/response validation.
- `repository.py`: Database access and query logic.
- `service.py`: Business logic.
- `routes.py`: FastAPI endpoint definitions.

## 4. Service Responsibilities

- **Authentication Service**: Strictly responsible for identity verification. It never stores plain-text passwords and relies on bcrypt for hashing.
- **Data Processing Service**: Abstracts the logic for analyzing user uploads (e.g., images for meal logging). It provides a standardized interface for predictions and handles graceful fallbacks if primary analysis is unavailable.
- **Recommendation Engine**: Aggregates data from workouts, nutrition, and recovery. It evaluates this context against predefined rules and historical patterns to output ranked, actionable insights.

## 5. API Design

APIs follow RESTful principles with standard HTTP verbs:
- `GET`: Retrieve resources.
- `POST`: Create new resources or execute state-changing actions.
- `PUT/PATCH`: Update existing resources.
- `DELETE`: Remove resources.

All secure endpoints require an `Authorization: Bearer <token>` header. Input validation is strictly enforced by FastAPI and Pydantic before any business logic executes.

## 6. Request Lifecycle

1. **Client Request**: Initiated by the Next.js frontend.
2. **Middleware/Gateway**: CORS and rate-limiting are applied.
3. **Dependency Injection**: FastAPI extracts the JWT, validates it, and fetches the `current_user`.
4. **Validation**: The request body is validated against the corresponding Pydantic schema.
5. **Controller (Route)**: The route handler delegates the validated payload to the Service layer.
6. **Business Logic & Repository**: The Service layer executes business rules and uses the Repository layer to interact with the database.
7. **Response**: Data is serialized via Pydantic response schemas and returned to the client as JSON.

## 7. Database Entities & Relationships

The relational database uses a normalized schema:
- **`users`**: Core identity (ID, email, hashed password).
- **`user_profiles`**: Demographics, goals, and settings (One-to-One with `users`).
- **`workout_sessions`**: Logged workouts (Many-to-One with `users`).
- **`meals`**: Logged nutrition (Many-to-One with `users`).
- **`sleep_logs`**: Sleep duration and quality (Many-to-One with `users`).

## 8. Authentication Flow

- **Registration**: Email and plain text password -> Hashed and stored -> JWT Access/Refresh tokens returned.
- **Login**: Email and password verified against hash -> JWT Access/Refresh tokens returned.
- **Client Storage**: Tokens are stored securely in the client (e.g., `localStorage`).
- **Refresh**: When the access token expires, the client sends the refresh token to obtain a new access token.

## 9. Error Handling

Errors are managed globally using FastAPI exception handlers. Custom exceptions (e.g., `NotFoundError`, `UnauthorizedError`) map to specific HTTP status codes (404, 401) and return standard JSON error structures to the frontend.

## 10. Background Jobs

Heavy operations are decoupled from the HTTP request cycle using asynchronous background tasks.
- **Task Queue**: Redis manages the queue.
- **Workers**: Separate processes consume jobs (e.g., updating complex user recommendations, processing images) to keep the API responsive.
