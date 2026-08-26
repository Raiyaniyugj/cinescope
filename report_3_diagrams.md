# Reporting 3 Diagram Specifications

This document contains the detailed specifications required to generate the four diagrams for Section 4(c) of the Reporting 3 document. It is based strictly on the current implemented state of the CineScope project as of Reporting 3.

---

## 1. UPDATED SYSTEM ARCHITECTURE

**Diagram Title:** CineScope Updated System Architecture  
**Purpose:** To show the complete physical and logical structure of the application, emphasizing the newly introduced production deployment layers and the robust separation of concerns in the backend.

### Nodes and Components:
1. **Client Layer (IMPLEMENTED):**
   - Node Text: "Web Browser (Client)"
   - Sub-items: HTML5, Custom CSS, JS, Bootstrap 5 UI.
2. **Deployment / Production Preparation Layer (PRODUCTION PREPARATION):**
   - Node Text: "Cloud Deployment Target: Render/Railway"
   - Node Text: "Gunicorn (WSGI Server)"
3. **Application Framework Layer (IMPLEMENTED):**
   - Node Text: "Flask Application Factory"
   - Node Text: "Flask Blueprints (Routing)"
4. **Application Modules / Blueprints (IMPLEMENTED):**
   - Node Text: "Auth & Profile Manager (auth.py)"
   - Node Text: "Movie Explorer & Search (main.py)"
   - Node Text: "Watchlist & History Manager (watchlist.py)"
   - Node Text: "Custom Lists Manager (lists.py)"
   - Node Text: "Personnel & Studio Profiles (directors.py, profiles.py)"
   - Node Text: "Analytics Dashboard (analytics.py)"
5. **Data Processing & Service Layer (IMPLEMENTED):**
   - Node Text: "TMDB API & Providers Client (tmdb.py)"
   - Node Text: "Content-Based Recommender (recommendations.py)"
   - Node Text: "Analytics Data Generator (Plotly)"
6. **Data Storage Layer (IMPLEMENTED):**
   - Node Text: "SQLAlchemy ORM"
   - Node Text: "SQLite Database" (Contains: Users, Watchlists, Watched, CustomLists, UserFavorites, APICache)
7. **External Service (IMPLEMENTED):**
   - Node Text: "TMDB REST API"

### Relationships and Data Flow (Arrows):
- **Client Layer** `<-- (HTTP/HTTPS) -->` **Gunicorn (WSGI Server)**
- **Gunicorn** `<-- (WSGI Interface) -->` **Flask Application Factory**
- **Flask Application Factory** `-->` Routes to **Application Modules / Blueprints**
- **Application Modules** `<-- (Data Request) -->` **Data Processing & Service Layer**
- **TMDB API & Providers Client** `<-- (Check Cache / Fallback) -->` **SQLite Database (APICache)**
- **TMDB API & Providers Client** `<-- (HTTP REST GET) -->` **TMDB REST API**
- **Content-Based Recommender** `<-- (Read Watched Data) -->` **SQLAlchemy ORM**
- **Analytics Data Generator** `<-- (Process Data) -->` **SQLAlchemy ORM**
- **SQLAlchemy ORM** `<-- (SQL Queries) -->` **SQLite Database**

### What changed from Reporting 2:
- **Reporting 2:** Basic watchlist and recommendation engine running on local development server.
- **Reporting 3:** Configured the **Deployment / Production Preparation Layer** (Gunicorn/Cloud target). Expanded Application Modules to map to specific real Flask blueprints (`lists.py`, `watchlist.py`, `directors.py`). Added integrated Watch Provider data fetching within the TMDB service layer.

### Short Explanation for Report:
*The updated system architecture illustrates the transition toward a production-preparation environment using Gunicorn as the WSGI server. The backend has been expanded since Reporting 2 to support advanced features like independent watch history, written reviews, custom lists, and detailed personnel profiles, all cleanly separated through verified Flask Blueprints.*

**Generation constraints:**
- Keep all labels readable.
- Do not overcrowd the diagram.
- Use clear directional arrows.
- Do not invent components.
- Use only components listed in this specification.
- Keep terminology identical across all four diagrams.

---

## 2. UPDATED APPLICATION WORKFLOW / PROCESS FLOW

