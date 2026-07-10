# Agent Guide

Instructions for any AI coding agent (Claude Code, Cursor, Copilot Workspace, etc.) working in this repository. Read this file first, every session.

## 1. Read Order

Before writing any code in a new session:
1. `context/project-overview.md` — what phase are we in, what's actually in scope
2. `context/workflow.md` §5 — confirm the requested task belongs to the current phase
3. `context/architecture.md` + `context/database-schema.md` — relevant module boundaries
4. `context/api-design.md` and `context/code-standard.md` — conventions to follow
5. Only then look at existing code in the relevant module folder

## 2. Hard Rules

- **Never build a feature outside the current phase's scope** (per `workflow.md`) without the user explicitly overriding this. If asked for something from a later phase, say so and ask whether to fast-track it or stick to the roadmap.
- **Never touch Alembic migrations that have already been applied** to a shared environment. New schema changes = new migration (`alembic revision`).
- **Never bypass the repository pattern** — no direct SQLAlchemy session queries from FastAPI routers or frontend JS.
- **Never invent a payment/payout code path that skips the `WalletTransaction` ledger or idempotency key.** This is the highest-risk part of the system.
- **Never mark a task done without the tests required by `code-standard.md` §4.**
- **Continue from existing work, don't rewrite it.** If a module already has a working implementation, extend it; don't regenerate the whole file unless refactoring is the explicit task.
- **Update the relevant `context/*.md` file in the same PR** if you change architecture, schema, or API contracts — these docs must stay accurate, not aspirational.

## 3. When Requirements Are Ambiguous

- Check `database-schema.md` and `api-design.md` first — many "ambiguous" questions are already answered there.
- If genuinely unresolved (e.g., a business rule like "how long before an order auto-cancels if the seller doesn't respond"), pick a reasonable default, implement it, and flag the assumption explicitly in the PR description / response rather than blocking on it.
- Do not silently expand scope to "while I'm here" build adjacent features.

## 4. Task Sizing

- Prefer completing one module's vertical slice (domain → application → infrastructure → interface → tests) over touching many modules shallowly.
- For a new endpoint: Pydantic schema → application service method → repository method (if new) → FastAPI router → tests → OpenAPI doc (automatic from type hints, no extra work) → done. Don't stop at "router returns mock data."

## 5. Working With the Event Bus

- When a use-case in one module needs something to happen in another module (e.g., order paid → trigger payout logic), emit a domain event; do not import the other module's service directly. Check `architecture.md` §4 for the canonical event flow before adding a new event type.

## 6. Verifying Your Own Work

Before declaring a task complete, self-check:
- [ ] Does this match an existing pattern elsewhere in the codebase, or did I introduce a new one unnecessarily?
- [ ] Are all inputs validated (Pydantic schema) and all outputs role/ownership-checked?
- [ ] If money or delivery state changed, is it inside a SQLAlchemy transaction and event-logged?
- [ ] Did I add/update tests, and do they actually fail if the logic is wrong (not just assert a truthy value)?
- [ ] Did I avoid introducing a new library/pattern not already listed in `architecture.md` without flagging it?
- [ ] If I touched an asset upload path, did it go through the shared Cloudinary client wrapper rather than calling the SDK inline?

## 7. Communication Style Expected From the Agent

- State assumptions made, briefly, rather than asking many clarifying questions for a well-specified task.
- When a request conflicts with the roadmap or an architectural decision in these docs, say so plainly before proceeding, rather than quietly complying or quietly refusing.
- Prefer shipping a complete vertical slice over a wide, half-finished surface.
