# Movie Platform --- GCP MVP Specification

## 1. Project Overview

### Goal

Build a small movie discovery web application whose **primary objective
is to demonstrate practical GCP architecture and cloud engineering**,
not to build an advanced recommendation engine.

The application allows users to:

-   Browse popular movies.
-   Search for movies.
-   View movie details.
-   Optionally maintain a small set of user preferences such as
    favorites.
-   Generate basic application events for analytics.

The application uses **TMDB as the external movie-data provider**.

### MVP Principle

Keep the application intentionally simple.

The project should provide enough functionality to demonstrate:

-   Containerized workloads.
-   Cloud Run.
-   API Gateway.
-   Managed database.
-   Secret management.
-   Redis caching (optional).
-   Pub/Sub event-driven ingestion (optional).
-   BigQuery analytics (optional).
-   Terraform/IaC.
-   CI/CD.
-   Monitoring and logging.

Do **not** implement the recommendation engine in the MVP.

------------------------------------------------------------------------

# 2. High-Level Architecture

``` text
                         ┌──────────────────────┐
                         │      User Browser    │
                         └──────────┬───────────┘
                                    │ HTTPS
                                    ▼
                         ┌──────────────────────┐
                         │   Next.js Frontend   │
                         │      Cloud Run       │
                         └──────────┬───────────┘
                                    │ HTTPS
                                    ▼
                         ┌──────────────────────┐
                         │     API Gateway      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Flask Backend     │
                         │      Cloud Run       │
                         └───────┬───────┬──────┘
                                 │       │
                    ┌────────────┘       └──────────────┐
                    ▼                                   ▼
             ┌─────────────┐                     ┌─────────────┐
             │   TMDB API  │                     │  Database   │
             │  External   │                     │   (TBD)     │
             └─────────────┘                     └─────────────┘

Optional:
                                 │
                                 ▼
                          ┌─────────────┐
                          │    Redis    │
                          │    Cache    │
                          └─────────────┘

Optional analytics:

Flask Backend
      │
      ▼
   Pub/Sub
      │
      ▼
  BigQuery
```

------------------------------------------------------------------------

# 3. Technology Stack

## Frontend

-   Next.js
-   React
-   TypeScript
-   Tailwind CSS
-   Responsive UI

The frontend must communicate with the application's backend API rather
than directly with TMDB.

## Backend

-   Python
-   Flask
-   REST API
-   Docker
-   Cloud Run

The Flask service is responsible for:

-   Application API endpoints.
-   TMDB integration.
-   User/favorite persistence.
-   Input validation.
-   Publishing optional analytics events.

## External API

-   TMDB API

TMDB credentials must never be exposed to the browser.

## GCP

Core:

-   Cloud Run
-   API Gateway
-   Secret Manager
-   Artifact Registry
-   Cloud Logging / Cloud Monitoring

Data:

-   Database: initially SQLite for local development, but **do not use
    SQLite as the production database on Cloud Run**.
-   Production database decision: Cloud SQL if persistent relational
    user data is required.

Optional:

-   Memorystore for Redis
-   Pub/Sub
-   BigQuery

Infrastructure:

-   Terraform

CI/CD:

-   GitHub Actions or Cloud Build

------------------------------------------------------------------------

# 4. MVP Scope

## 4.1 Movie Discovery

The frontend should provide:

### Home page

Display:

-   Popular movies.
-   Movie poster.
-   Movie title.
-   Release date/year.
-   Rating.

Example:

``` text
GET /api/movies/popular
```

### Search

Allow users to search TMDB movies.

``` text
GET /api/movies/search?q=inception
```

### Movie details

Display:

-   Poster.
-   Title.
-   Overview.
-   Release date.
-   Genres.
-   Rating.
-   Runtime when available.

``` text
GET /api/movies/{movie_id}
```

------------------------------------------------------------------------

# 5. User Features

Authentication is **out of scope for the first MVP**.

A minimal user model may be introduced only if necessary for
demonstrating persistence.

Possible functionality:

``` text
Add movie to favorites
Remove movie from favorites
List favorites
```

Example API:

``` text
POST   /api/favorites/{movie_id}
DELETE /api/favorites/{movie_id}
GET    /api/favorites
```

For the first iteration, a simple anonymous/session identifier can be
used if persistent user accounts are intentionally avoided.

Do not introduce a complete authentication system unless it provides
clear value for the GCP learning objectives.

------------------------------------------------------------------------

# 6. Backend Architecture

Recommended Flask structure:

``` text
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   │
│   ├── routes/
│   │   ├── movies.py
│   │   ├── favorites.py
│   │   └── health.py
│   │
│   ├── services/
│   │   ├── tmdb_service.py
│   │   ├── movie_service.py
│   │   └── event_service.py
│   │
│   ├── repositories/
│   │   └── favorites_repository.py
│   │
│   └── models/
│       └── favorite.py
│
├── tests/
├── requirements.txt
├── Dockerfile
└── run.py
```

### Architectural rule

Routes should remain thin.

Example:

