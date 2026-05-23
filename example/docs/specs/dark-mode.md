# Dark mode

**Status:** Closed 2026-01-08

## Problem

Users on the feedback form: "Why is the app blindingly white at 11pm." Fair point. The competitor that everyone defected from had dark mode; we don't.

## Solution

Detect `prefers-color-scheme: dark` on the OS level and swap to a dark palette. Add a manual override toggle in Settings for users whose OS preference doesn't match their app preference.

A minimum two-palette set:

- Light (current default)
- Dark — `#1a1a1a` background, `#e8e8e8` text, `#4a9eff` accent

## Implementation

- [x] Initial implementation — CSS variables + JS toggle + Settings UI — [#22](https://example.com/pull/22), commit `c8f9a2b`
- [x] **Reverted** — feature rolled back two weeks after launch — [#31](https://example.com/pull/31), commit `7d3e1f4`

## Why it was reverted

Two weeks of post-launch data:

- **Contrast bugs throughout the app.** The "completed" strikethrough on todos was nearly invisible in dark mode (light gray on dark gray, ~2.1:1 contrast — WCAG fails AA at 4.5:1). Reported by 14% of dark-mode users.
- **Color-coded categories broke.** The 8 category colors were tuned for white backgrounds; on dark, half of them looked like the same muddy red-brown.
- **Date-picker library hard-coded white.** The third-party date-picker doesn't respect CSS variables; opening it on dark mode was a jarring white flash.

The right fix is a full design pass on the dark palette + replacing the date-picker. That's bigger than the original spec scoped for. Closing this spec as history; a future "design-system v2" effort will pick the dark-mode work back up properly.
