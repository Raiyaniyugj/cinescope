import pandas as pd
import numpy as np
from app.models import Watchlist, Watched
from app.services.tmdb import tmdb_service

class RecommendationEngine:
    """Content-based Recommendation Engine powered by Pandas and NumPy."""

    @staticmethod
    def get_recommendations(user_id, num_recommendations=8):
        """Generates content-based movie recommendations for a user based on watchlist history."""
        # 1. Fetch user's watched history
        watched_items = Watched.query.filter_by(user_id=user_id).all()
        
        # If user has no watched history, recommend popular trending movies
        if not watched_items:
            trending = tmdb_service.get_trending_movies()
            return trending[:num_recommendations]

        # Get set of all movies currently in user's watchlist/history to filter them out later
        user_watchlist = Watchlist.query.filter_by(user_id=user_id).all()
        user_movie_ids = {item.tmdb_id for item in watched_items + user_watchlist}

        # 2. Build User Preference Profile using Pandas
        # Extract watched movie details
        watched_details = []
        for item in watched_items:
            m_details = tmdb_service.get_movie_details(item.tmdb_id)
            if m_details:
                # Use user rating (1-10) as weight; default to 6 if not rated
                weight = item.rating if item.rating else 6
                watched_details.append({
                    "id": m_details["id"],
                    "genres": [g["name"] for g in m_details.get("genres", [])],
                    "director": m_details.get("director", {}).get("name") if m_details.get("director") else None,
                    "weight": weight
                })

        if not watched_details:
            return tmdb_service.get_trending_movies()[:num_recommendations]

        # Construct profile dataframe
        df_history = pd.DataFrame(watched_details)

        # Calculate genre preference weights
        genre_weights = {}
        director_weights = {}

        for _, row in df_history.iterrows():
            w = row["weight"]
            # Genres weight accumulation
            for genre in row["genres"]:
                genre_weights[genre] = genre_weights.get(genre, 0) + w
            # Director weight accumulation
            if row["director"]:
                director_weights[row["director"]] = director_weights.get(row["director"], 0) + w

        # Convert to Pandas Series and normalize
        s_genres = pd.Series(genre_weights, dtype=float)
        s_directors = pd.Series(director_weights, dtype=float)

        if not s_genres.empty:
            s_genres = s_genres / s_genres.sum()
        if not s_directors.empty:
            s_directors = s_directors / s_directors.sum()

        # 3. Gather candidate movies from TMDB (Trending + Popular + Discover from top genre)
        candidates = []
        seen_candidates = set()

        # Add trending and popular
        raw_candidates = tmdb_service.get_trending_movies() + tmdb_service.get_popular_movies()
        
        # Add discover movies of top genre to get wider inventory
        if not s_genres.empty:
            top_genre_name = s_genres.idxmax()
            # Map genre name to TMDB ID (standard mapping)
            genre_map = {
                "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35,
                "Crime": 80, "Documentary": 99, "Drama": 18, "Family": 10751,
                "Fantasy": 14, "History": 36, "Horror": 27, "Music": 10402,
                "Mystery": 9648, "Romance": 10749, "Sci-Fi": 878, "Science Fiction": 878,
                "TV Movie": 10770, "Thriller": 53, "War": 10752, "Western": 37
            }
            top_genre_id = genre_map.get(top_genre_name)
            if top_genre_id:
                raw_candidates += tmdb_service.get_movies_by_genre(top_genre_id)

        # De-duplicate raw candidates and filter out already added movies
        for item in raw_candidates:
            c_id = item["id"]
            if c_id not in user_movie_ids and c_id not in seen_candidates:
                seen_candidates.add(c_id)
                # Fetch full details to get genres and directors for scoring
                details = tmdb_service.get_movie_details(c_id)
                if details:
                    candidates.append(details)

        if not candidates:
            # Fallback if no fresh candidates (e.g. if database is small or user has added everything)
            return []

        # 4. Vectorized Scoring of Candidates
        # Combine all features (genres & directors) into a single feature space index
        all_features = list(s_genres.index) + list(s_directors.index)
        
        # Build user profile vector
        user_vector = np.zeros(len(all_features))
        for i, feat in enumerate(all_features):
            if feat in s_genres.index:
                user_vector[i] = s_genres[feat] * 0.6  # Genre weight = 60%
            elif feat in s_directors.index:
                user_vector[i] = s_directors[feat] * 0.4  # Director weight = 40%

        # Build candidate feature matrix using Pandas
        candidate_rows = []
        for c in candidates:
            c_genres = [g["name"] for g in c.get("genres", [])]
            c_dir = c.get("director", {}).get("name") if c.get("director") else None
            
            c_row = np.zeros(len(all_features))
            for i, feat in enumerate(all_features):
                if feat in c_genres:
                    c_row[i] = 1.0
                elif feat == c_dir:
                    c_row[i] = 1.0
            candidate_rows.append(c_row)

        df_candidates_features = pd.DataFrame(candidate_rows, columns=all_features)
        
        # Perform matrix multiplication using NumPy: score = Feature Matrix * User Profile Vector
        feature_matrix = df_candidates_features.to_numpy()
        scores = np.dot(feature_matrix, user_vector)

        # Assign scores back to candidates list
        scored_candidates = []
        for idx, score in enumerate(scores):
            movie = candidates[idx]
            # Add small rating bonus to candidate score
            rating_bonus = (movie.get("vote_average", 0) / 10.0) * 0.1
            scored_candidates.append({
                "movie": tmdb_service._minify_movie(movie),
                "score": float(score) + rating_bonus
            })

        # Sort by score descending
        scored_candidates = sorted(scored_candidates, key=lambda x: x["score"], reverse=True)
        
        # Return the top recommended movie objects
        return [item["movie"] for item in scored_candidates[:num_recommendations]]
