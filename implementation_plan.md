# CineScope: Implementation Plan

CineScope is a data-driven movie analytics and recommendation platform built using Python Flask, SQLite, Pandas, NumPy, and Plotly. It features a dark user interface inspired by Letterboxd, Spotify Analytics, and IMDb.

## User Review Required

> [!IMPORTANT]
> **TMDB API Key & Demo Fallback System**:
> To make the app run instantly out-of-the-box without requiring the user to obtain a TMDB API key first, we will implement a local **Demo Fallback System** containing details for ~40 popular movies across 4 directors (Christopher Nolan, Quentin Tarantino, Martin Scorsese, and James Cameron). If `TMDB_API_KEY` is missing in the environment, the app will enter a "Demo Mode", utilizing this local data structure for search, profile page, and details.

> [!TIP]
> **Plotly & Bootstrap Theme Integration**:
> We will inject Plotly's configuration to use custom dark themes matching the Letterboxd HSL color palette (pitch dark backgrounds `#14181c`, custom greens `#00c030`, oranges `#ff8000`, and secondary grays `#9ab`).

---

## Proposed Changes

We will create a modular, service-oriented Flask application under the directory `d:\INTERNSHIP PROJECT`.

### Core Configuration and Bootstrapping

#### [NEW] [requirements.txt](file:///d:/INTERNSHIP%20PROJECT/requirements.txt)
Defines project dependencies:
- Flask, Flask-SQLAlchemy, Flask-Login, Werkzeug (auth)
- requests (TMDB client)
- pandas, numpy (recommendations, analytics)
- plotly (visualizations)
- python-dotenv (environment configurations)

#### [NEW] [config.py](file:///d:/INTERNSHIP%20PROJECT/config.py)
App configuration handling:
- SQLite Database path configuration
- TMDB API variables and session configurations
- Secret keys and cookie security settings

#### [NEW] [.env](file:///d:/INTERNSHIP%20PROJECT/.env)
Environment template for user credentials, port configuration, and `TMDB_API_KEY`.

#### [NEW] [run.py](file:///d:/INTERNSHIP%20PROJECT/run.py)
Main entrypoint to run the Flask development server.

---

### Application Factory and Models

#### [NEW] [__init__.py](file:///d:/INTERNSHIP%20PROJECT/app/__init__.py)
Flask Application Factory:
- Initializing database and migrations
- Initializing Flask-Login session manager
- Registering blueprints: `auth`, `main`, `watchlist`, `directors`, `analytics`
- Registering global context processors and template helpers

#### [NEW] [models.py](file:///d:/INTERNSHIP%20PROJECT/app/models.py)
Database Schema:
- `User`: Handles registration, login (hashed passwords via `scrypt` or `pbkdf2`).
- `Watchlist`: Tracks user's personalized movie catalog. Includes flags for `watched` state, user ratings (1-10), date added, and date watched.
- `APICache`: Standard cache for TMDB API queries (caching responses as text/json by URL key for 24h to avoid API throttling and speed up pages).

---

### Service Layer

#### [NEW] [tmdb.py](file:///d:/INTERNSHIP%20PROJECT/app/services/tmdb.py)
TMDB Client Service:
- Fetches trending, popular, search queries, and specific movie info.
- Formulates a crew and cast list.
- Implements an automated local JSON fallback when the API key is not present or yields connection errors.
- Integrates with the database `APICache` to store queries.

#### [NEW] [recommendations.py](file:///d:/INTERNSHIP%20PROJECT/app/services/recommendations.py)
Content-Based Recommendation Engine:
- Utilizes Pandas and NumPy.
- Builds a profile vector of user preferences based on their high-rated watchlist movies (analyzing genres and directors).
- Ranks candidate movies fetched from TMDB trending/popular using cosine similarity metrics.
- Recommends movies matching the profile, avoiding already-watched titles.

#### [NEW] [analytics.py](file:///d:/INTERNSHIP%20PROJECT/app/services/analytics.py)
Plotly Analytics Engine:
- **Genre Dashboard plots**: Most popular genres, highest rated genres, genre distribution.
- **Revenue Dashboard plots**: Budget vs Revenue scatter charts, revenue-to-rating correlation, top grossing lists.
- **Director Profile plots**: Filmography ratings, filmography revenue bar chart, genre breakdowns.
- **Director Comparison plots**: Combined bar/line charts side-by-side.
- **Cinephile Dashboard plots**: Most watched decade, genre breakdown, stats charts.

---

### Blueprints & Routes

#### [NEW] [auth.py](file:///d:/INTERNSHIP%20PROJECT/app/routes/auth.py)
User authentication endpoints (register, login, logout, profile settings).

#### [NEW] [main.py](file:///d:/INTERNSHIP%20PROJECT/app/routes/main.py)
Main explorer (landing page, trending lists, search engine, movie details page).

#### [NEW] [watchlist.py](file:///d:/INTERNSHIP%20PROJECT/app/routes/watchlist.py)
Watchlist management endpoints (add, remove, toggle watched, review rating).

#### [NEW] [directors.py](file:///d:/INTERNSHIP%20PROJECT/app/routes/directors.py)
Director profile search and comparison page.

#### [NEW] [analytics.py](file:///d:/INTERNSHIP%20PROJECT/app/routes/analytics.py)
Cinephile dashboard, general revenue analytics, and general genre analytics.

---

### Templates and Static Assets

#### [NEW] [style.css](file:///d:/INTERNSHIP%20PROJECT/app/static/css/style.css)
Visual Design System:
- Dark background palette (`#0B0E11` to `#182027`)
- Vivid typography and neon accents (Spotify green `#1DB954` or Letterboxd green `#00C030`)
- Large movie poster grid system, transition card animations, scale hovers.

#### [NEW] [main.js](file:///d:/INTERNSHIP%20PROJECT/app/static/js/main.js)
AJAX handlers for watchlist toggling, rating updates, and live search.

#### [NEW] [base.html](file:///d:/INTERNSHIP%20PROJECT/app/templates/base.html)
Shared navbar, alerts system, loading states, and dark theme container wrapper.

#### [NEW] Template Subfolders
Folders for `auth`, `main`, `watchlist`, `directors`, and `analytics`.

---

## Verification Plan

### Automated Verification
- Write a basic unit test file `tests.py` verifying:
  - User registration and login flow.
  - Watchlist operations (adding, marking watched, deleting).
  - Recommendation calculations (mock inputs feed into the logic, outputs ranked list).

### Manual Verification
- Spin up the server: `python run.py`.
- Open browser to check:
  - Registration and logging in.
  - Searching movies and view detailed posters.
  - Adding to watchlist, marking watched, rating.
  - Checking the Revenue, Genre, Director comparison, and Cinephile dashboards.
