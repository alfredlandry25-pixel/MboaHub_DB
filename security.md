# Security

Mapped to the feature areas that actually need each control — not a generic checklist copy-paste.

## 1. Authentication & Session
- Passwords: `passlib` (bcrypt/argon2) hashed, never logged, never returned in any response
- JWT access token short-lived (15 min) via `python-jose`/`PyJWT`; refresh token longer-lived, rotated on use
- Since the frontend is plain JS with no server-rendering framework managing cookies, tokens are issued as JSON in the response body. The access token is kept in memory (a JS module-level variable) and the refresh token in an `httpOnly`+`secure` cookie set by the backend — **never** in `localStorage`, to limit XSS blast radius
- Phone OTP: rate-limited (max attempts + cooldown), OTP expires in 5 min, never logged in plaintext
- Account lockout / exponential backoff after repeated failed logins
- 2FA and OAuth (Google/Facebook/Apple) are Phase 2 — designed for in the `UserRole`/future `AuthProvider` schema, not blocking MVP

## 2. Authorization
- RBAC via a `require_role(...)` FastAPI dependency on every route that isn't explicitly public
- Ownership checks in the application layer (a seller can only edit their own products — role alone is not enough, must check resource ownership)
- Admin actions require the `ADMIN` role AND are all written to `AuditLog`

## 3. Input Handling
- Every endpoint has a Pydantic request model; unknown fields are rejected (`model_config = ConfigDict(extra="forbid")`) rather than silently dropped
- SQLAlchemy parameterizes queries by default — raw SQL is avoided; if ever required, only via parameterized `text()` with bound params, never string interpolation
- File uploads: server-side MIME + size validation (via `python-magic`/Pillow) **before** the file is forwarded to Cloudinary, served back via the Cloudinary `secure_url` (HTTPS, optionally signed/private delivery for sensitive docs like rider verification); malware scanning is Phase 2

## 4. Transport & Storage
- HTTPS everywhere (enforced at the load balancer/edge)
- Secrets in environment variables / secret manager (DB URL, JWT secret, Cloudinary API key+secret, MoMo/Stripe keys), never in source control
- PII (phone, email, address) encrypted at rest where the hosting provider supports column/volume encryption; access logged
- Database backups encrypted, tested restore process documented in `workflow.md`
- Cloudinary assets: verification documents and other sensitive uploads use Cloudinary's signed/private delivery mode rather than public URLs; product images and shop logos remain public (they're meant to be shown)

## 5. API Hardening
- Rate limiting (Redis-backed, per-IP and per-user, e.g. via `slowapi` or a custom FastAPI middleware) on: login, OTP request, checkout, chat message send
- CSRF protection for the refresh-token cookie flow (`SameSite=Strict` or a double-submit token, since it's the one cookie-based credential in an otherwise Bearer-token API)
- CORS locked to known frontend origins
- Standard security headers (via a middleware or `secure` headers lib): CSP, HSTS, X-Frame-Options, etc. — CSP matters more than usual here since the frontend is hand-written JS with no framework auto-escaping, so XSS discipline in templating/DOM insertion is part of this control too

## 6. Payments Specifically
- Webhook signature verification mandatory for MoMo and Stripe callbacks — reject anything unsigned/invalid
- Idempotency keys required on all payment-mutating requests (see `api-design.md`)
- No card data ever touches our servers directly (Stripe Elements/hosted fields only, loaded client-side in plain JS) — we are never in PCI scope beyond SAQ-A
- Wallet balance changes only via the `WalletTransaction` ledger — never a direct `UPDATE balance` — so balance is always derivable/auditable from transaction history

## 7. Fraud & Abuse (MVP-appropriate, not full ML)
- Basic velocity checks: flag accounts placing many orders in a short window for admin review
- Manual dispute queue reviewed by admin (`admin/disputes`) — automated fraud scoring is Phase 2+

## 8. Logging & Monitoring
- Structured logs (`structlog` or stdlib `logging` with a JSON formatter), PII-redacted, correlation ID per request (via middleware)
- Sentry for error tracking (backend + frontend JS)
- Login history and active sessions visible to the user under their profile (basic device/IP list) — full device management UI is Phase 2

## 9. Dependency & Infra
- `pip-audit`/`safety` and Dependabot (or Renovate) run in CI for Python dependencies
- Docker images built from minimal base images (`python:3.12-slim`), scanned in CI
- Principle of least privilege for cloud IAM roles (API service role cannot, e.g., delete the database) and for the Cloudinary API key scope

## 10. Definition of "secure enough to ship" for Phase 1
A feature is not done until: RBAC is enforced, inputs are validated, relevant actions are rate-limited if user-triggered and cheap to spam, and — for anything payment/wallet-related — an idempotency key and audit trail exist.
