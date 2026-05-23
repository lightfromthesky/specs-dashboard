# Two-factor authentication (TOTP)

**Status:** Shipped 2026-04-28

## Problem

Email/password auth has the usual problems: credential stuffing from leaked breaches elsewhere, weak password choices, phishing. 2FA mitigates all three with one mechanism users already understand from other apps.

## Solution

TOTP-based 2FA — the standard `otpauth://` URL + 30-second 6-digit code. Compatible with Google Authenticator, 1Password, Authy, etc.

Enrollment flow:

1. User goes to Settings → Security → "Set up two-factor"
2. Server generates a 32-byte secret, encodes as an `otpauth://` URL, returns the QR code
3. User scans with their authenticator app
4. User enters the current 6-digit code to confirm
5. Server verifies, stores the secret encrypted with the per-user key, marks 2FA enabled
6. Recovery codes (8 single-use codes) generated and shown to the user (must be saved offline)

Login flow when 2FA is enabled:

1. Email + password as today → server returns `{ "status": "needs_2fa", "challenge_id": "..." }`
2. Client prompts for code → submits to `/api/auth/2fa/verify`
3. Server verifies the TOTP code → returns JWT pair

## Implementation

- [x] Migration: `users.totp_secret_encrypted` + `users.recovery_codes_encrypted` — [#102](https://example.com/pull/102)
- [x] Enrollment endpoint + QR generation — [#105](https://example.com/pull/105)
- [x] Login flow with challenge step — [#108](https://example.com/pull/108)
- [x] Recovery-code generation + single-use enforcement — [#110](https://example.com/pull/110)
- [x] Settings UI for enroll/disable/regenerate-codes — [#114](https://example.com/pull/114)

## Out of scope

WebAuthn / passkeys. Strongly preferred by some power users but adds infrastructure (attestation handling) we don't have. Likely a v2 effort.
