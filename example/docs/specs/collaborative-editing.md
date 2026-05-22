# Collaborative todo lists (multi-user)

**Status:** Draft

## Problem

Several users have asked for shared lists — "Groceries", "House Projects" — where multiple people can add/check todos. Currently every account is solo; sharing means screenshotting a list to a partner.

## Solution (proposal)

Two new concepts:

1. **`Workspace`** — a named container of todos that one or more users have access to.
2. **`Membership`** — links a user to a workspace with a role (`owner` / `editor` / `viewer`).

The existing solo experience is preserved by giving every user a "Personal" workspace at signup.

Sharing flow:

- Owner clicks "Share list" → enters an email
- If the email matches an existing user → send invite notification
- If not → send a sign-up + invite combined link
- Invitee accepts → joins the workspace with the offered role

Real-time sync (already in flight in `realtime-sync.md`) is a prerequisite — collaborative edits without real-time updates would be frustrating.

## Implementation

- [ ] Migration: `workspaces`, `memberships` tables; backfill every user's todos into a "Personal" workspace
- [ ] API: scope all `/api/todos` endpoints by workspace; add `/api/workspaces` CRUD
- [ ] Invite + accept flow + email templates
- [ ] Frontend: workspace switcher in the sidebar
- [ ] Permission UI: per-membership role chip with role-change controls for owners

## Open questions

- Conflict resolution for simultaneous edits to the same todo. Last-write-wins is the simplest answer; matches Google Docs' offline-edit semantics. Operational transform / CRDT is overkill at this scale.
- Whether viewers can comment (without checking). Adds a `comments` table — deferred until v2 unless users specifically ask.

Not started — waiting on `realtime-sync.md` to ship first.
