# Reminder emails for due todos

**Status:** Planned

## Problem

Todos with `due_date` set (shipped in `due-date-field.md`) currently have no
notification path. Users who don't open the app daily miss deadlines. The
in-app reminder is useless if the app isn't open.

Push notifications are tracked separately in `push-notifications.md` (still
in progress) and only work on mobile. We want a cross-channel reminder that
works regardless of device: email.

## Solution

A daily cron job at 08:00 in the user's timezone (we already store it from
the user-registration flow) that:

1. Queries todos with `due_date` in the next 24h that haven't been marked
   complete, grouped by user.
2. Renders an HTML email (one per user) listing the todos with deep links
   back into the app.
3. Sends via Postmark (already used for password reset + welcome emails).
4. Respects an `email_reminders_enabled` setting per user, defaulting on,
   with a one-click unsubscribe in the email footer.

## Implementation

Decided last sprint planning. Slotted for the sprint after `full-text-search`
ships. Estimated effort: ~3 days (mostly templating + per-user-timezone job
scheduling; the data query is trivial).

No code committed yet.
