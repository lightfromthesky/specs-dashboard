# Full-text search across todos

**Status:** In progress

## Problem

The current search box only matches todo titles — substring `LIKE '%foo%'`. Users have hundreds of todos accumulated over months; finding "that thing I wrote about the dentist last spring" requires scrolling timeline-style.

Bodies are searched today, but slowly: every body is `TEXT`, queried with `LIKE`, full table scan. On the median account it's fast enough; on heavy users (5000+ todos) it takes 1.5–3 seconds.

## Solution

Postgres full-text search. Add a `search_tsv tsvector` column derived from `title || ' ' || body`, with a GIN index. Search endpoint accepts a free-text query, returns ranked results.

```sql
ALTER TABLE todos ADD COLUMN search_tsv tsvector
  GENERATED ALWAYS AS (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, ''))) STORED;
CREATE INDEX todos_search_idx ON todos USING GIN(search_tsv);
```

API:

- `GET /api/todos/search?q=dentist+spring` → `to_tsquery`, rank by `ts_rank` × recency boost
- Returns 50 results, paginated

Frontend: replace the title-only filter with a unified search box that hits this endpoint after a 200ms debounce.

## Implementation

- [x] Migration + GIN index — [#161](https://example.com/pull/161)
- [x] `/api/todos/search` endpoint with ranking — [#164](https://example.com/pull/164)
- [ ] Frontend debounced search input + result rendering
- [ ] Highlighted matches in the result list (server-side `ts_headline`)
- [ ] Search analytics — log queries (no PII) to find common patterns we should pre-index

## Open questions

- Whether to support per-language stemming (some users mix Spanish/English in todos). `to_tsvector('simple', …)` avoids stemming entirely. Will pick after looking at the query log post-launch.
