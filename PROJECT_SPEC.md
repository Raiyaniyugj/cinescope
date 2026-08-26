# PROJECT_SPEC.md - CineScope Implementation Roadmap for Reporting 2

This document serves as the master checklist and implementation roadmap for **CineScope**. It aligns directly with the "Reporting 2" template to ensure every requirement is met with concrete project artifacts.

---

## 3b) Brief Overview of Work Completed After Reporting 1

To honestly complete this section, the following work must be fully finished in the project:

### Development Completed
- **Movie Explorer Module**: Fully functional Home page (trending/popular), robust Search functionality, and dynamic Movie Detail pages.
- **Personal Watchlist System**: Backend and UI allowing users to add/remove movies, toggle "watched" status, and provide ratings (1-10).
- **Recommendation Engine**: Integration of a content-based recommendation system that suggests movies to the user based on their highly-rated watchlist items.
- **Analytics Dashboards**: Four interactive dashboards built with Plotly integrated into Flask:
  1. Genre Distribution
  2. Revenue Trends
  3. Director Analytics
  4. Cinephile (User Activity/History) Dashboard
- **UI/UX Theming**: Final front-end polish using Bootstrap 5.3, ensuring a responsive, modern "movie platform" aesthetic across all templates.

### Research Completed
- Algorithm selection and validation for the recommendation engine (Cosine Similarity vs. other content-based approaches).
- Evaluation of Plotly.js integration methods within Jinja2 templates (e.g., passing JSON encoded graphs).

### Implementation Finished
- Seamless flow of data from the TMDB API -> Data Processing (Pandas/NumPy) -> Visualization (Plotly) -> Frontend Presentation.

---

## 3c) System Architecture / Workflow Diagram

You must create and save the following diagrams (e.g., in an `assets/` or `docs/diagrams/` folder) to attach to the report:

- **System Architecture Diagram**: A high-level block diagram illustrating the interaction between the Client Browser, Flask App (Blueprints), SQLite Database (SQLAlchemy), TMDB API, and the Data/Analytics Engine (Pandas/Plotly).
- **User Workflow / State Diagram**: A flowchart tracking a user's journey: `Login -> Browse Movies -> View Details -> Add to Watchlist -> View Recommendations -> Explore Analytics`.
- **UML/ER Diagrams**:
  - **ER Diagram**: Detailed schema showing the `User`, `Watchlist`, and `APICache` tables, including primary/foreign keys and relationships (1-to-many).
  - **Sequence Diagram**: The exact data flow for generating a recommendation (User requests -> System fetches watchlist -> System computes cosine similarity -> System fetches metadata -> UI renders).

---

## 3d) Modules Completed / Features Implemented

The project must reflect these modules in its codebase (e.g., in `app/routes/`):

| Module Name | Description (What should exist in code) | Target Status for Report 2 | Dependencies |
| :--- | :--- | :--- | :--- |
| **Movie Explorer** | Routes for home (`/`), search (`/search`), and movie details (`/movie/<id>`). | Completed | TMDB API, APICache |
| **Personal Watchlist** | Routes/DB logic for adding, removing, marking watched, and rating movies. | Completed | User Auth, Database |
| **Recommendation Engine** | Pandas/NumPy logic calculating cosine similarity based on user's watched/rated movies. | Completed | Watchlist, TMDB API |
| **Analytics Dashboards** | Plotly generation logic for Genre, Revenue, Director, and User Activity charts. | Completed | Pandas, Database, TMDB |
| **UI/UX Theming** | Base template, navbars, and responsive layouts utilizing Bootstrap 5.3. | Completed | HTML/CSS/JS |

---

## 3e) Tools and Technologies Used

Ensure the final codebase genuinely utilizes these technologies:

- **Programming Language**: Python 3.x, JavaScript (ES6+)
- **Framework**: Flask (Web Framework), Bootstrap 5.3 (CSS Framework)
- **Database**: SQLite (via Flask-SQLAlchemy)
- **Hardware/Software Tools**: VS Code, Git/GitHub, Web Browser (Chrome/Firefox)
- **Other Technologies**: TMDB REST API, Pandas, NumPy, Plotly (for data visualization), Werkzeug (Security/Hashing), Flask-Login, Jinja2 (Templating)

---

## 4. Implementation Description

To write this section convincingly, the codebase must demonstrate:

