# Mobile push notifications

**Status:** In progress

## Problem

Users on the mobile app don't see due-date reminders unless the app is open. Email reminders work but are easy to miss. The competitor apps push notifications and ours doesn't.

## Solution

iOS: APNs via Firebase Cloud Messaging. Android: FCM directly. Same code path on the server side — both abstracted behind `Notification.send(user_id, payload)`.

Notification types (v1):

| Trigger | Payload |
|---|---|
| Due date is "today" at the user's local 9am | "X todos due today: …" |
| A shared list (when collaborative-editing.md ships) gets a new item | "Y added 'foo' to Groceries" |
| 2FA login from a new device | "New login from <city>. Tap if this wasn't you." |

Token management:

- On app launch, mobile registers its device token with `POST /api/devices`
- Server stores `(user_id, device_token, platform)` rows
- Each notification is sent to every active device for that user
- Dead-token responses from FCM/APNs purge the row

## Implementation

- [x] Server: notification table + send abstraction — [#178](https://example.com/pull/178)
- [x] Device registration endpoint — [#180](https://example.com/pull/180)
- [x] iOS APNs integration via FCM — [#184](https://example.com/pull/184)
- [ ] Android FCM integration (in-flight, 70% complete)
- [ ] Due-date reminder scheduler (cron at user's local 9am)
- [ ] User-facing notification preferences (Settings → Notifications)
- [ ] Telemetry: send-rate, delivery-rate, click-through-rate per type

## Open questions

- Quiet hours respect. Should the 9am reminder be suppressed if the user is in their declared sleep hours? Leaning yes — adds a Settings field.