**Diagram Title:** CineScope Application Process Flow  
**Purpose:** To map the exact user journey through the modernized frontend, demonstrating how the new Profile, Avatar, Settings, and Watch History features branch off the core navigation.

### Nodes (Decision points & Actions):
1. **Start:** User accesses CineScope URL.
2. **Decision:** Is User Authenticated? (Yes/No)
   - *If No:* Redirect to **Login / Register Page**. After success -> **Home Page**.
   - *If Yes:* Proceed to **Home Page (Dynamic Hero & Trending)**.
3. **From Home Page, User can navigate to:**
   - Path A: **Search/Browse Movies/TV** -> **TMDB Request Logic** -> Show Results -> **Movie/TV Details Page**.
   - Path B: **Films Page** -> View Custom Lists & Watch History.
   - Path C: **Profile Page** -> View detailed watch history, analytics, and Top 4 Pinned Favorites.
   - Path D: **Recommendation Engine** -> Generate Vector & Cosine Similarity -> Display recommendations.
4. **From Profile Page, User can navigate to:**
   - Path C1: **Settings Page** (Update user configs and Pin Top 4 `UserFavorite` movies).
   - Path C2: **Avatar Page** (Update profile imagery).
5. **From Movie Details Page, User can independently:**
   - Action: **Add to Watchlist** (Independent Action) -> Save to `Watchlist` table.
   - Action: **Mark as Watched** (Independent Action) -> Save to `Watched` table.
   - Action: **Rate Movie (0.5 to 5.0)** -> Update `Watched` table.
   - Action: **Write Review** -> Update `Watched` table.
   - Action: **Like / Heart Movie** -> Update `is_favorite` flag in `Watched` table.
   - View: **Where to Watch** -> Display Streaming Providers (Data retrieved by TMDB Client).
   - Navigate: **Click Actor / Director / Studio** -> Browse specific personnel/company profiles.
6. **TMDB Request Logic (Background Process):**
   - **Action:** Request data from TMDB REST API.
   - **Decision:** Success?
   - *If Yes:* Display Data + Save to APICache.
   - *If No:* Fetch from APICache (or Fallback) -> Display Data.

### What changed from Reporting 2:
- **Reporting 2:** Basic navigation for searching movies and adding them to a watchlist.
- **Reporting 3:** Added explicit flows for **Settings** and **Avatar** pages. Expanded the **Movie Details** interactions to explicitly include independent **Mark as Watched**, **0.5 increment Ratings**, **Written Reviews**, and **Like/Heart flag**. Added the distinct **Pin Top 4 Favorites** action on the Settings page. Added browsing paths for **Actor, Director, and Studio profiles** and **Where to Watch** provider information.

### Short Explanation for Report:
*This process flow demonstrates the advanced user interactions implemented in the current phase. It highlights the expanded user profile journey, the independent "Mark as Watched" and review flows, the dual favorites implementation (general likes vs. pinned top 4), and the ability to navigate deeply into specific actor, director, and studio portfolios.*

**Generation constraints:**
- Keep all labels readable.
- Do not overcrowd the diagram.
- Use clear directional arrows.
- Do not invent components.
- Use only components listed in this specification.
- Keep terminology identical across all four diagrams.

---

## 3. UPDATED SYSTEM BLOCK DIAGRAM

**Diagram Title:** CineScope High-Level Functional Block Diagram  
**Purpose:** To provide a clean, high-level abstraction of the system's operational domains, highlighting the separation of UI presentation from backend data computation.

### Blocks and Contents:
1. **Block 1: Presentation & UI Domain (IMPLEMENTED)**
   - Jinja2 Templates (Modular Layouts)
   - Bootstrap 5 & Custom CSS
   - Interactive Plotly Dashboards
2. **Block 2: Web Server Domain (PRODUCTION PREPARATION)**
   - Gunicorn Worker Processes
   - Flask Request Handlers
   - Flask-Login Session Manager
3. **Block 3: Core Application Domain (IMPLEMENTED)**
   - User Account Management
   - Independent Watch History & Reviews
   - Custom Lists & Favorites Tracking
   - Personnel / Studio Browsing
4. **Block 4: Data Science & Processing Domain (IMPLEMENTED)**
   - Pandas Vectorizer & Cosine Similarity
   - Plotly Graph Generator
   - TMDB Data & Provider Parsing
5. **Block 5: Storage & External Domain (IMPLEMENTED)**
   - Local SQLite Database
   - TMDB REST API
   - APICache Manager