- **Algorithm / Method Followed**: You must implement and be able to explain the Content-Based Filtering algorithm using Cosine Similarity (e.g., comparing movie feature vectors like genres, cast, and keywords).
- **Coding / Development Details**: The project must strictly adhere to the Flask Application Factory pattern and use Blueprints (`auth`, `main`, `movies`, `analytics`, `directors`) for modularity.
- **Database Design**: The SQLAlchemy models (`app/models.py`) must cleanly define `User`, `Watchlist` (with `watched` boolean and `rating` integer), and `APICache`.
- **API Integration**: Code showing the TMDB API wrapper (`app/utils/tmdb.py`), how the 24-hour caching mechanism works to intercept requests, and the fallback mechanism.
- **Testing Performed**: Evidence of basic unit tests (e.g., `tests/test_models.py`, `tests/test_auth.py`) or documented manual end-to-end testing scenarios.
- **Folder Structure**: A clean MVC-like structure must be present:
  ```text
  cinescope/
  ├── app/
  │   ├── models/ (Database schema)
  │   ├── routes/ (Blueprints)
  │   ├── templates/ (Jinja2 HTML)
  │   ├── static/ (CSS/JS/Images)
  │   └── utils/ (API, Recommender, Plotly logic)
  ├── tests/
  ├── config.py
  └── run.py
  ```

---

## 5. Results / Output Screenshots

You must capture the following screenshots from the running application. *Ensure the app looks visually polished before capturing.*

1. **Screenshot 1: Movie Explorer (Home Page)**
   - *Demonstrates*: Trending movies fetching correctly, dynamic UI, functional search bar.
2. **Screenshot 2: Movie Detail Page**
   - *Demonstrates*: Comprehensive TMDB metadata rendering, posters, and the "Add to Watchlist" interactive element.
3. **Screenshot 3: Personal Watchlist**
   - *Demonstrates*: User-specific database tracking, toggle switches for watched status, and numerical ratings.
4. **Screenshot 4: Recommendation Engine Output**
   - *Demonstrates*: The algorithmic output. Movies suggested specifically based on the items in the user's watchlist.
5. **Screenshot 5: Analytics Dashboards (e.g., Genre or Revenue)**
   - *Demonstrates*: Interactive Plotly charts seamlessly embedded in the Flask template.
6. **Screenshot 6: Cinephile / User Profile Dashboard**
   - *Demonstrates*: Custom data aggregation showing the user's personal movie-watching habits.

---

## 6. Challenges Faced and Solutions

The implementation must justify these common development challenges:

| Potential Challenge | Required Implementation Solution in Code |
| :--- | :--- |
| **TMDB API Rate Limiting & Latency** | Implementation of a custom `APICache` database model that intercepts identical requests for 24 hours. |
| **Recommendation Processing Speed** | Utilizing vectorized operations in Pandas/NumPy rather than pure Python `for` loops to calculate Cosine Similarity matrices quickly. |
| **Rendering Dynamic Charts in Flask** | Serializing Plotly graph objects using `plotly.utils.PlotlyJSONEncoder` in the backend and parsing them securely in the Jinja frontend. |

---

## 7. Tasks in Progress / Next Month Plan

To show ongoing momentum, keep these items clearly pending (or in a separate branch):

- **Remaining Modules**: Integration of a user review/commenting system.
- **Testing Plan**: Expanding unit test coverage and performing cross-browser compatibility checks.
- **Documentation Work**: Writing the final comprehensive project report and a detailed `README.md` for the repository.
- **Deployment Plan**: Preparing the application for cloud deployment (e.g., Render or Railway) and migrating from SQLite to PostgreSQL for production environments.

---

## 8. Learning / Skills Acquired

Ensure you can comfortably speak to these concepts during your evaluation based on the code written:

- **Technical Skills**: Advanced Flask routing (Blueprints, app context), ORM database management (SQLAlchemy), Data processing and matrix operations (Pandas/NumPy), Interactive web visualization (Plotly), and secure third-party API integration.
- **Professional Skills**: Modular software architecture, debugging complex data pipelines, translating UI/UX concepts into Bootstrap, and writing technical documentation.

---

## 9. References

Ensure you have utilized and can cite these in your final report:

- [1] Flask Documentation, https://flask.palletsprojects.com/
- [2] TMDB API Developer Portal, https://developer.themoviedb.org/docs
- [3] Plotly Open Source Graphing Library for Python, https://plotly.com/python/
- [4] SQLAlchemy 2.0 Documentation, https://docs.sqlalchemy.org/
- [5] Include at least one Medium/Towards Data Science article or academic paper on "Content-Based Filtering using Cosine Similarity".

---

## Additional Project Artifacts to Prepare (For Maximum Evaluation Marks)

To secure an "Excellent (20)" evaluation, ensure the following exist in the project repository, even if not strictly in the template:

1. **`requirements.txt`**: A clean, updated list of dependencies for easy reproduction.
2. **`README.md`**: A professional repository guide with setup instructions, features list, and screenshots.
3. **Demo Data Script**: A script (e.g., `seed.py`) that pre-populates the database with demo users, watchlists, and cached API data so evaluators can test the app immediately without hitting rate limits.
4. **Git Commit History**: A consistent history showing iterative development (not just one giant commit at the end).
