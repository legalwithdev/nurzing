# Going live (Rs. 0)

The site is static on Cloudflare Pages. Bookings are handled by two Pages Functions
in `functions/api/` and stored in Cloudflare D1. Everything here is on the free plan.

## 1. Create the database (once)

```
npx wrangler d1 create nurzing
```

Copy the `database_id` it prints into `wrangler.toml`.

Then create the tables:

```
npx wrangler d1 execute nurzing --file=db/schema.sql --remote
```

## 2. Bind D1 to the Pages project

Cloudflare dashboard -> Workers & Pages -> nurzing -> Settings -> Functions ->
D1 database bindings -> add: variable name `DB`, pick the `nurzing` database.
Redeploy after adding it.

## 3. Set two variables

Same screen, under Variables and Secrets:

- `WHATSAPP_NUMBER` - the number that should receive bookings, digits only, with country code (for example 9198XXXXXXXX)
- `ADMIN_KEY` - a long random string. This is the password for the bookings page.

## 4. Use it

- Customers book at `/book.html` - the request is saved and they get a WhatsApp button.
- You read them at `/admin-bookings.html` - paste the admin key, then call or message the customer.
- `POST /api/applications` accepts professional sign-ups.

## What works without D1

If the database is not bound yet, the form still works: it shows the WhatsApp button
so no request is lost. Nothing breaks, it just is not stored.

## Honest limits

- The admin page is protected by a single shared key, not real accounts.
- The per-IP throttle is best-effort: Cloudflare isolates do not share memory.
- There is no SMS: WhatsApp is the free delivery channel.
- Payments are not wired here. Use Razorpay payment links until the Python backend is deployed.
