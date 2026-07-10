# UI / Content Guidelines

## 1. Design Principles

- Clean, minimal, high information density done well (think: Amazon's clarity, not Amazon's clutter)
- One primary action per screen; secondary actions visually de-emphasized
- Mobile-first layout, since most target users (per the delivery/marketplace context) are on phones
- Dark mode is a token-swap, not a separate design — build with CSS custom properties from day one (`--color-surface`, etc., re-mapped under `[data-theme="dark"]`)

## 2. Design Tokens (starting point, refine visually before build)

Defined as plain CSS custom properties in `assets/css/tokens.css` (no Tailwind config — this is a hand-rolled, small token set kept intentionally simple):

- Font: Inter (UI), a rounded sans for marketing/onboarding headlines — loaded via a font-hosting `<link>` or self-hosted `.woff2`
- Color roles (not literal hexes — define per brand): `--color-primary`, `--color-primary-foreground`, `--color-surface`, `--color-surface-muted`, `--color-border`, `--color-success`, `--color-warning`, `--color-danger`, `--color-info`
- Spacing scale: `--space-1` through `--space-8` on a 4px base (e.g. `--space-1: 4px; --space-2: 8px; ...`)
- Radius: consistent single scale (`--radius-sm/md/lg`), used consistently — no ad hoc one-off radius values
- Elevation: 2–3 `--shadow-sm/md/lg` levels max; avoid heavy drop shadows

## 3. Screen Inventory (Phase 1)

Each screen below is a standalone `.html` file under `frontend/public/` (see `file-structure.md`), progressively enhanced by its matching page script in `assets/js/pages/`.

**Public / Customer**
- Landing / marketplace home (featured shops, categories)
- Product listing (search + filters)
- Product detail
- Shop page
- Cart
- Checkout (address → payment → confirm)
- Order detail / live tracking
- Chat inbox + conversation
- Profile & addresses
- Auth: login, register, OTP verify, forgot password

**Seller**
- Onboarding (create shop, verification upload)
- Product management (list, create/edit, stock)
- Orders queue (accept/reject/prepare/request rider)
- Earnings/wallet
- Shop analytics (basic: sales over time, top products)

**Rider**
- Online/offline toggle
- Incoming delivery request (accept/reject, countdown timer)
- Active delivery (map, status buttons, chat/call customer)
- Earnings/wallet, withdrawal

**Admin**
- Users table (filter by role/status, suspend)
- Orders table (filter by status, drill into detail)
- Disputes queue
- Revenue/analytics summary
- Shop verification queue

## 4. Content / Copy Tone

- Direct and plain. "Your order is on its way" not "Your delightful package is en route to you!"
- Errors tell the user what to do next, not just what went wrong: "This email is already registered. Try logging in instead." not "Error: duplicate email."
- Empty states always include a next action ("No products yet — add your first product")
- Currency and numbers always formatted per locale (support at minimum the currency of Phase 1 launch market) — use the native `Intl.NumberFormat`/`Intl.DateTimeFormat` browser APIs rather than a formatting library, since the frontend has no package/build step

## 5. Accessibility Baseline

- All interactive elements keyboard-reachable, visible focus states (don't strip the browser's default `:focus-visible` outline without replacing it)
- Color is never the only signal (status also uses icon/text, e.g. order status)
- Minimum contrast ratio AA (4.5:1 body text)
- All images have alt text (product images: product title as fallback)
- Use semantic HTML first (`<button>`, `<nav>`, `<main>`, `<label>`) — with no framework enforcing this, accessibility depends entirely on writing correct markup by hand

## 6. Componentization

Since there's no component framework, "components" are small, reusable building blocks implemented as either:
1. **HTML partials** — small `.html` snippets (e.g. a product card) inserted via a tiny include step or JS template, reused across pages, or
2. **JS DOM-builder functions** — a function like `renderProductCard(product)` in `assets/js/components/productCard.js` that returns a DOM node/HTML string, so markup isn't hand-duplicated across pages

Shared visual primitives (buttons, inputs, dialogs/modals, cards, badges, tables, tabs) are defined once as CSS classes in `assets/css/components/` (`.btn`, `.card`, `.badge`, etc.) plus, where they need behavior (a modal opening/closing, a tab switching), a matching small JS helper in `assets/js/components/`. Domain components (`productCard`, `orderStatusBadge`, `deliveryMap`, `chatBubble`, `ratingStars`) compose these primitives — never reimplement a primitive's styling inline on a page.
