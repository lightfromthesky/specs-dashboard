# Bulk import from CSV

**Status:** Shipped 2025-11-12

## Problem

New users migrating from other todo apps (Todoist, TickTick, Things) consistently bounce when they realize they'd have to re-enter every existing todo by hand. Onboarding friction is the #1 reason for sign-up-without-second-visit churn (analytics: 41% of new accounts never add a second todo).

## Solution

A CSV import flow accessible from Settings → Data → Import:

1. User uploads a CSV
2. Frontend previews the first 10 rows + lets the user map columns to fields (title, body, due_date, completed, category)
3. Server validates the full file, returns `{ valid_rows: N, errors: [{row, message}] }`
4. User clicks Confirm → server creates todos in a transaction
5. On success, user sees their newly-imported todos appear in the timeline

Import is idempotent on a per-file basis: the same CSV uploaded twice creates each todo once (deduped on `(user_id, title, body, due_date)` hash).

## Implementation

- [x] Backend: `POST /api/import/csv` accepting multipart upload — [#7](https://example.com/pull/7)
- [x] CSV parsing + column mapping endpoint — [#9](https://example.com/pull/9)
- [x] Transactional batch insert with dedup — [#11](https://example.com/pull/11)
- [x] Frontend upload + preview + mapping UI — [#13](https://example.com/pull/13)
- [x] Pre-canned column mappings for Todoist / TickTick / Things export formats — [#17](https://example.com/pull/17)

## Risks & rollback

Large CSVs (10K+ rows) could OOM the server. Mitigation: 5MB upload limit + chunked processing. Rollback is a feature-flag flip.
