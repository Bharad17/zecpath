# Day 15 Architecture Review and Self-Assessment

**Status:** Proposed architecture review and self-assessment. No mentor
meeting, approval, or feedback is represented as completed.

## Architecture overview

The Django URL configuration routes requests to DRF API views. Serializers
validate request data and shape responses. `services/auth_service.py` owns
email/password authentication and JWT pair creation. Role permissions remain
in `core/permissions.py`. Profile and resume behavior remains in
`core/profile_views.py`; models and upload path rules remain in
`core/models.py`. SimpleJWT validates access/refresh tokens and the blacklist
app supports logout invalidation.

## Refactoring performed

- Consolidated login credential authentication and JWT issuance in
  `services/auth_service.py`.
- Removed duplicate serializer imports and replaced broad refresh-token
  exception handling with the library's `TokenError`.
- Preserved existing endpoint paths and response shapes.
- Kept Day 14 query services, pagination, deterministic ordering, and related
  object loading intact.

## Security checks and findings

### Addressed in this change

- Public signup now permits only `CANDIDATE` and `EMPLOYER`; it cannot create
  an `ADMIN` account.
- Application listing is scoped to the requesting candidate or employer; an
  administrator may inspect the complete set.
- Hard-coded Django secret keys were removed from both tracked settings copies.
  Settings now require `SECRET_KEY` from the environment.

### Verified controls

- Access tokens expire after 15 minutes; refresh tokens expire after 1 day.
- Refresh-token blacklisting is installed and logout calls `blacklist()`.
- Role permissions protect employer, candidate, and admin operations.
- Candidate resume validation checks extension, size, signatures/structure, and
  macro-enabled DOCX content; randomized storage names avoid original-name
  reuse.

### Remaining review items

- Deployment should set secure production settings such as HTTPS, restrictive
  hosts, and a production secret-management process.
- No formal penetration test or external mentor review was available for this
  self-assessment.
- The previously committed secret must be rotated and removed from repository
  history through the repository's approved secret-rotation process.

## Design decisions

- Use a small authentication service rather than rewriting all views.
- Keep JWT response contracts and endpoint paths backward compatible.
- Treat missing mentor evidence as unverified, not as approval.

## Proposed mentor discussion questions

1. Should logout require a valid access token in addition to the refresh token?
2. Should login and signup receive throttling or lockout controls?
3. Which production secret manager and deployment security settings are
   required before release?
4. Should profile authorization be extracted into a dedicated policy service?

## Mentor feedback to record

_Pending actual mentor comments, decisions, owners, and target dates._
