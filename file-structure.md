# File Structure

Simple monorepo (no workspace tooling like pnpm/Turborepo needed — the backend is a single Python project and the frontend has no build step).

```
ecosystem/
├── context/                        # this documentation folder
│   ├── project-overview.md
│   ├── architecture.md
│   ├── database-schema.md
│   ├── api-design.md
│   ├── file-structure.md
│   ├── code-standard.md
│   ├── ui-content.md
│   ├── security.md
│   ├── workflow.md
│   └── agent-guide.md
│
├── apps/
│   ├── backend/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── auth/
│   │   │   │   ├── domain/
│   │   │   │   ├── application/
│   │   │   │   ├── infrastructure/
│   │   │   │   │   ├── models.py
│   │   │   │   │   └── repository.py
│   │   │   │   └── interface/
│   │   │   │       ├── router.py
│   │   │   │       └── schemas.py
│   │   │   ├── users/
│   │   │   ├── catalog/
│   │   │   │   ├── domain/
│   │   │   │   ├── application/
│   │   │   │   ├── infrastructure/
│   │   │   │   └── interface/
│   │   │   ├── orders/
│   │   │   ├── payments/
│   │   │   ├── delivery/
│   │   │   ├── chat/
│   │   │   │   └── websocket.py       # FastAPI WebSocket routes
│   │   │   ├── notifications/
│   │   │   ├── reviews/
│   │   │   ├── admin/
│   │   │   ├── events/
│   │   │   │   ├── event_bus.py
│   │   │   │   └── domain_events/
│   │   │   ├── common/
│   │   │   │   ├── dependencies.py     # get_current_user, require_role, etc.
│   │   │   │   ├── exceptions.py       # typed exception classes
│   │   │   │   ├── exception_handlers.py
│   │   │   │   └── middleware.py
│   │   │   ├── core/
│   │   │   │   ├── config.py           # Pydantic Settings, env validation
│   │   │   │   ├── database.py         # async SQLAlchemy session/engine
│   │   │   │   ├── security.py         # password hashing, JWT
│   │   │   │   └── cloudinary_client.py
│   │   │   └── main.py                 # FastAPI() app, router includes
│   │   ├── alembic/
│   │   │   ├── versions/
│   │   │   └── env.py
│   │   ├── alembic.ini
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── e2e/
│   │   ├── pyproject.toml              # deps + tool config (ruff, black, mypy, pytest)
│   │   ├── requirements.txt            # pinned, generated from pyproject/lockfile
│   │   ├── .env.example
│   │   └── Dockerfile
│   │
│   ├── frontend/                   # plain HTML/CSS/JS
│   │   ├── public/
│   │   │   ├── index.html
│   │   │   ├── shop/[slug].html        # or /shop/index.html?slug= if avoiding dynamic routing
│   │   │   ├── product/[id].html
│   │   │   ├── cart/index.html
│   │   │   ├── checkout/index.html
│   │   │   ├── orders/[id].html
│   │   │   ├── seller/dashboard.html
│   │   │   ├── rider/dashboard.html
│   │   │   ├── admin/dashboard.html
│   │   │   └── auth/ (login.html, register.html, verify-otp.html)
│   │   ├── assets/
│   │   │   ├── css/
│   │   │   │   ├── tokens.css          # CSS custom properties (design tokens)
│   │   │   │   ├── base.css
│   │   │   │   └── components/         # button.css, card.css, badge.css, etc.
│   │   │   ├── js/
│   │   │   │   ├── api/                # apiClient.js + one wrapper module per resource
│   │   │   │   ├── components/         # small reusable DOM builder functions / Web Components
│   │   │   │   ├── pages/               # one entry script per page, wired via <script type="module">
│   │   │   │   ├── state/              # tiny pub-sub or module-level store for cart/auth state
│   │   │   │   └── sockets/            # websocket client helpers (chat, delivery tracking)
│   │   │   └── images/                 # static/marketing images only (uploaded content lives in Cloudinary)
│   │   ├── Dockerfile                  # nginx (or simple static server) serving /public + /assets
│   │   └── package.json                # only if using a dev-only static server/linter; no bundler required
│   │
│   └── mobile/                     # Flutter app — Phase 2, scaffolded later
│
├── infra/
│   ├── docker-compose.yml           # local dev: postgres, redis, backend, frontend
│   ├── docker-compose.prod.yml
│   └── github-actions/              # reusable workflow fragments
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
└── README.md
```

## Naming Rules
- Folders: `kebab-case`
- Python files/modules: `snake_case.py`
- Python classes: `PascalCase`
- FastAPI routers: `router.py` per module, mounted in `main.py` with an `/api/v1` prefix
- SQLAlchemy models: `models.py`, one class per table, `PascalCase` class name / `snake_case` table name
- Tests mirror source path: `app/orders/application/checkout_service.py` → `tests/unit/orders/test_checkout_service.py`
- HTML pages: `kebab-case.html`, one file per screen (see `ui-content.md` §3 for the screen inventory)
- Frontend JS files: `camelCase.js` for modules/functions (matches JS convention, distinct from the Python backend's `snake_case`)
- CSS files: `kebab-case.css`
- DB migrations: Alembic auto-generates timestamped revision files (`xxxx_add_wallet_table.py`); never hand-edited after being applied to a shared env