``` text
HTTP Request
     ↓
Route
     ↓
Service
     ↓
Repository / External API
```

Do not put TMDB HTTP logic directly inside route functions.

------------------------------------------------------------------------

# 7. TMDB Integration

TMDB calls belong in the Flask backend.

The browser must not call TMDB directly.

Example:

``` text
Next.js
   │
   │ GET /api/movies/popular
   ▼
Flask
   │
   │ GET TMDB API
   ▼
TMDB
```

The TMDB API key must be stored in:

``` text
GCP Secret Manager
```

and injected into the Cloud Run backend at runtime.

------------------------------------------------------------------------

# 8. Redis --- Optional MVP Enhancement

Redis should be added only after the basic application works.

Recommended use case:

### Cache TMDB responses

For example:

``` text
GET /movies/popular
```

Flow:

``` text
Flask
  │
  ├── Redis HIT ──────► return cached result
  │
  └── Redis MISS
          │
          ▼
        TMDB
          │
          ▼
        Redis
          │
          ▼
       Response
```

Good cache candidates:

-   Popular movies.
-   Trending movies.
-   Movie details.
-   Search results with short TTL.

Do not use Redis as the primary persistent database.

------------------------------------------------------------------------

# 9. Pub/Sub + BigQuery --- Optional Analytics

This should be treated as an **analytics feature**, not as part of
recommendation generation.

The backend can publish user/application events such as:

``` json
{
  "event_type": "movie_viewed",
  "movie_id": 123,
  "timestamp": "2026-09-05T18:00:00Z",
  "session_id": "..."
}
```

Possible events:

-   `movie_viewed`
-   `movie_searched`
-   `movie_favorited`
-   `movie_unfavorited`

Architecture:

``` text
User
  │
  ▼
Next.js
  │
  ▼
Flask API
  │
  ├──────────────► Application response
  │
  ▼
Pub/Sub
  │
  ▼
BigQuery
```

The analytics pipeline should not block the user's request.

The backend should publish the event and return the application response
independently.

------------------------------------------------------------------------

# 10. BigQuery

Create a simple event table such as:

``` text
movie_events
```

Possible fields:

``` text
event_id
event_type
movie_id
session_id
timestamp
metadata
```

Example analytics queries:

-   Most viewed movies.
-   Most searched movies.
-   Most favorited movies.
-   Number of movie views per day.
-   Search activity over time.

This gives the project a legitimate reason to use Pub/Sub and BigQuery
without artificially introducing a recommendation engine.

------------------------------------------------------------------------

# 11. Database Decision

## Local Development

SQLite is acceptable for local development.

Example:

``` text
SQLite
   ↓
Flask
```

## Production

Do not rely on SQLite on Cloud Run because the container filesystem is
ephemeral.

If the MVP needs persistent favorites/users:

``` text
Cloud Run
    ↓
Cloud SQL
```

Recommended initial schema:

``` text
users
-----
id
created_at

favorites
---------
id
user_id
movie_id
created_at
```

However, if authentication and persistent favorites are removed from the
MVP, **you do not need Cloud SQL at all**.

This is preferable if the goal is primarily learning GCP rather than
database engineering.

------------------------------------------------------------------------

# 12. API Specification

## Health

``` text
GET /health
```

Response:

``` json
{
  "status": "ok"
}
```

## Popular movies

``` text
GET /api/movies/popular
```

## Search

``` text
GET /api/movies/search?q={query}
```

## Movie details

``` text
GET /api/movies/{movie_id}
```

## Favorites

Optional:

``` text
GET    /api/favorites
POST   /api/favorites/{movie_id}
DELETE /api/favorites/{movie_id}
```

------------------------------------------------------------------------

# 13. Frontend Structure

Recommended:

``` text
frontend/
├── app/
│   ├── page.tsx
│   ├── search/
│   │   └── page.tsx
│   └── movie/
│       └── [id]/
│           └── page.tsx
│
├── components/
│   ├── MovieCard.tsx
│   ├── MovieGrid.tsx
│   ├── SearchBar.tsx
│   └── Header.tsx
│
├── lib/
│   └── api.ts
│
├── types/
│   └── movie.ts
│
├── Dockerfile
└── package.json
```

The frontend API client should communicate with Flask:

``` text
frontend/lib/api.ts
       ↓
Backend API
```

Avoid putting business logic or TMDB credentials in the frontend.

------------------------------------------------------------------------

# 14. GCP Deployment Architecture

## Frontend

``` text
Next.js
   ↓
Docker
   ↓
Artifact Registry
   ↓
Cloud Run
```

## Backend

``` text
Flask
   ↓
Docker
   ↓
Artifact Registry
   ↓
Cloud Run
```

## API Gateway

``` text
Internet
   ↓
API Gateway
   ↓
Flask Cloud Run
```

Only the API Gateway should be the public API entry point if this is
part of the learning objective.

------------------------------------------------------------------------

# 15. Secrets

Use:

``` text
Secret Manager
```

Secrets:

``` text
TMDB_API_KEY
```

