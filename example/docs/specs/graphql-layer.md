# GraphQL API layer

**Status:** Abandoned 2025-12-19

## Problem

(From the original 2025-09 draft.) The REST API has the typical over/under-fetch problems on the mobile client — the todos list endpoint returns 12 fields per row when the list view only renders 4. A GraphQL layer would let the client ask for exactly what it needs and stop the bandwidth waste.

## Solution (original proposal)

Stand up a GraphQL gateway in front of the existing REST controllers. Use [Mercurius](https://mercurius.dev/) (Node) since the backend is already Node + Fastify. Schema mirrors the REST resources; resolvers proxy to the existing controllers initially, then migrate to direct DB queries case-by-case.

## Implementation status

A spike PR ([#54](https://example.com/pull/54), closed-without-merge) stood up the gateway and exposed `query { todos { id title completed } }`. Worked fine in isolation.

## Why this is Abandoned

After the spike and a week of usage on the mobile client:

1. **Bandwidth wasn't actually the bottleneck.** Profiling showed the mobile client's slowness was due to a render-blocking JS bundle, not API payload size. Trimming the JSON shaved 12% off response body but didn't move user-perceived load time at all.
2. **Two API surfaces means double the auth, double the caching, double the test surface.** The cost of maintaining GraphQL + REST in parallel was real and ongoing.
3. **The escape hatch was simpler.** Adding `?fields=id,title,completed` to the REST endpoints (5 lines of serializer code) solved 90% of the over-fetch problem with zero new infrastructure.

Closing the spec as history. If we ever revisit (e.g., for a public partner API where typed schemas are a real win), this is the prior art.
