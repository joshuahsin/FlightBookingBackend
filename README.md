# Flight Buddy — Backend

REST API backend for a flight booking application built with Django REST Framework. Stripe is implemented for easy payment services, JWT secures the application, and Redis caches large results supporting the PostGreSQL database. The Frontend of the application is constructed using React.js.

With this application, Users can book flights for themselves and others, looking up round trip or one way flights between a period of time, select seats, select passengers, and complete their payment with Stripe. Additionally, signed in users can view their orders or users without accounts an use their order confirmation to view past flight orders. 

## Frontend
https://github.com/joshuahsin/flight-booking-app-frontend

## Tech Stack

- **Django 4.2** + Django REST Framework
- **PostgreSQL** — primary database
- **Redis** — response caching
- **Stripe** — payment processing and refunds
- **JWT** (SimpleJWT) — authentication
- **pytest** — test suite

## Features

- Email verification signup flow with 24-hour expiring tokens
- Role-based access control (user / admin)
- Flight and seat browsing by route
- Cart for selecting departure and return flights
- Order creation with auto-generated confirmation numbers
- Stripe payment integration with webhook handling
- Booking lifecycle: pending → confirmed → checked-in → boarded
- Order and booking cancellation
- Admin-managed refund requests with full and partial Stripe refunds
- Guest order lookup by confirmation number + last name
- Redis caching on order, booking, and payment list endpoints

## Setup

**Prerequisites:** Python 3.9+, PostgreSQL, Redis (optional — falls back to in-memory cache)

```bash
# 1. Clone and create virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your database credentials, Stripe keys, and email settings

# 4. Run migrations and seed data
python manage.py migrate
python manage.py seed_data

# 5. Start the server
python manage.py runserver
```

## Environment Variables

See [.env.example](.env.example) for the full list. Required variables:

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DB_PASSWORD` | PostgreSQL password |
| `STRIPE_SECRET_KEY` | Stripe secret key (`sk_test_...`) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret (`whsec_...`) |

## API Overview

| Resource | Endpoint |
|---|---|
| Auth | `POST /api/users/start_signup/`, `GET /api/users/verify_email/`, `POST /api/token/`, `POST /api/token/refresh/` |
| Flights | `GET /api/flight/` |
| Cart | `GET /POST /api/cart/` |
| Orders | `GET /POST /api/order/`, `POST /api/order/{id}/cancel/` |
| Bookings | `GET /api/booking/`, `POST /api/booking/{id}/check_in/`, `POST /api/booking/{id}/board/` |
| Payments | `POST /api/payment/`, `POST /api/payment/webhook/` |
| Refunds | `POST /api/refund-request/`, `POST /api/refund-request/{id}/approve/` |
| Guest lookup | `GET /api/order/lookup/?confirmation_number=&last_name=` |

## Running Tests

```bash
pytest
```