Never:

``` text
.env committed to Git
API key in Next.js
API key in Docker image
API key hardcoded in Python
```

------------------------------------------------------------------------

# 16. Terraform

Terraform should provision the GCP infrastructure.

Suggested structure:

``` text
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
├── cloud_run.tf
├── api_gateway.tf
├── artifact_registry.tf
├── secret_manager.tf
├── pubsub.tf
├── bigquery.tf
└── redis.tf
```

Optional resources should be isolated so they can be enabled/disabled
easily.

------------------------------------------------------------------------

# 17. CI/CD

Recommended pipeline:

``` text
Git Push
   ↓
CI
   ├── Test frontend
   ├── Test backend
   └── Build Docker images
          ↓
    Artifact Registry
          ↓
       Deploy
          ↓
      Cloud Run
```

Terraform deployment should be separated from application deployment.

------------------------------------------------------------------------

# 18. Observability

The MVP should demonstrate:

-   Cloud Logging.
-   Cloud Monitoring.
-   Cloud Run metrics.
-   Request latency.
-   Error rate.
-   Container logs.

Backend should emit structured logs where practical.

Example:

``` text
INFO movie_request
movie_id=123
endpoint=/api/movies/123
```

------------------------------------------------------------------------

# 19. Security Requirements

Minimum:

-   TMDB API key in Secret Manager.
-   HTTPS.
-   Backend input validation.
-   No secrets in source code.
-   No secrets in frontend.
-   Least-privilege IAM service accounts.
-   CORS configured explicitly.
-   Container images stored in Artifact Registry.

------------------------------------------------------------------------

# 20. MVP Implementation Phases

## Phase 1 --- Application

Build:

``` text
Next.js
    ↓
Flask
    ↓
TMDB
```

Features:

-   Popular movies.
-   Search.
-   Movie details.

No GCP complexity yet.

------------------------------------------------------------------------

## Phase 2 --- Containerization

Create Docker images for:

-   frontend
-   backend

Run both locally.

------------------------------------------------------------------------

## Phase 3 --- GCP Core

Deploy:

``` text
Next.js → Cloud Run

Flask → Cloud Run

Artifact Registry
Secret Manager
```

------------------------------------------------------------------------

## Phase 4 --- API Gateway

Add:

``` text
Frontend
   ↓
API Gateway
   ↓
Flask Cloud Run
```

------------------------------------------------------------------------

## Phase 5 --- Persistence

Only if favorites are implemented:

``` text
Flask
   ↓
Cloud SQL
```

------------------------------------------------------------------------

## Phase 6 --- Redis

Add caching:

``` text
Flask
   ↓
Redis
   ↓
TMDB
```

Measure the difference between cache hit and cache miss.

------------------------------------------------------------------------

## Phase 7 --- Event-Driven Analytics

Add:

``` text
Flask
   ↓
Pub/Sub
   ↓
BigQuery
```

Track movie interactions.

------------------------------------------------------------------------

## Phase 8 --- IaC + CI/CD

Add:

``` text
Terraform
+
CI/CD
```

------------------------------------------------------------------------

# 21. Explicitly Out of Scope

The MVP should NOT include:

-   Machine-learning recommendation models.
-   Recommendation Worker.
-   Cloud Run Jobs for recommendations.
-   Complex authentication.
-   Microservice explosion.
-   Kubernetes/GKE.
-   Vector database.
-   RAG.
-   Model training pipeline.
-   Complex user profiles.
-   Real-time recommendation generation.

These can be future extensions.

------------------------------------------------------------------------

# 22. Target Final Architecture

The preferred MVP architecture is:

``` text
                         ┌───────────────┐
                         │    Browser    │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │    Next.js    │
                         │   Cloud Run   │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │  API Gateway  │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │ Flask Backend │
                         │   Cloud Run   │
                         └───┬───────┬───┘
                             │       │
                    ┌────────┘       └────────┐
                    ▼                         ▼
               ┌─────────┐              ┌──────────┐
               │  TMDB   │              │ Database │
               │   API   │              │ optional │
               └─────────┘              └──────────┘


             Optional analytics:

                         Flask
                           │
                           ▼
                       Pub/Sub
                           │
                           ▼
                       BigQuery

             Optional caching:

                         Flask
                           │
                           ▼
                         Redis
```

# 23. Success Criteria

The project is successful when:

1.  A user can browse and search movies.
2.  Next.js is deployed independently from Flask.
3.  Flask is deployed on Cloud Run.
4.  API requests pass through API Gateway.
5.  TMDB credentials are protected with Secret Manager.
6.  The application is containerized.
7.  Infrastructure is reproducible with Terraform.
8.  CI/CD can deploy the application.
9.  Cloud Logging/Monitoring can be used to diagnose requests.
10. Optional Pub/Sub → BigQuery analytics works without blocking the
    API.
11. Optional Redis caching demonstrably reduces repeated TMDB requests.

The primary success metric is **the quality of the GCP architecture and
engineering practices**, not the sophistication of the movie
application.
