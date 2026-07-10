# Database Schema (Phase 1)

PostgreSQL, managed via **SQLAlchemy 2.0 (async ORM)** with **Alembic** for migrations. This covers MVP entities only; Job Portal entities are listed at the bottom as a forward-compatible placeholder (not built in Phase 1).

Table and column names are `snake_case` (Postgres/Python convention). Any field that stores an uploaded asset (avatar, logo, product image, chat attachment, verification doc) stores **two** columns: a `*_url` (Cloudinary `secure_url`, safe to render directly) and a `*_public_id` (Cloudinary `public_id`, needed for deletion/transformation later).

## Core Entities

```
User
  id, email, phone, password_hash, full_name
  avatar_url, avatar_public_id
  status (active | suspended | pending_verification)
  email_verified_at, phone_verified_at
  created_at, updated_at

Role            → enum: CUSTOMER, SELLER, RIDER, ADMIN, (EMPLOYER, JOB_SEEKER - phase 2)
UserRole        → join table (user_id, role)  [a user can hold multiple roles]

Shop
  id, owner_id (→User), name, slug, description
  logo_url, logo_public_id
  verification_status (pending | verified | rejected)
  created_at, updated_at

Category
  id, name, slug, parent_id (self-relation → subcategories)

Product
  id, shop_id (→Shop), category_id (→Category)
  title, slug, description, price_cents, currency
  stock_quantity, sku
  status (draft | active | out_of_stock | archived)
  created_at, updated_at

ProductImage
  id, product_id, url, public_id, position

Cart / CartItem
  Cart: id, user_id
  CartItem: id, cart_id, product_id, quantity, unit_price_cents_snapshot

Order
  id, customer_id (→User), shop_id (→Shop)
  status: PENDING_PAYMENT | PAID | PREPARING | RIDER_REQUESTED | RIDER_ASSIGNED
          | EN_ROUTE_TO_SELLER | PICKED_UP | EN_ROUTE_TO_CUSTOMER
          | DELIVERED | CONFIRMED | CANCELLED | DISPUTED
  subtotal_cents, delivery_fee_cents, total_cents, currency
  delivery_address_id (→Address)
  created_at, updated_at

OrderItem
  id, order_id, product_id, quantity, unit_price_cents_snapshot

Address
  id, user_id, label, line1, line2, city, country, lat, lng

Delivery
  id, order_id (1:1), rider_id (→User, nullable until assigned)
  status: mirrors relevant Order statuses for delivery leg
  pickup_lat/lng, dropoff_lat/lng
  requested_at, accepted_at, picked_up_at, delivered_at, confirmed_at

RiderLocation (high-write, consider Redis + periodic Postgres snapshot)
  rider_id, lat, lng, updated_at

Wallet
  id, user_id (1:1), balance_cents, currency

WalletTransaction
  id, wallet_id, type (CREDIT | DEBIT), amount_cents
  reference_type (ORDER | PAYOUT | REFUND | TOPUP)
  reference_id, status (PENDING | COMPLETED | FAILED)
  idempotency_key (unique)
  created_at

Payment
  id, order_id, provider (MOMO | STRIPE), provider_reference
  amount_cents, status (INITIATED | SUCCEEDED | FAILED | REFUNDED)
  raw_webhook_payload (jsonb, for audit)
  created_at

Payout
  id, recipient_id (→User: seller or rider), amount_cents
  status (PENDING | PROCESSING | PAID | FAILED)
  created_at, paid_at

Conversation
  id, type (BUYER_SELLER | RIDER_CUSTOMER | ADMIN_SUPPORT)
  participant_ids (join table conversation_participant)

Message
  id, conversation_id, sender_id, content
  attachment_url, attachment_public_id, type (TEXT|IMAGE)
  read_by (join table message_read), created_at

Review
  id, author_id, target_type (PRODUCT | SHOP | RIDER)
  target_id, rating (1-5), comment, created_at

Notification
  id, user_id, type, title, body, data (jsonb), read_at, created_at

AuditLog
  id, actor_id, action, entity_type, entity_id, metadata (jsonb), created_at
```

## Relationships Summary
- `User` 1—N `UserRole` (multi-role support from day one, even though Phase 1 UI only exposes 4 roles)
- `Shop` 1—N `Product`, `User(owner)` 1—1 `Shop` (a seller has one shop in Phase 1; multi-shop-per-seller deferred)
- `Order` 1—1 `Delivery`, `Order` 1—N `OrderItem`
- `User` 1—1 `Wallet`, `Wallet` 1—N `WalletTransaction`
- Every money-moving table (`WalletTransaction`, `Payment`, `Payout`) has an `idempotency_key` or `provider_reference` unique constraint — this is non-negotiable given the escrow/payout flow.

## Indexing Notes
- `Product`: index on `(shop_id, status)`, GIN index on `to_tsvector(title || description)` for search
- `Order`: index on `(customer_id, status)`, `(shop_id, status)`
- `RiderLocation`: kept hot in Redis (geo set) for matching; Postgres row is just an audit snapshot, not queried for live matching
- `Message`: index on `(conversation_id, created_at)`

## Job Portal Entities (Phase 2 — documented now, not built now)
`Company`, `JobPosting`, `Application`, `Resume`, `Interview` — designed later once Phase 1 ships, but `UserRole` already reserves `EMPLOYER`/`JOB_SEEKER` so the auth/role system doesn't need rework. `Resume` will store its file the same way as other assets (`resume_url`/`resume_public_id` via Cloudinary raw upload).

## ORM / Migration Notes
- Each module owns a `models.py` (SQLAlchemy declarative models) and a `repository.py` (all queries for that module's tables) under its `infrastructure/` folder.
- `Base.metadata` is assembled from all modules' models at app startup so Alembic autogeneration can diff against the full schema.
- Alembic Migration Strategy: one migration per PR, reviewed like code, generated with `alembic revision --autogenerate` then hand-checked (autogenerate misses some constraint/enum changes and index renames).
- No destructive migration (`DROP COLUMN`, etc.) ships without a backward-compatible deploy step first (expand → migrate → contract).
- Never hand-edit a migration file that has already been applied to a shared environment (staging/production) — write a new migration instead.