### Relationships and Data Flow:
- **Presentation & UI** `<-- (Data Flow) -->` **Web Server Domain**
- **Web Server Domain** `<-- (Data Flow) -->` **Core Application Domain**
- **Core Application Domain** `--> (Data Request) -->` **Data Science & Processing Domain**
- **Data Science & Processing Domain** `<-- (Data Retrieval) -->` **Storage & External Domain**
- **Core Application Domain** `<-- (Data Retrieval) -->` **Storage & External Domain**

### What changed from Reporting 2:
- **Reporting 2:** Basic three-tier abstraction (UI, Flask, DB).
- **Reporting 3:** Expanded the **Core Application Domain** to represent independent watch histories, written reviews, custom lists, and detailed personnel browsing. Separated the **Data Science & Processing Domain** to clearly represent analytical features and provider extraction.

### Short Explanation for Report:
*The functional block diagram groups the application into distinct domains. This clearly separates data science logic from standard web routing and demonstrates the inclusion of advanced interaction tracking (reviews, lists, favorites).*

**Generation constraints:**
- Keep all labels readable.
- Do not overcrowd the diagram.
- Use clear directional arrows.
- Do not invent components.
- Use only components listed in this specification.
- Keep terminology identical across all four diagrams.

---

## 4. UPDATED UML DIAGRAM

**Diagram Title:** CineScope UML Class & Module Specification  
**Purpose:** To define the exact data models (ORM) and primary service classes used in the backend, focusing on the database schema relationships and the processing logic.

### Classes / Entities (and their attributes/methods):

1. **User (SQLAlchemy Model)**
   - Attributes: `id` (Integer, PK), `username` (String), `email` (String), `password_hash` (String), `given_name` (String), `family_name` (String), `bio` (Text), `avatar_url` (String).
   - Methods: `set_password(password)`, `check_password(password)`.
2. **Watchlist (SQLAlchemy Model)**
   - Attributes: `id` (Integer, PK), `user_id` (Integer, FK), `tmdb_id` (Integer), `title` (String), `added_at` (DateTime).
3. **Watched (SQLAlchemy Model) - INDEPENDENT LOG**
   - Attributes: `id` (Integer, PK), `user_id` (Integer, FK), `tmdb_id` (Integer), `title` (String), `rating` (Float), `review` (Text), `is_favorite` (Boolean - *General Like/Heart*), `watched_at` (DateTime).
4. **CustomList (SQLAlchemy Model)**
   - Attributes: `id` (Integer, PK), `user_id` (Integer, FK), `name` (String), `description` (Text), `created_at` (DateTime).
5. **CustomListMovie (SQLAlchemy Model)**
   - Attributes: `id` (Integer, PK), `list_id` (Integer, FK), `tmdb_id` (Integer), `title` (String).
6. **UserFavorite (SQLAlchemy Model) - TOP 4 PINNED**
   - Attributes: `id` (Integer, PK), `user_id` (Integer, FK), `tmdb_id` (Integer), `title` (String), `order` (Integer - *1, 2, 3, or 4*).
7. **APICache (SQLAlchemy Model)**
   - Attributes: `url_key` (String, PK), `response_text` (Text), `created_at` (DateTime).
8. **TMDBService (Service Module)**
   - Methods: `search_multi(query)`, `get_movie_details(movie_id)` *(Note: This method is explicitly responsible for appending and extracting watch/providers data)*, `get_tv_details(tv_id)`, `get_person_details(person_id)`, `get_company_movies(company_id)`.
9. **RecommenderEngine (Service Module)**
   - Methods: `build_user_preference_vector(user_id)`, `calculate_cosine_similarity(user_vector, candidate_movies)`, `get_recommendations(user_id)`.
10. **AnalyticsEngine (Service Module)**
    - Methods: `generate_genre_distribution(user_id)`, `generate_revenue_scatter()`.

### Relationships and Multiplicity:
- **User** `1 -- *` **Watchlist** *(One User has Many Watchlist items)*.
- **User** `1 -- *` **Watched** *(One User has Many Watched items. Completely independent from Watchlist.)*.
- **User** `1 -- *` **CustomList** *(One User creates Many Custom Lists)*.
- **CustomList** `1 -- *` **CustomListMovie** *(One List contains Many Movies. This is the association model for Lists.)*.
- **User** `1 -- *` **UserFavorite** *(One User has Top 4 Pinned Favorites)*.
- **TMDBService** `uses` **APICache** *(Dependency: API client reads/writes to the cache model).*
- **RecommenderEngine** `reads` **Watched** *(Dependency: Needs ratings and history from Watched table to generate the preference vector).*

