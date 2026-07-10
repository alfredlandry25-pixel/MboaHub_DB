# Code Standard

## 1. General

- Python 3.12+, type hints everywhere (`mypy --strict`), no untyped `def` without a `# TODO(reason)` comment
- `ruff` (lint) + `black` (format) enforced via pre-commit hook and CI — a PR with lint/format errors cannot merge
- No commented-out code in merged PRs; delete it, git history has it if needed
- Functions do one thing; if a function needs a comment to explain "and then it also...", split it

## 2. Backend (FastAPI)

- One router per module (`interface/router.py`); one Pydantic schema module per module (`interface/schemas.py`)
- Routers: thin — validate input (Pydantic request model, handled automatically by FastAPI), call one application service method, return a Pydantic response model
- Business logic lives in `application/*_service.py`, never in routers
- Repositories (`infrastructure/repository.py`) are the **only** place SQLAlchemy `select`/`insert`/`update` statements are written
- Every endpoint has a Pydantic request model with field validators — no endpoint accepts an unvalidated raw `dict` body
- All async operations that touch money or delivery state must be wrapped in a single SQLAlchemy transaction (`async with session.begin():`) where multiple tables change together
- Domain events are typed Pydantic models in `events/domain_events/`, never raw dicts or strings
- Errors: raise typed exception classes (`OrderAlreadyPaidException(ConflictException)`), never a bare `raise Exception("...")` in application code; a global exception handler (`common/exception_handlers.py`) converts these into the uniform error format from `api-design.md`
- Dependency injection via FastAPI's `Depends()` — current user, DB session, and role checks are all dependencies, not manually parsed in each route
- File uploads to Cloudinary go through a single `infrastructure/cloudinary_client.py` wrapper — routers/services never call the Cloudinary SDK directly

## 3. Frontend (HTML/CSS/JavaScript)

- No framework, no build step, no bundler required — plain ES modules loaded via `<script type="module" src="...">`
- One `<script>` entry point per page (`assets/js/pages/productDetail.js`, etc.); shared logic goes in `assets/js/components/` or `assets/js/api/`, never copy-pasted across pages
- Data fetching: all HTTP calls go through `assets/js/api/apiClient.js` (a thin `fetch` wrapper handling base URL, auth header, and error-format parsing) — no page calls `fetch()` directly
- Forms: native HTML5 validation attributes (`required`, `pattern`, `type=email`) as the first line of defense, plus a small JS validation helper before submit; server-side Pydantic validation is still the source of truth
- No inline styles (`style="..."` attributes); all styling in `assets/css/`, using CSS custom properties from `tokens.css` for colors/spacing/radius
- Keep page-entry JS files focused: if a file grows past ~150 lines, extract a `components/` helper
- Progressive rendering: pages are static HTML by default; JS enhances them (populates dynamic content, wires up interactivity) rather than fully client-rendering everything from an empty `<div id="root">`

## 4. Testing (required, not optional)

| Layer | Tool | Minimum bar |
|---|---|---|
| Backend unit | `pytest` | every application service, especially state machines (orders, delivery) |
| Backend integration | `pytest` + `testcontainers-python` (real Postgres) | every repository, every payment/payout path |
| Backend e2e | `pytest` + `httpx.AsyncClient` against the FastAPI app | happy path + key failure paths per module (auth, checkout, delivery lifecycle) |
| Frontend unit | plain JS test runner (e.g. `node --test` or Vitest run standalone, no framework needed) | pure logic functions (cart totals, validators) — skip DOM-heavy snapshot tests |
| Critical flow e2e | Playwright | register → browse → buy → deliver → pay-out, run in CI on every PR to `main` |

- No PR touching `payments/`, `orders/`, or `delivery/` merges without tests covering the changed behavior.
- Coverage is a signal, not a target — 100% coverage on trivial getters is not the goal; coverage on state machines and money paths is.

## 5. Git Commit Style

Conventional Commits: `feat(orders): add checkout idempotency key`, `fix(delivery): correct ETA calc`, `chore:`, `docs:`, `test:`. Enforced by commitlint.

## 6. Security-Adjacent Code Rules

(Full checklist in `security.md`; the coding-time rules are:)
- Never log full request bodies for auth/payment endpoints (redact tokens, card data, phone/email where not needed)
- Never construct raw SQL with string interpolation of user input — use SQLAlchemy's parameterized `select()`/`text()` bindparams if raw SQL is ever unavoidable
- All file uploads validated by MIME type + size limit server-side (before the Cloudinary upload call), not just client-side
- Secrets only via environment variables (loaded through `core/config.py`'s Pydantic `Settings`), never committed; `.env.example` kept up to date with no real values
