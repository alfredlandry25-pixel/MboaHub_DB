# Workflow

## 1. Git Flow

- `main` — always deployable, protected, requires PR + passing CI + 1 review (or AI-agent self-review checklist if solo)
- `develop` — optional integration branch if working with more than one contributor; solo/small team can work directly off `main` with short-lived feature branches
- Branch naming: `feat/orders-checkout`, `fix/delivery-eta-bug`, `chore/update-deps`
- PRs are small and scoped to one module/concern where possible — a PR that touches `payments` and `ui-content` unrelatedly should be split

## 2. Definition of Done (applies to every ticket/task)

A task is not done until:
1. Code follows `code-standard.md`
2. Tests written per the testing table in `code-standard.md` and passing
3. No new lint (`ruff`), format (`black`), or type (`mypy`) errors
4. Relevant `context/*.md` file updated if the change alters architecture, schema, or API contract
5. Manually verified against the acceptance criteria in the ticket
6. Security-sensitive changes checked against `security.md` §10

## 3. CI Pipeline (GitHub Actions)

```
on: pull_request → main
  1. install (pip install -r requirements.txt, cached)
  2. lint (ruff) + format check (black --check) + typecheck (mypy)
  3. unit + integration tests (pytest; spin up Postgres/Redis via GitHub Actions `services:`)
  4. build (backend Docker image; frontend needs no build step, just a lint pass e.g. with a simple JS linter if desired)
  5. Playwright critical-path e2e (against an ephemeral docker-compose stack: backend + Postgres + Redis + static frontend server)

on: push → main
  1. all of the above
  2. build & push Docker images (tagged with commit SHA) — backend image (FastAPI + Uvicorn/Gunicorn) and frontend image (static file server, e.g. nginx)
  3. deploy to staging automatically
  4. deploy to production: manual approval gate
```

## 4. Environments

| Env | Purpose | Deploy trigger |
|---|---|---|
| local | dev via docker-compose (Postgres, Redis, backend on Uvicorn `--reload`, frontend on any static server) | manual |
| staging | pre-prod validation, uses test payment provider keys + a separate Cloudinary folder/preset | auto on merge to `main` |
| production | live | manual approval after staging smoke test |

## 5. Phased Roadmap

**Phase 0 — Foundations (this doc set + scaffolding)**
Repo setup, CI skeleton, auth module, empty modules for all Phase 1 domains, docker-compose local env (Postgres, Redis, FastAPI backend, static frontend).

**Phase 1 — MVP (see `project-overview.md` §3)**
Marketplace core loop + delivery + payments + chat + basic admin. Ships to real users.

**Phase 2 — Job Portal**
Company profiles, job postings, applications, resume upload (via Cloudinary raw upload), ATS-lite, saved jobs, employer↔applicant chat (reuses existing chat module).

**Phase 3 — Marketplace depth**
Coupons/discounts, flash sales, product variants, wishlist, compare, follow shops, digital products.

**Phase 4 — Payments breadth**
Orange Money, Flutterwave/Paystack, PayPal, bank transfer, split payments, refund automation.

**Phase 5 — AI & Search**
Meilisearch/Elasticsearch migration, product/job recommendations, resume matching, smart/voice search, auto-translation, chat assistant.

**Phase 6 — Scale & Native**
Flutter mobile app, GraphQL if needed, service extraction for payments/delivery, Kubernetes if traffic warrants it, video/voice calls, route optimization, geofencing, and — only if the vanilla-JS frontend starts limiting velocity — introduction of a frontend framework/build step.

Each phase only starts once the previous phase's Definition of Done is met across its features — this roadmap is the single source of truth for "what should I build next," overriding the full feature wishlist in the original brief.

## 6. Backlog Triage Rule

Any feature from the original brief not yet placed into a phase above gets added to the relevant phase's section in this file before work starts on it — nothing gets built ad hoc outside this roadmap.
