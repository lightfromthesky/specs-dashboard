# User registration with email verification

**Status:** Shipped 2026-02-14

## Problem

The TodoApp launched with anonymous, browser-local storage. Synced multi-device usage requires accounts. We need a sign-up flow that's fast (email + password, no friction), verifies the email exists (so we can recover accounts later), and resists spam-bot signups.

## Solution

Standard email-verification flow:

1. User submits `{ email, password }` to `POST /api/auth/register`
2. Server creates a `users` row with `verified_at: NULL` and emails a one-time link
3. User clicks the link → `GET /api/auth/verify?token=…` → server sets `verified_at` and redirects to the app
4. Unverified accounts can browse a sandbox view but can't sync across devices

The token is a 32-byte random value stored hashed in `email_verification_tokens`, expires after 24 hours.

## Implementation

- [x] Migration: `users` + `email_verification_tokens` tables — [#12](https://example.com/pull/12)
- [x] Register + verify endpoints — [#15](https://example.com/pull/15)
- [x] Email template + Postmark integration — [#16](https://example.com/pull/16)
- [x] Frontend signup form + verification landing page — [#18](https://example.com/pull/18)

## Risks & rollback

Postmark outages block new registrations. Mitigation: queue emails locally and retry with exponential backoff (handled by Sidekiq). Existing users are unaffected. Rollback is a feature-flag flip (registration disabled, sign-in still works).
