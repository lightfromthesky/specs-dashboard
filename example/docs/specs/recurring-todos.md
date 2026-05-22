# Recurring todos

**Status:** Shipped 2026-05-10

## Problem

Users routinely create the same todo repeatedly — "Pay rent" every month, "Water the plants" every Tuesday, "1-on-1 prep" every Friday. The natural request: let me create it once and have it auto-appear.

This was marked "out of scope" in the original `due-date-field.md` spec because the data model needed more thought. Returning to it now with a concrete design.

## Solution

Recurrence rules attached to a parent todo. When the parent is checked or its due date passes, the server materializes the next occurrence.

Data model:

```sql
ALTER TABLE todos ADD COLUMN recurrence_rule TEXT;
-- e.g. 'FREQ=WEEKLY;BYDAY=TU' or 'FREQ=MONTHLY;BYMONTHDAY=1'
-- Uses iCalendar RRULE syntax (RFC 5545)
ALTER TABLE todos ADD COLUMN recurrence_parent_id BIGINT REFERENCES todos(id);
```

When a recurring todo is completed:

1. Server marks the current todo `completed`
2. Server computes the next occurrence date from the RRULE + the completion time
3. Server inserts a new todo with the next date, copying body/category/etc., linked to the parent via `recurrence_parent_id`

Editing a recurring todo offers "Just this one" vs "All future occurrences" — same UX as Google Calendar.

## Implementation

- [x] Migration: add the two columns — [#138](https://example.com/pull/138)
- [x] RRULE parsing + next-occurrence calculation (using `node-rrule`) — [#141](https://example.com/pull/141)
- [x] Materialization on completion — [#144](https://example.com/pull/144)
- [x] Frontend: recurrence-rule picker UI (daily/weekly/monthly/custom) — [#147](https://example.com/pull/147)
- [x] "Just this one" vs "all future" edit flow — [#150](https://example.com/pull/150)
