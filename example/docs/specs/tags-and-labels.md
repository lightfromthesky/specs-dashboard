# Tags and labels for todos

**Status:** Draft

## Problem

Categories are single-valued (one per todo) and capped at 8 system-defined options. Users want to slice their todos by ad-hoc dimensions that don't fit the rigid taxonomy: `#work`, `#waiting-on-vendor`, `#high-priority`, `#kid-school`, etc. Several have asked for "tag-like" labels with multi-value support and free-form text.

## Solution (proposal)

Add `tags TEXT[]` to `todos`. Frontend exposes a tag-picker on each row that:

- Suggests already-used tags as the user types (autocomplete from `SELECT DISTINCT unnest(tags) FROM todos WHERE user_id = ?`)
- Accepts new tags inline
- Lets the user filter the timeline by one or more tags

Tags are user-scoped — one user's `#work` doesn't appear in another user's autocomplete. Tag deletion is a per-todo concern; we don't need a separate `tags` table.

## Implementation

- [ ] Migration: `ALTER TABLE todos ADD COLUMN tags TEXT[] DEFAULT '{}'`
- [ ] Backfill: nothing needed — empty array is the right starting state
- [ ] API: tag CRUD on the todo (`PATCH /api/todos/:id { tags: [...] }`); list filter `?tags=work,urgent`
- [ ] Autocomplete endpoint: `GET /api/tags/suggestions?prefix=wor`
- [ ] Frontend: tag chip UI on the todo row + filter pills above the timeline

## Open questions

- Whether to keep system categories as-is alongside tags, or fold categories into tags as "pinned" tags. Leaning keep-both for v1 — categories serve a different mental model (a todo has ONE category, MANY tags).
- Tag rename UX. If a user renames `#work` → `#office`, do we update every existing todo? Or treat them as independent? Probably independent — too easy to break things otherwise.

No implementation work started.
