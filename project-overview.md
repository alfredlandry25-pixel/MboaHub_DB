# Project Overview

## 1. What This Is

A unified platform combining three product lines under one account system and one wallet:

1. **Marketplace** — multi-vendor e-commerce (Amazon/Jumia-style)
2. **Jobs** — job board + applicant tracking (LinkedIn/Upwork-style)
3. **Delivery** — on-demand rider dispatch (Uber/Glovo-style), which also serves the Marketplace's fulfillment

These share: authentication, user profiles, wallet/payments, chat, notifications, search, and the admin dashboard.

Built on a deliberately small, dependency-light stack: **FastAPI (Python) + PostgreSQL** on the backend, **Cloudinary** for all media/object storage, and a **plain HTML/CSS/JavaScript** frontend with no framework or build step. See `architecture.md` for the full rationale and stack table.

## 2. The Honest Scoping Problem

The source brief describes three separate billion-dollar companies (Amazon, LinkedIn, Uber) merged into one app, built by one team, to enterprise standards, "not a simple CRUD project." That is a 2–4 year roadmap for a funded team of 15–30 engineers, not a single build.

This documentation set does **not** pretend otherwise. Instead it:
- Defines a **real, shippable MVP** (Phase 1) that proves the core loop end-to-end
- Designs the architecture so Phase 2/3 features (jobs portal, AI recommendations, video calls, auctions, etc.) can be added **without rewrites**
- Treats every "nice to have" in the original brief as a backlog item in `workflow.md`, not a v1 requirement

If you (or an AI agent) are ever unsure what to build next, the rule is: **check the MVP scope below before building anything from the full feature list.**

## 3. Phase 1 (MVP) Scope — what actually gets built first

**Goal:** A customer can browse products from multiple sellers, buy one, pay for it, and have a rider deliver it, with both sides tracking the order in real time.

Included:
- Auth (email/password + JWT, phone OTP verification)
- Roles: Customer, Seller, Rider, Admin (Employer/Job Seeker deferred to Phase 2)
- Seller: create shop, CRUD products (images uploaded to Cloudinary), view orders, accept/reject
- Customer: browse, search (Postgres full-text first, Meilisearch later), cart, checkout, order tracking
- Delivery: seller requests rider → nearest available rider notified → accept → status pipeline → delivered → auto payout
- Payments: one mobile money provider (MTN MoMo) + Stripe card payments; internal wallet ledger; manual/escrow-style release on delivery confirmation
- Chat: buyer↔seller and rider↔customer, text + images, via native WebSockets
- Notifications: in-app + push (FCM), order lifecycle events only
- Admin: user management, order oversight, dispute flag, basic revenue dashboard
- Reviews: product + seller + rider ratings only

Explicitly **excluded from Phase 1** (see `workflow.md` roadmap for when):
- Job portal (all of it)
- Auctions, flash sales, coupons, digital products
- Voice/video calls
- AI recommendations, resume matching, OCR, auto-translation
- Multiple payment providers beyond the two above
- Elasticsearch/Meilisearch (Postgres FTS is enough at MVP scale)
- Kubernetes (single Docker Compose / managed platform is enough at MVP scale)
- Native mobile apps (responsive web first; Flutter app is Phase 2)
- A frontend framework or build step (plain HTML/CSS/JS is enough at MVP scale — see `architecture.md` §7)

## 4. User Roles (Phase 1)

| Role | Core capability |
|---|---|
| Customer | browse, buy, pay, track, chat, review |
| Seller | list products, manage orders, request rider, get paid |
| Rider | go online, accept deliveries, navigate, get paid |
| Admin | oversee users/orders/payments/disputes |

Employer and Job Seeker roles are designed for in the data model (see `database-schema.md`) but their UI/API surface is Phase 2.

## 5. Success Criteria for MVP

- A seller can list a product and receive a paid order within 10 minutes of shop creation
- A customer can complete checkout-to-delivery in a single session without support intervention
- A rider can go online, accept, complete, and get paid without manual admin steps
- p95 API latency < 300ms at low load; system survives a basic load test of 500 concurrent users
- Zero plaintext secrets, all inputs validated, RBAC enforced on every endpoint

## 6. How the Rest of This Doc Set Fits Together

- `architecture.md` — system design, tech stack, service boundaries
- `database-schema.md` — entities, relationships, migration strategy
- `api-design.md` — REST conventions, versioning, error format
- `file-structure.md` — repo/folder layout
- `code-standard.md` — language/style/testing rules
- `ui-content.md` — design system, copy tone, screen inventory
- `security.md` — checklist mapped to features
- `workflow.md` — git flow, CI/CD, phased roadmap, Definition of Done
- `agent-guide.md` — rules for any AI coding agent (Claude Code, Cursor, etc.) working in this repo
