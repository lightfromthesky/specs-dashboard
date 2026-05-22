# Calendar integration (iCal export + Google Calendar sync)

**Status:** Draft

## Problem

Users who live in Google Calendar / Apple Calendar / Outlook want their todos with due dates to show up alongside their meetings. Today they have to set a separate phone reminder for every due date — annoying enough that several have asked for this.

## Solution (proposal)

Two phases:

### Phase 1 — one-way iCal export (read-only feed)

Each user gets a private iCal URL: `https://api.todoapp.example/cal/<user_id>/<token>.ics`. Calendar apps subscribe to it; the server returns a VEVENT per todo-with-due-date:

```
BEGIN:VEVENT
UID:todo-<id>@todoapp.example
DTSTART;VALUE=DATE:<due_date>
SUMMARY:<title>
DESCRIPTION:<body — first 200 chars>
END:VEVENT
```

Calendar apps poll the URL on their own cadence (Apple is ~hourly, Google is ~daily). Read-only, no API integration with the calendar provider needed.

### Phase 2 — two-way Google Calendar sync (OAuth-based)

User connects their Google Calendar via OAuth. Todos with due dates become Calendar events; checking off the calendar event marks the todo done. Bigger surface — OAuth token refresh, conflict resolution, webhook handling.

## Implementation

- [ ] Phase 1: token-signed iCal endpoint + RFC 5545-compliant VEVENT generation
- [ ] Phase 1: Settings page with "Subscribe to calendar" button (copies the user's iCal URL)
- [ ] Phase 1: integration tests against the iCal validator
- [ ] Phase 2: Google OAuth app + token refresh handling (deferred until Phase 1 ships and we see uptake)

## Open questions

- Should completed todos disappear from the calendar feed or stay as past-dated events? Lean disappear — calendar should reflect "what's still pending."
- Subscription URL leakage. The token is per-user and revocable from Settings. Audit logs if a token is rotated.

Phase 1 is small (~3 days of work). Not started — waiting on a clear "yes, build this" signal from a few more user requests.
