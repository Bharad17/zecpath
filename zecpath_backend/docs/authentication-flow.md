# Authentication Flow

This diagram reflects the implemented Zecpath authentication endpoints.

```mermaid
sequenceDiagram
    participant Client
    participant API as Zecpath API
    participant DB as User database
    participant JWT as SimpleJWT

    Client->>API: POST /api/signup/ (user details)
    API->>DB: Validate and create user
    DB-->>API: user_id
    API-->>Client: 201 Created

    Client->>API: POST /api/login/ (email, password)
    API->>DB: Look up user and authenticate password
    API->>JWT: Issue refresh and access tokens
    JWT-->>Client: token pair

    Client->>API: Protected request + Bearer access token
    API->>JWT: Validate access token
    JWT-->>API: Authenticated user and role
    API-->>Client: Protected response or 401/403

    Client->>API: POST /api/token/refresh/ (refresh token)
    API->>JWT: Validate refresh token
    JWT-->>Client: New access token

    Client->>API: POST /api/logout/ (refresh token)
    API->>JWT: Blacklist refresh token
    API-->>Client: 200 Logout successful
```

## Protected surfaces

- `GET /api/user-test/` is an authenticated smoke-test endpoint.
- `GET` and `POST /api/jobs/` require authentication; job creation is employer-only.
- `GET` and `POST /api/applications/` require authentication; application creation is candidate-only.
- Profile and resume endpoints require authentication and enforce the requested user's role.
- `GET /api/admin-control/` is restricted to users with the `ADMIN` role.
