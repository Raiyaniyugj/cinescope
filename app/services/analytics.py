import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime
from app.services.tmdb import tmdb_service
from app.models import Watched

# Set style template
pio.templates.default = "plotly_dark"

def apply_dark_theme(fig):
    """Formats a Plotly figure to fit CineScope's Letterboxd-like dark theme."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9ab', family='Inter, system-ui, sans-serif'),
        title_font=dict(color='#ffffff', size=16, family='Outfit, sans-serif'),
        legend=dict(
            bgcolor='#14181c',
            bordercolor='#2c3440',
            borderwidth=1,
            font=dict(color='#9ab')
        ),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    fig.update_xaxes(
        gridcolor='#202830',
        linecolor='#2c3440',
        zerolinecolor='#202830',
        tickfont=dict(color='#9ab')
    )
    fig.update_yaxes(
        gridcolor='#202830',
        linecolor='#2c3440',
        zerolinecolor='#202830',
        tickfont=dict(color='#9ab')
    )
    return fig

class AnalyticsService:
    """Service to handle generating interactive data visualization dashboards."""

    @staticmethod
    def generate_genre_dashboard():
        """Generates plots for the general Genre Analytics page."""
        # Get popular movies as dataset
        movies = tmdb_service.get_popular_movies()
        if not movies:
            return {}

        # Enrich movies with complete genres list
        rich_movies = []
        for m in movies[:30]:  # Limit to 30 for performance
            details = tmdb_service.get_movie_details(m['id'])
            if details:
                rich_movies.append(details)

        if not rich_movies:
            return {}

        # Construct DataFrame
        df_list = []
        for rm in rich_movies:
            year = rm.get('release_date', '2020-01-01')[:4]
            try:
                year = int(year)
            except Exception:
                year = 2020
            
            for g in rm.get('genres', []):
                df_list.append({
                    "title": rm.get('title'),
                    "rating": rm.get('vote_average', 0),
                    "popularity": rm.get('popularity', 0),
                    "genre": g['name'],
                    "year": year
                })

        df = pd.DataFrame(df_list)

        # 1. Donut Chart - Genre Popularity (Distribution of Count)
        genre_counts = df['genre'].value_counts().reset_index()
        genre_counts.columns = ['Genre', 'Count']
        fig_dist = px.pie(
            genre_counts, values='Count', names='Genre', hole=0.4,
            title='Genre Distribution in Popular Releases',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_dist = apply_dark_theme(fig_dist)

        # 2. Horizontal Bar - Average Rating per Genre
        genre_ratings = df.groupby('genre')['rating'].mean().reset_index().sort_values(by='rating', ascending=True)
        genre_ratings.columns = ['Genre', 'Avg Rating']
        fig_rating = px.bar(
            genre_ratings, x='Avg Rating', y='Genre', orientation='h',
            title='Highest Rated Genres',
            color='Avg Rating',
            color_continuous_scale='Viridis'
        )
        fig_rating = apply_dark_theme(fig_rating)
        fig_rating.update_layout(coloraxis_showscale=False)

        # 3. Line Chart - Genre Trends Over Release Years
        genre_trends = df.groupby(['year', 'genre']).size().reset_index(name='count')
        # Filter top 5 genres for clarity
        top_genres = df['genre'].value_counts().head(5).index
        genre_trends = genre_trends[genre_trends['genre'].isin(top_genres)]
        fig_trend = px.line(
            genre_trends, x='year', y='count', color='genre',
            title='Top 5 Genre Trends Over Years',
            markers=True
        )
        fig_trend = apply_dark_theme(fig_trend)

        return {
            "dist_chart": pio.to_html(fig_dist, full_html=False, include_plotlyjs='cdn'),
            "rating_chart": pio.to_html(fig_rating, full_html=False, include_plotlyjs=False),
            "trend_chart": pio.to_html(fig_trend, full_html=False, include_plotlyjs=False)
        }

    @staticmethod
    def generate_revenue_dashboard():
        """Generates plots for the general Revenue and Economics dashboard."""
        movies = tmdb_service.get_top_grossing_movies(25)
        if not movies:
            return {}

        df_list = []
        for m in movies:
            df_list.append({
                "title": m.get('title'),
                "budget": m.get('budget', 0) / 1000000.0, # in Millions
                "revenue": m.get('revenue', 0) / 1000000.0, # in Millions
                "rating": m.get('vote_average', 0),
                "year": m.get('release_date', '2020-01-01')[:4]
            })

        df = pd.DataFrame(df_list)
        # Filter zero values for meaningful calculations
        df_filtered = df[(df['budget'] > 0) & (df['revenue'] > 0)]

        # 1. Bar Chart - Top Grossing Movies
        top_grossing = df.sort_values(by='revenue', ascending=False).head(10)
        fig_gross = px.bar(
            top_grossing, x='revenue', y='title', orientation='h',
            title='Top Grossing Releases ($ Millions)',
            labels={"revenue": "Revenue ($M)", "title": "Movie"},
            color='revenue', color_continuous_scale='Cividis'
        )
        fig_gross = apply_dark_theme(fig_gross)
        fig_gross.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)

        # 2. Scatter Plot - Revenue vs rating
        fig_scatter = px.scatter(
            df_filtered, x='rating', y='revenue', size='budget', hover_name='title',
            title='Revenue vs. Rating (Size = Budget)',
            labels={"rating": "Vote Average", "revenue": "Revenue ($M)"},
            color='revenue', color_continuous_scale='Viridis'
        )
        fig_scatter = apply_dark_theme(fig_scatter)
        fig_scatter.update_layout(coloraxis_showscale=False)

        # 3. Stacked/Grouped Bar - Budget vs Revenue (Top 10 sorted by revenue)
        comp_df = df_filtered.sort_values(by='revenue', ascending=False).head(10)
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(x=comp_df['title'], y=comp_df['budget'], name='Budget ($M)', marker_color='#ff8000'))
        fig_comp.add_trace(go.Bar(x=comp_df['title'], y=comp_df['revenue'], name='Revenue ($M)', marker_color='#00c030'))
        fig_comp.update_layout(
            barmode='group',
            title='Budget vs. Revenue (Top 10 High Performers)',
            xaxis_tickangle=-45
        )
        fig_comp = apply_dark_theme(fig_comp)

        return {
            "gross_chart": pio.to_html(fig_gross, full_html=False, include_plotlyjs='cdn'),
            "scatter_chart": pio.to_html(fig_scatter, full_html=False, include_plotlyjs=False),
            "comp_chart": pio.to_html(fig_comp, full_html=False, include_plotlyjs=False)
        }

    @staticmethod
    def generate_director_dashboard(director_id):
        """Generates analysis plots for a single director profile."""
        director = tmdb_service.get_director_details(director_id)
        if not director or 'movies' not in director:
            return {}

        raw_movies = director['movies']
        df_list = []

        # Gather detailed records for budget/revenue (max 10 for speed)
        for m in raw_movies[:10]:
            details = tmdb_service.get_movie_details(m['id'])
            if details:
                year = details.get('release_date', '')[:4]
                try:
                    year = int(year)
                except ValueError:
                    year = None
                
                df_list.append({
                    "title": details.get('title'),
                    "rating": details.get('vote_average', 0),
                    "budget": details.get('budget', 0) / 1000000.0,
                    "revenue": details.get('revenue', 0) / 1000000.0,
                    "genres": [g['name'] for g in details.get('genres', [])],
                    "year": year
                })

        if not df_list:
            return {}

        df = pd.DataFrame(df_list).dropna(subset=['year']).sort_values(by='year')

        # 1. Line Plot: Rating Trend Over Career
        fig_ratings = px.line(
            df, x='year', y='rating', text='title', markers=True,
            title="Movie Ratings Trend Over Career",
            labels={"year": "Release Year", "rating": "Average Rating"}
        )
        fig_ratings.update_traces(textposition="top center")
        fig_ratings = apply_dark_theme(fig_ratings)

        # 2. Bar Chart: Revenue Performance ($ Millions)
        fig_revenue = px.bar(
            df, x='title', y='revenue',
            title='Revenue ($ Millions) per Release',
            labels={"revenue": "Revenue ($M)", "title": "Movie"},
            color='revenue', color_continuous_scale='GnBu'
        )
        fig_revenue = apply_dark_theme(fig_revenue)
        fig_revenue.update_layout(xaxis_tickangle=-30, coloraxis_showscale=False)

        # 3. Pie/Donut Chart: Director's Genre Distribution
        genres_exploded = []
        for r in df_list:
            genres_exploded.extend(r['genres'])
        
        df_genres = pd.DataFrame(genres_exploded, columns=['Genre'])
        genre_dist = df_genres['Genre'].value_counts().reset_index()
        genre_dist.columns = ['Genre', 'Count']
        fig_genres = px.pie(
            genre_dist, values='Count', names='Genre', hole=0.5,
            title="Genre Preference Distribution",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_genres = apply_dark_theme(fig_genres)

        return {
            "ratings_chart": pio.to_html(fig_ratings, full_html=False, include_plotlyjs='cdn'),
            "revenue_chart": pio.to_html(fig_revenue, full_html=False, include_plotlyjs=False),
            "genres_chart": pio.to_html(fig_genres, full_html=False, include_plotlyjs=False)
        }

    @staticmethod
    def generate_director_comparison(dir1_id, dir2_id):
        """Generates plots comparing two directors using pre-fetched movie data."""
        dir1 = tmdb_service.get_director_details(dir1_id)
        dir2 = tmdb_service.get_director_details(dir2_id)
        if not dir1 or not dir2:
            return {}

        def get_director_df(director):
            df_list = []
            for m in director.get('movies', []):
                rating = m.get('vote_average', 0)
                if rating and rating > 0:
                    df_list.append({
                        "director": director['name'],
                        "title": m.get('title', 'Unknown'),
                        "rating": rating,
                        "year": m.get('release_date', '')[:4] if m.get('release_date') else '',
                    })
            return pd.DataFrame(df_list)

        df1 = get_director_df(dir1)
        df2 = get_director_df(dir2)

        if df1.empty or df2.empty:
            return {}

        df_all = pd.concat([df1, df2])

        # 1. Rating Distribution (Box Plot)
        fig_box = px.box(
            df_all, x='director', y='rating', color='director',
            title='Ratings Distribution Comparison',
            labels={"director": "Director", "rating": "TMDB Rating"},
            color_discrete_map={dir1['name']: '#00c030', dir2['name']: '#ff8000'}
        )
        fig_box = apply_dark_theme(fig_box)

        # 2. Average Rating Comparison (Bar)
        avg_df = df_all.groupby('director')['rating'].agg(['mean', 'count']).reset_index()
        avg_df.columns = ['director', 'avg_rating', 'film_count']
        fig_avg = go.Figure()
        fig_avg.add_trace(go.Bar(
            x=avg_df['director'], y=avg_df['avg_rating'],
            text=[f"{r:.1f} ({c} films)" for r, c in zip(avg_df['avg_rating'], avg_df['film_count'])],
            textposition='auto',
            marker_color=['#00c030', '#ff8000']
        ))
        fig_avg.update_layout(title='Average Rating & Film Count')
        fig_avg = apply_dark_theme(fig_avg)

        # 3. Ratings Over Time (Line)
        df_all_sorted = df_all.sort_values('year')
        fig_timeline = px.line(
            df_all_sorted, x='year', y='rating', color='director',
            title='Rating Trends Over Career',
            markers=True, text='title',
            color_discrete_map={dir1['name']: '#00c030', dir2['name']: '#ff8000'}
        )
        fig_timeline.update_traces(textposition='top center', textfont_size=8)
        fig_timeline = apply_dark_theme(fig_timeline)

        return {
            "box_chart": pio.to_html(fig_box, full_html=False, include_plotlyjs='cdn'),
            "financials_chart": pio.to_html(fig_avg, full_html=False, include_plotlyjs=False),
            "genres_chart": pio.to_html(fig_timeline, full_html=False, include_plotlyjs=False),
            "dir1_name": dir1['name'],
            "dir2_name": dir2['name']
        }

    @staticmethod
    def generate_cinephile_dashboard(user_id):
        """Generates user-specific statistics and plots for their dashboard."""
        watched_items = Watched.query.filter_by(user_id=user_id).all()
        if not watched_items:
            return {}

        df_list = []
        for item in watched_items:
            m_details = tmdb_service.get_movie_details(item.tmdb_id)
            # Find release year and decade
            year = item.release_date[:4] if item.release_date else "2020"
            try:
                year_val = int(year)
                decade = f"{(year_val // 10) * 10}s"
            except Exception:
                decade = "2020s"
            
            genres = [g['name'] for g in m_details.get('genres', [])] if m_details else []
            director = m_details.get('director', {}).get('name') if (m_details and m_details.get('director')) else None
            runtime = m_details.get('runtime', 120) if m_details else 120
            
            # Month watched
            month_watched = item.watched_at.strftime('%Y-%m') if item.watched_at else "Unknown"

            df_list.append({
                "title": item.title,
                "user_rating": item.rating if item.rating else 0,
                "decade": decade,
                "genres": genres,
                "director": director,
                "runtime": runtime,
                "month_watched": month_watched
            })

        df = pd.DataFrame(df_list)

        # 1. Decade Distribution (Bar Chart)
        decade_counts = df['decade'].value_counts().reset_index()
        decade_counts.columns = ['Decade', 'Count']
        decade_counts = decade_counts.sort_values(by='Decade')
        fig_decades = px.bar(
            decade_counts, x='Decade', y='Count',
            title='Watched Movies by Release Decade',
            color='Count', color_continuous_scale='Purples'
        )
        fig_decades = apply_dark_theme(fig_decades)
        fig_decades.update_layout(coloraxis_showscale=False)

        # 2. Rating Distribution (Histogram)
        # Using 0.5 increments for new rating system
        fig_ratings = px.histogram(
            df, x='user_rating', nbins=10, range_x=[0.25, 5.25],
            title='Your Personal Rating Distribution',
            labels={"user_rating": "Rating Logged"},
            color_discrete_sequence=['#00c030']
        )
        fig_ratings.update_layout(
            xaxis=dict(tickmode='linear', tick0=0.5, dtick=0.5),
            yaxis_title="Count"
        )
        fig_ratings = apply_dark_theme(fig_ratings)

        # 3. Favorite Genres Donut
        all_genres = []
        for genres in df['genres']:
            all_genres.extend(genres)
        df_genres = pd.DataFrame(all_genres, columns=['Genre'])
        fav_genres = df_genres['Genre'].value_counts().head(5).reset_index()
        fav_genres.columns = ['Genre', 'Count']
        
        fig_fav_genres = px.pie(
            fav_genres, values='Count', names='Genre', hole=0.5,
            title='Your Top Genres',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_fav_genres = apply_dark_theme(fig_fav_genres)

        # 4. Favorite Directors Bar
        fav_directors = df['director'].dropna().value_counts().head(5).reset_index()
        fav_directors.columns = ['Director', 'Count']
        fig_fav_dirs = px.bar(
            fav_directors, x='Count', y='Director', orientation='h',
            title='Your Most Watched Directors',
            color='Count', color_continuous_scale='Burg'
        )
        fig_fav_dirs = apply_dark_theme(fig_fav_dirs)
        fig_fav_dirs.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)

        # 5. Watching Activity By Month
        month_counts = df['month_watched'].value_counts().reset_index()
        month_counts.columns = ['Month', 'Count']
        month_counts = month_counts[month_counts['Month'] != 'Unknown'].sort_values(by='Month')
        fig_activity = px.bar(
            month_counts, x='Month', y='Count',
            title='Watching Activity By Month',
            color_discrete_sequence=['#ff8000']
        )
        fig_activity = apply_dark_theme(fig_activity)

        # 6. Runtime Distribution
        fig_runtime = px.histogram(
            df, x='runtime', nbins=15,
            title='Runtime Distribution (Minutes)',
            labels={"runtime": "Runtime (m)"},
            color_discrete_sequence=['#1DB954']
        )
        fig_runtime = apply_dark_theme(fig_runtime)

        # Get text stats
        total_watched = len(watched_items)
        avg_rating = df[df['user_rating'] > 0]['user_rating'].mean()
        total_watch_time = df['runtime'].sum()
        top_genre = fav_genres['Genre'].iloc[0] if not fav_genres.empty else "N/A"
        top_director = fav_directors['Director'].iloc[0] if not fav_directors.empty else "N/A"
        top_decade = decade_counts.sort_values(by='Count', ascending=False)['Decade'].iloc[0] if not decade_counts.empty else "N/A"

        return {
            "decades_chart": pio.to_html(fig_decades, full_html=False, include_plotlyjs='cdn'),
            "ratings_chart": pio.to_html(fig_ratings, full_html=False, include_plotlyjs=False),
            "genres_chart": pio.to_html(fig_fav_genres, full_html=False, include_plotlyjs=False),
            "dirs_chart": pio.to_html(fig_fav_dirs, full_html=False, include_plotlyjs=False),
            "activity_chart": pio.to_html(fig_activity, full_html=False, include_plotlyjs=False),
            "runtime_chart": pio.to_html(fig_runtime, full_html=False, include_plotlyjs=False),
            "stats": {
                "total_watched": total_watched,
                "total_watch_time": int(total_watch_time),
                "avg_rating": round(avg_rating, 2) if not pd.isna(avg_rating) else 0.0,
                "top_genre": top_genre,
                "top_director": top_director,
                "top_decade": top_decade
            }
        }
