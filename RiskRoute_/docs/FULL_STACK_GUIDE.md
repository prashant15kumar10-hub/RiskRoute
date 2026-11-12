# Full-Stack Architecture

## Technology stack

| Layer | Technology | Responsibility |
| --- | --- | --- |
| Frontend | React + Vite | Authentication, shipment form, results, history and responsive UI |
| Backend | FastAPI | REST endpoints, request validation and application orchestration |
| ML service | scikit-learn | Delay-risk prediction and counterfactual generation |
| Database | SQLite | User accounts, sessions and simulation history |
| Application server | Uvicorn | Serves the API and production React build |

## Application flow

1. The user creates an account or signs in.
2. React sends shipment conditions to `POST /api/predict`.
3. FastAPI validates the request and calls the trained model.
4. The counterfactual engine searches allowed operational changes.
5. FastAPI stores the prediction and scenarios in SQLite.
6. React displays risk and ranked interventions.
7. Saved decisions are available from `GET /api/history`.

## Main endpoints

- `GET /api/health`
- `POST /api/register`
- `POST /api/login`
- `POST /api/predict`
- `GET /api/history`

## Database tables

- `users`
- `sessions`
- `predictions`

Passwords use PBKDF2-HMAC-SHA256 with a unique random salt. This is an
educational local prototype. Production deployment would additionally require
HTTPS, session expiration, rate limiting and environment-based secrets.
