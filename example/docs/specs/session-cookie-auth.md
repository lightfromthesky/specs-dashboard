# Session-cookie authentication (initial design)

**Status:** Superseded by example/docs/specs/jwt-bearer-auth.md

## Problem

(From the original 2025-08 draft.) The TodoApp launched anonymous-only. To support multi-device sync (see `user-registration.md`), we need authenticated sessions.

## Solution (original proposal, now obsolete)

Server-side session storage. On login, the server creates a `sessions` row with a random session ID, sets it as an `httpOnly` cookie, and returns 200. Subsequent requests carry the cookie automatically; middleware loads the session row from the DB and attaches the user to the request.

Logout deletes the row server-side.

## Why this was superseded

Two issues that surfaced as the architecture decisions firmed up:

1. **Server-side session storage doesn't fit a stateless API design.** We're targeting horizontal-scale-out on the API tier; every request loading a session from DB pins us to either a shared DB or sticky sessions. JWTs avoid that entirely — the token is the session, no server-side lookup needed.
2. **The mobile client uses pure REST + Bearer tokens.** Cookie-based sessions on web + Bearer tokens on mobile means two auth code paths. JWTs unify both.

[jwt-bearer-auth.md](jwt-bearer-auth.md) takes the JWT approach: signed token returned on login, stored client-side, sent via `Authorization: Bearer` on every request. Same user-facing UX, simpler server architecture.

Spec kept as history.