### What changed from Reporting 2:
- **Reporting 2:** Basic `User` and `Watchlist` tables.
- **Reporting 3:** Separated `Watchlist` from the newly implemented `Watched` table to support independent tracking. Added `rating` (Float), `review` (Text), and a general `is_favorite` flag to `Watched`. Implemented `CustomList`, `CustomListMovie` (association), and the separate `UserFavorite` table for pinning Top 4 movies. Explicitly noted how `TMDBService.get_movie_details()` parses Watch Provider data. Expanded `User` fields to include `avatar_url` and bio information.

### Short Explanation for Report:
*This UML class diagram highlights the relational data structure implemented via SQLAlchemy. It shows the core One-to-Many relationships between Users and their independent Watchlists, Watched logs, Custom Lists, and specific pinned Favorites, illustrating how service modules interact with these strictly defined schemas.*

**Generation constraints:**
- Keep all labels readable.
- Do not overcrowd the diagram.
- Use clear directional arrows.
- Do not invent components.
- Use only components listed in this specification.
- Keep terminology identical across all four diagrams.

---

## Final Verified Component Inventory

### Frontend Pages / Interfaces
- Home Page (`main/index.html`)
- Movie Detail Page (`main/movie_detail.html`)
- TV Detail Page (`main/tv_detail.html`)
- Person/Actor/Director Detail Page (`profiles/person.html` / `directors/director.html`)
- Studio/Company Page (`profiles/studio.html`)
- Profile Page (`profiles/profile.html`)
- Settings Page (`auth/settings.html` - manages UserFavorites)
- Avatar Page (`auth/avatar.html`)
- Films / Watchlist Page (`watchlist/films.html`)
- View Custom List Page (`lists/view_list.html`)
- Recommendations Page
- Analytics Dashboard Page

### Backend Modules / Services
- `auth.py`: Authentication, Settings, & Top 4 Favorites Blueprint
- `main.py`: Main Navigation, Movie/TV Pages & Search Blueprint
- `watchlist.py`: Watchlist, Watch History, Reviews, & General Likes Blueprint
- `lists.py`: Custom Lists Blueprint
- `directors.py` & `profiles.py`: Personnel & Studio Blueprint
- `analytics.py`: Analytics & Graphs Blueprint
- `tmdb.py`: TMDB API & Watch Providers Service
- `recommendations.py`: Vector Math Service

### Database Models
- `User`: id, username, email, password_hash, given_name, family_name, bio, avatar_url.
- `Watchlist`: id, user_id, tmdb_id, title, added_at.
- `Watched`: id, user_id, tmdb_id, title, rating, review, is_favorite, watched_at.
- `CustomList`: id, user_id, name, description, created_at.
- `CustomListMovie`: id, list_id, tmdb_id, title.
- `UserFavorite`: id, user_id, tmdb_id, title, order.
- `APICache`: url_key, response_text, created_at.

### External APIs
- TMDB REST API: Fetches movie details, TV details, actor/director details, studio/company movies, watch providers (extracted directly inside the details requests), search results, and trending media.

### Processing / Algorithms
- Content-Based Recommendation: Pandas Vectorizer and Cosine Similarity calculation.
- Data Analytics: Plotly graph generation.

### Deployment
- **Configured (Production Preparation):** Gunicorn WSGI server.
- **Target (Planned/Pending):** Render/Railway cloud hosting.

### Features Added After Reporting 2
- Independent Mark as Watched functionality (`Watched` table).
- 0.5 increment ratings (`rating` Float field).
- Written movie reviews (`review` Text field).
- General likes/hearts (`is_favorite` Boolean in `Watched`).
- Top 4 Pinned Favorites (`UserFavorite` table).
- Custom Lists creation and browsing (`CustomList` table).
- Actor/Director/Studio profile pages.
- Where-to-Watch provider extraction.
- User Settings and Avatar pages.

### Features Still Planned
- Live cloud deployment and domain configuration.
- Collaborative filtering recommendations.
