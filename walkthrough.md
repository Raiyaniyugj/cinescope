# Walkthrough - CineScope: Data-Driven Movie Analytics and Recommendation Platform

I have successfully designed and built **CineScope**, a Python Flask web application that serves as a movie discovery, watchlist management, and analytical platform for film enthusiasts. The application features a Spotify/Letterboxd-inspired dark theme and includes a content-based recommendation engine, robust SQLite caching, and dynamic Plotly visual dashboards.

---

## Architecture & Codebase Design

CineScope is structured using the Flask **Application Factory Pattern** with modular Blueprints to divide logical responsibilities.

```
d:\INTERNSHIP PROJECT\
├── app/
│   ├── __init__.py          # Flask Application Factory & Jinja filters
│   ├── models.py            # SQLite schemas (User, Watchlist, APICache)
│   ├── routes/              # Blueprint controller endpoints
│   │   ├── auth.py          # Signup, Login, Logout, Profile settings
│   │   ├── main.py          # Explore, Search, Movie details
│   │   ├── watchlist.py     # Add/remove watchlist, toggle watched, review/rate
│   │   ├── directors.py     # Director profile views and search
│   │   └── analytics.py     # Cinephile metrics and charts
│   ├── services/            # Algorithms and external client layers
│   │   ├── tmdb.py          # TMDB client with local cache & JSON fallback
│   │   ├── recommendations.py # Vector similarity recommender using Pandas/NumPy
│   │   └── analytics.py     # Plotly interactive graphs generator
│   ├── static/              # CSS variables, HSL color palettes, and vanilla JS
│   └── templates/           # Modular Jinja2 HTML layout components
├── config.py                # Database and session configuration
├── run.py                   # Dev server entrypoint
└── requirements.txt         # Core libraries (Flask, Pandas, NumPy, Plotly, requests)
```

---

## Key Modules Implemented

### 1. Database & Session Management
* **Database Tables** ([models.py](file:///d:/INTERNSHIP%20PROJECT/app/models.py)):
  * `User`: Hashed password storage (via `scrypt`/`pbkdf2`) and profile info.
  * `Watchlist`: Tracks user catalogs. Stores ratings (1-10), watched states, dates.
  * `APICache`: Key-value cache that maps query requests to JSON string text payloads.
* **Access Control**: Session validation and auth rules integrated using `Flask-Login` in [auth.py](file:///d:/INTERNSHIP%20PROJECT/app/routes/auth.py).

### 2. TMDB Client & 24h Caching Layer
* **API Connector** ([tmdb.py](file:///d:/INTERNSHIP%20PROJECT/app/services/tmdb.py)):
  * Wraps HTTP requests to TMDB REST endpoints for trending, search, and movie records.
  * Checks `APICache` database table before querying TMDB. Extends performance by saving responses for **24 hours** to avoid API throttling and speed up page load speeds.
* **Local Offline Fallback ("Demo Mode")**:
  * If the API key is not present in `.env` or network requests fail, the client activates an offline sandbox using a local memory structure containing full attributes of 40 popular movies across 4 directors (Nolan, Tarantino, Scorsese, Cameron).

### 3. Content-Based Recommendation Engine
* **Algorithm Pipeline** ([recommendations.py](file:///d:/INTERNSHIP%20PROJECT/app/services/recommendations.py)):
  1. Pulls user's watched list items and their ratings to act as weights.
  2. Aggregates and normalizes genre and director counts to construct a **User Preference Profile Vector**.
  3. Queries candidate movies from trending/popular queues.
  4. Calculates **Cosine Similarity** between candidate attribute vectors and the user preference profile.
  5. Returns high-scoring movies that the user hasn't added to their watchlist yet.

### 4. Interactive Analytics Service
* **Plotly Visuals** ([analytics.py](file:///d:/INTERNSHIP%20PROJECT/app/services/analytics.py)):
  * Generates high-resolution dark-themed SVG graphs configured to blend with CSS backgrounds:
    * **Genre Analytics**: Donut chart of genre distribution and horizontal bar chart of average ratings.
    * **Revenue Analytics**: Budget vs. Revenue scatter plot showing budget-to-revenue correlation, and top-grossing movie charts.
    * **Director Profiler**: Grouped comparisons and average rating trends across filmographies.
    * **Cinephile Dashboard**: Personal stats (e.g. genre breakdown, decade distribution, watched logs over time).

---

## Verification & Launch Plan

### 1. Dependencies Setup
Install libraries from requirements file:
```bash
pip install -r requirements.txt
```

### 2. Execution
Spin up the Flask development server:
```bash
python run.py
```
Open browser to `http://localhost:5000` (or the configured port in `.env`).

### 3. Feature Verification
* **Demo Sandbox**: Remove `TMDB_API_KEY` from `.env` to verify immediate redirection into local sandbox demo mode.
* **Watchlist Flow**: Sign up, search "Inception", add to watchlist, rate it `10`, and check the dashboard to verify that recommended movies immediately skew towards Sci-Fi/Christopher Nolan titles.
* **Dashboard Checks**: Check the "Genre Stats" and "Revenue Analysis" links in the navbar to confirm that Plotly graphs load with dark color schemes and responsive resizing.
