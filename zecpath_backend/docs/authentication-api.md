# Authentication API Usage Guide

Base URL: `http://localhost:8000`

Examples use placeholders. Do not copy example passwords, tokens, or secret
values into a real environment.

## Signup

`POST /api/signup/`

No authentication is required.

```json
{
  "username": "alex_candidate",
  "email": "alex@example.test",
  "phone": "10000000001",
  "password": "Example-only-password-123!",
  "role": "CANDIDATE"
}
```

Success: `201 Created` with the created `user_id`. Public signup accepts only
`CANDIDATE` and `EMPLOYER`; administrator accounts must be created through a
protected administrative process. Validation errors return `400 Bad Request`.

## Login

`POST /api/login/`

No authentication is required.

```json
{
  "email": "alex@example.test",
  "password": "Example-only-password-123!"
}
```

Success: `200 OK` with `refresh` and `access` JWT values. Invalid credentials
return `401 Unauthorized`.

## Refresh an access token

`POST /api/token/refresh/`

Send the refresh token in the request body:

```json
{"refresh": "<refresh-token>"}
```

Success: `200 OK` with a new access token. Invalid or blacklisted tokens return
`401 Unauthorized`.

## Protected API request

Send the access token in the header:

```text
Authorization: Bearer <access-token>
```

For example, `GET /api/user-test/` returns `200 OK` for an authenticated user.
Missing or invalid credentials return `401 Unauthorized`; authenticated users
without the required role receive `403 Forbidden`.

## Logout

`POST /api/logout/`

Send the refresh token:

```json
{"refresh": "<refresh-token>"}
```

Success: `200 OK`. Missing, malformed, or already-invalid refresh tokens return
`400 Bad Request`. A valid token is blacklisted and cannot be refreshed
afterward.

## Role-protected endpoints

| Endpoint | Methods | Requirement |
|---|---|---|
| `/api/jobs/` | `GET` | Authenticated |
| `/api/jobs/` | `POST` | Authenticated `EMPLOYER` |
| `/api/applications/` | `GET` | Authenticated; candidates see their own, employers see applications for their jobs |
| `/api/applications/` | `POST` | Authenticated `CANDIDATE` |
| `/api/admin-control/` | `GET` | Authenticated `ADMIN` |
| `/api/candidate/profile/` | `GET`, `POST`, `PUT`, `DELETE` | Authenticated `CANDIDATE`, or `ADMIN` with `user_id` |
| `/api/employer/profile/` | `GET`, `POST`, `PUT`, `DELETE` | Authenticated `EMPLOYER`, or `ADMIN` with `user_id` |
| `/api/candidate/resume/` | `GET`, `POST`, `PUT`, `DELETE` | Authenticated `CANDIDATE`, or `ADMIN` with `user_id` |

Resume uploads accept PDF, DOC, and DOCX files up to 5 MB. File signatures and
document structure are validated, macro-enabled DOCX files are rejected, and
stored names are randomized.
