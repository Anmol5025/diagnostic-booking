# Diagnostic Booking Service

A robust backend service for diagnostic test bookings and simulated payments, built with FastAPI and PostgreSQL.

## Features

- **Authentication**: JWT-based signup and login.
- **Centres & Tests**: Manage diagnostic centres and the tests they offer, along with pricing.
- **Bookings**: Book an appointment for a specific test at a specific centre.
- **Payments**: Simulate payment processing (SUCCESS or FAILED) and update booking statuses.
- **Idempotent Webhooks**: Secure and reliable webhook processing for payment events.

## Tech Stack

- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (Async) with Alembic for migrations
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest with HTTPX and pytest-asyncio

## Database/Schema Design

The database is built on PostgreSQL with the following core entities:
1. **User**: Stores `id` (UUID), `email`, `hashed_password`, and `is_active`.
2. **DiagnosticCentre**: Stores `id`, `name`, and `location`.
3. **DiagnosticTest**: Stores `id`, `name`, and `description`.
4. **CentreTest**: A Many-to-Many association table linking a `DiagnosticCentre` and a `DiagnosticTest`. It also stores the specific `price` of the test at that centre and an `is_available` flag.
5. **Booking**: Stores the appointment information. Contains foreign keys to `user_id`, `centre_id`, and `test_id`. Tracks `appointment_time`, `amount`, `status` (Enum: PENDING, CONFIRMED, FAILED, CANCELLED), and a unique `payment_reference` used for webhook idempotency.

## Setup & Running Locally

The easiest way to run the service is using Docker Compose.

1. **Clone the repository** (if not already done).
2. **Build and start the containers**:
   ```bash
   docker compose up --build
   ```
   This will spin up a PostgreSQL database and the FastAPI backend. It also automatically applies Alembic migrations on startup.

3. **Access the API Documentation**:
   The Swagger UI is available at: [http://localhost:8000/docs](http://localhost:8000/docs)
   The ReDoc UI is available at: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

### Authentication
- `POST /auth/signup` - Register a new user
- `POST /auth/login` - Authenticate and get a JWT

### Diagnostic Centres & Tests
- `GET /centres/` - List diagnostic centres
- `POST /centres/` - Create a centre
- `GET /centres/{centre_id}` - Get centre details
- `GET /tests/` - List tests
- `POST /tests/` - Create a test
- `POST /centres/{centre_id}/tests/` - Link a test to a centre and set price
- `GET /centres/{centre_id}/tests/` - List tests for a centre

### Bookings (Requires Authentication)
- `POST /bookings/` - Create a booking
- `GET /bookings/` - List your bookings
- `GET /bookings/{booking_id}` - Get booking details
- `PATCH /bookings/{booking_id}/cancel` - Cancel a booking

### Payments
- `POST /payments/` - Simulate a payment processing for a booking
- `POST /payments/webhook/` - Idempotent webhook to receive external payment statuses

## Local Development (Without Docker)

If you prefer to run it locally without Docker:
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` or `.\venv\Scripts\activate` on Windows
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `alembic upgrade head` (ensure your `DATABASE_URL` is set correctly in `.env` to point to a running PostgreSQL instance)
5. Run the app: `uvicorn app.main:app --reload`

## Important Assumptions Made
- The simulation of payments is fully internal; in a real-world application, the `/payments/` endpoint would integrate with Stripe/Razorpay SDKs.
- The webhook endpoint `/payments/webhook/` is kept unauthenticated for simplicity of the simulation. In a real-world scenario, we would use HMAC signatures or IP whitelisting to secure it.
- A user can only access their own bookings.
- Appointments are stored using `datetime` but we assume the application passes UTC datetimes to maintain consistency.

## What I would improve with more time
- Add Redis caching for the centres and tests endpoints, as they change infrequently.
- Add Celery for sending confirmation emails/SMS to patients asynchronously after a booking is confirmed.
- Implement rate limiting (e.g., using `slowapi`) to protect the auth and webhook endpoints.
- Enhance the OpenAPI documentation with more examples and detailed descriptions of error codes.
- Implement more extensive integration tests using `pytest` and `TestClient` for all edge cases.
