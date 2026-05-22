# Add `due_date` field to todos

**Status:** Shipped 2026-04-05

## Problem

The most-requested feature on the feedback form (62 mentions in the last 90 days): due dates on individual todos. Currently users hack this by typing dates into the body ("Pay rent by April 5") which the app can't sort by or remind on.

## Solution

Add a `due_date: TIMESTAMPTZ NULL` column to `todos`. Frontend exposes a date-picker on each row. Backend supports:

- `GET /api/todos?due_before=YYYY-MM-DD`
- `GET /api/todos?overdue=true` (todos with `due_date < now()` and not completed)
- Sort by due date

A "Due Soon" smart list (next 7 days) appears on the home screen.

## Implementation

- [x] Migration: `ALTER TABLE todos ADD COLUMN due_date TIMESTAMPTZ` — [#68](https://example.com/pull/68)
- [x] API query params + serializer — [#71](https://example.com/pull/71)
- [x] Frontend date-picker on todo row — [#74](https://example.com/pull/74)
- [x] Home-screen "Due Soon" widget — [#77](https://example.com/pull/77)

## Out of scope

Recurring due dates ("every Tuesday"). Tracked separately as a future spec — the data model needs more thought.
