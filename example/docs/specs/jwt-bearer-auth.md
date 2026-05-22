# JWT bearer token authentication

**Status:** Shipped 2026-02-14

## Problem

The original auth design (see `session-cookie-auth.md`) used server-side session storage. As the architecture firmed up around a horizontally-scaling stateless API + a separate mobile client, server-side sessions stopped fitting:

- Every authenticated request had to load a session row from the DB. Either we pin to a shared DB (latency on every request) or implement sticky sessions (operationally annoying).
- The mobile client uses `Authorization: Bearer` natively. Cookie-based sessions on web + Bearer on mobile means two auth code paths.

## Solution

Issue a signed JWT on login. The token is the session — server-side state holds nothing per logged-in user, just a `revoked_tokens` set for forced logout.

Token shape (15-minute access + 7-day refresh):

```json
{
  "sub": "user-uuid",
  "iat": 1234567890,
  "exp": 1234568790,
  "type": "access"
}
```

Both clients send `Authorization: Bearer <jwt>` on every request. Web also stores in an `httpOnly` cookie (XSS-resistant); the cookie is read on the server side and forwarded as `Authorization` to upstream services. Mobile stores in the platform's secure-storage API (Keychain on iOS, Keystore on Android).

## Implementation

- [x] JWT mint + verify on the auth service — [#33](https://example.com/pull/33)
- [x] Web cookie-set on login + auth middleware reads from `req.cookies` — [#35](https://example.com/pull/35)
- [x] Mobile secure-storage adapter (RN bridge) — [#37](https://example.com/pull/37)
- [x] Revoke-on-logout via Redis token blacklist — [#39](https://example.com/pull/39)

## Risks & rollback

JWT secret rotation needs a planned procedure (key versioning in the token header). Documented in `runbooks/jwt-secret-rotation.md`. Rollback to session cookies is possible but would require a multi-day re-issue window for active users.
