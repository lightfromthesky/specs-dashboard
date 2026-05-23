# iOS native app

**Status:** Planned

## Problem

Users have been asking for a real iOS app since launch. The PWA works but
suffers from the usual web-on-mobile issues: home-screen-icon flakiness,
no offline-first behavior, no haptic feedback, no share-sheet integration
with system apps (Reminders, Calendar, Files).

Last quarter's user survey put a native iOS app at the top of the wishlist
(53% of respondents). The team has committed to building it in Q3, after
the realtime-sync work lands (see `realtime-sync.md`).

## Solution

Native Swift app using:

- SwiftUI for the entire UI surface (matching the design system that landed
  with dark mode, plus a few iOS-specific affordances like swipe actions
  and pull-to-refresh).
- The existing REST API (no new endpoints; we deliberately kept the API
  contract clean enough to support multiple clients).
- A local SQLite cache via GRDB for offline-first reads + queued writes;
  syncs through the same `/api/todos/sync` cursor that the realtime-sync
  spec is shipping.
- App Store distribution; TestFlight beta first.

## Implementation

Sequenced after realtime-sync ships. Tentative milestones:

- Q3 W1-2: read-only client (lists, todos, mark-complete)
- Q3 W3-4: write path + offline queue
- Q3 W5-6: share extension + widgets
- Q3 W7: TestFlight beta with 50 invited users
- Q3 W8: App Store submission

No code committed yet. Spec is here so the team can refine the design while
realtime-sync is in flight.
