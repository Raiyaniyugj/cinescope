from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.services.analytics import AnalyticsService
from app.services.tmdb import tmdb_service

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/genres')
def genres():
    charts = AnalyticsService.generate_genre_dashboard()
    return render_template('analytics/genres.html', charts=charts)


@analytics_bp.route('/revenue')
def revenue():
    charts = AnalyticsService.generate_revenue_dashboard()
    return render_template('analytics/revenue.html', charts=charts)


@analytics_bp.route('/cinephile')
@login_required
def cinephile():
    data = AnalyticsService.generate_cinephile_dashboard(current_user.id)
    return render_template('analytics/cinephile.html', data=data)


@analytics_bp.route('/compare-movies')
def compare_movies():
    """Compare two movies side by side."""
    m1_id = request.args.get('m1')
    m2_id = request.args.get('m2')

    movie1 = None
    movie2 = None

    if m1_id and m2_id:
        try:
            movie1 = tmdb_service.get_movie_details(int(m1_id))
            movie2 = tmdb_service.get_movie_details(int(m2_id))
        except (ValueError, TypeError):
            pass

    return render_template('analytics/compare_movies.html', movie1=movie1, movie2=movie2)


@analytics_bp.route('/movie_search_api')
def movie_search_api():
    """API endpoint for movie search autocomplete."""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])

    results = tmdb_service.search_movies(query)
    return jsonify([{
        'id': m.get('id'),
        'title': m.get('title'),
        'year': m.get('release_date', '')[:4] if m.get('release_date') else '',
        'poster_path': m.get('poster_path', ''),
        'vote_average': m.get('vote_average', 0)
    } for m in results[:8]])

