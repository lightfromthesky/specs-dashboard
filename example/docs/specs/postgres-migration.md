# SQLite → Postgres migration

**Status:** Shipped 2026-03-22

## Problem

The TodoApp launched on SQLite for simplicity. Three issues now blocking growth:

- **No concurrent writes.** SQLite's whole-database lock makes the API single-threaded under write load. The sync endpoint locks up regularly under modest traffic.
- **No JSON operators.** Stored as text, queried with `LIKE '%foo%'`. Searching todo bodies is O(n).
- **No replication.** Backups are a `cp` of the file; no point-in-time recovery.

## Solution

Move to Postgres 16 on a managed provider (Fly.io's Postgres add-on). Schema is mechanical translation; the only model change is `TEXT` body columns becoming `JSONB` for richer querying.

Migration plan:

1. Ship Postgres-compatible queries behind a `DATABASE_URL` env var
2. Run the existing test suite against both backends in CI
3. Dump SQLite + load into Postgres in a maintenance window (~10 min for the current dataset)
4. Flip `DATABASE_URL` to Postgres + redeploy
5. Run for a week with SQLite kept warm as a fallback
6. Drop the SQLite path

## Implementation

- [x] Postgres-compat schema + migrations — [#42](https://example.com/pull/42)
- [x] CI matrix runs tests on both SQLite and Postgres — [#45](https://example.com/pull/45)
- [x] Maintenance-window cutover — completed 2026-03-22, 7-minute downtime
- [x] SQLite path removed two weeks post-cutover — [#52](https://example.com/pull/52)

## Risks & rollback

Maintenance-window dump-and-restore is the riskiest step. Rehearsed three times on staging. Rollback: revert `DATABASE_URL`, re-import any new writes from the brief Postgres window — accepted that step would require a few minutes of manual reconciliation.
