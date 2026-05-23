# Real-time sync across devices via WebSockets

**Status:** In progress

## Problem

Today the app polls `GET /api/todos?since=<cursor>` every 30 seconds when the tab is focused. That's wasteful (95% of polls return zero changes), and the 30-second lag is visible — users on phone + laptop see noticeable delay between checking a todo on one and seeing the strikethrough on the other.

## Solution

Add a WebSocket endpoint that pushes mutations to all of a user's connected sessions in real time:

```
client → connects to wss://api.todoapp.example/v1/sync?token=<jwt>
client ← server pushes { type: "todo.updated", todo: {...} } on every mutation by ANY of the user's sessions
```

The polling code stays as a fallback for clients on flaky networks or in restricted environments where WebSockets are blocked.

Connection lifecycle:

- Auth via the same JWT used for REST calls
- Heartbeat ping every 30s; client reconnects on missed pongs
- Server-side: each mutation publishes to a per-user Redis pub/sub channel that all connected sessions subscribe to

## Implementation

- [x] WebSocket endpoint scaffolding + JWT auth — [#89](https://example.com/pull/89)
- [x] Redis pub/sub fan-out — [#91](https://example.com/pull/91)
- [ ] Frontend WebSocket client + reconnect logic
- [ ] Selective polling fallback when WebSocket unavailable for 60s+
- [ ] Telemetry: connection success rate, message-delivery latency

## Open questions

- How to gracefully degrade when a user has 10+ open sessions (multiple devices, browser tabs). Likely fine for now; revisit if we see real users with that pattern.
- Whether to push the full todo object on every change or just the IDs (clients refetch). Leaning push-full for v1 to avoid the second round trip.
