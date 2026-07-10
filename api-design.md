# API Design

## 1. Conventions

- REST, resource-oriented, versioned in the URL: `/api/v1/...`
- JSON only. API uses **`snake_case`** in payloads (Pythonic, matches Pydantic model fields directly — no alias mapping layer needed since the frontend is plain JS, not a typed language expecting `camelCase`).
- Auth: `Authorization: Bearer <access_token>`. Refresh via `POST /api/v1/auth/refresh`.
- Pagination: cursor-based for feeds (`?cursor=...&limit=20`), offset-based acceptable for admin tables.
- Filtering: `?status=active&category=electronics`
- All list endpoints return:
```json
{ "data": [...], "meta": { "next_cursor": "...", "has_more": true } }
```

## 2. Error Format (uniform across the API)

```json
{
  "error": {
    "code": "ORDER_ALREADY_PAID",
    "message": "This order has already been paid for.",
    "status_code": 409,
    "details": {}
  }
}
```
- `code` is a stable machine-readable string the frontend JS can switch on; `message` is safe to show the user.
- Validation errors use `code: "VALIDATION_ERROR"` with `details.fields` listing per-field messages. FastAPI's default `RequestValidationError` is caught by a global exception handler and reshaped into this format — never returned in FastAPI's default shape.
- Never leak stack traces, SQL, or internal identifiers in production error responses (a custom exception handler replaces FastAPI's debug traceback with the uniform error body).

## 3. Core Endpoint Groups (Phase 1)

```
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
POST   /auth/verify-otp
POST   /auth/logout

GET    /users/me
PATCH  /users/me
GET    /users/me/addresses
POST   /users/me/addresses

POST   /shops                       (seller)
GET    /shops/:slug
PATCH  /shops/:id                   (owner only)

GET    /categories
POST   /products                    (seller)
GET    /products                    (public, filterable, search)
GET    /products/:id
PATCH  /products/:id                (owner only)
DELETE /products/:id                (owner only)
POST   /products/:id/images         (owner only — uploads directly to Cloudinary, stores returned secure_url + public_id)

GET    /cart
POST   /cart/items
PATCH  /cart/items/:id
DELETE /cart/items/:id

POST   /orders/checkout             creates Order + Payment intent
GET    /orders/:id
GET    /orders                      (customer's own, or seller's shop orders)
PATCH  /orders/:id/status           (seller: accept/reject/prepare)

POST   /deliveries/:order_id/request-rider   (seller)
POST   /deliveries/:id/accept                (rider)
PATCH  /deliveries/:id/status                (rider: picked-up, en-route, delivered)
POST   /deliveries/:id/confirm               (customer)
WS     /ws/delivery/:id                      (live location + status stream)

POST   /payments/webhooks/momo      (provider callback, signature-verified)
POST   /payments/webhooks/stripe    (provider callback, signature-verified)
GET    /wallet
GET    /wallet/transactions
POST   /wallet/withdraw             (seller/rider)

GET    /conversations
GET    /conversations/:id/messages
POST   /conversations/:id/messages  (also available via WS)

POST   /reviews
GET    /reviews?target_type=PRODUCT&target_id=...

GET    /admin/users
PATCH  /admin/users/:id/status
GET    /admin/orders
GET    /admin/disputes
GET    /admin/analytics/summary
```

## 4. WebSocket Namespaces (FastAPI native `WebSocket` routes)

- `/ws/chat/{conversation_id}` — join room per conversation, events: `message:new`, `typing`, `read`
- `/ws/delivery/{delivery_id}` — join room per delivery, events: `location:update`, `status:change`
- `/ws/notifications` — per-user room (identified via token on connect), event: `notification:new`

Rooms are implemented as an in-process `ConnectionManager` (dict of `id → set[WebSocket]`) for a single-instance deployment; if the app is ever scaled to multiple instances, connections are fanned out via a Redis pub/sub channel so all instances see all events.

## 5. Idempotency

All `POST` endpoints that create a payment, payout, or wallet transaction require an `Idempotency-Key` header. The server stores the key + response (in Postgres or Redis with a 24h TTL) and replays it on retry instead of re-executing.

## 6. Documentation

- OpenAPI spec is generated automatically by FastAPI from route type hints and Pydantic schemas — no extra decorators needed. Served at `/docs` (Swagger UI) and `/redoc` in non-production, with `/openapi.json` always available for the frontend team to reference when writing `fetch` calls.
- Since the frontend is plain JavaScript (not TypeScript), there is no generated-types package; instead, `frontend/assets/js/api/` contains small hand-written wrapper functions per resource (`getProducts()`, `createOrder()`, etc.) that document the expected shape in JSDoc comments, kept in sync manually against `/openapi.json` as the contract changes.
