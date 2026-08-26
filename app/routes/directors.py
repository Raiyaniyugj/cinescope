from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services.tmdb import tmdb_service
from app.services.analytics import AnalyticsService

directors_bp = Blueprint('directors', __name__, url_prefix='/directors')

@directors_bp.route('/')
def index():
    query = request.args.get('q', '').strip()
    results = []
    popular = []

    if query:
        results = tmdb_service.search_directors(query)
    else:
        # Show popular directors when no search
        popular = tmdb_service.get_popular_directors()

    return render_template('directors/index.html', query=query, results=results, popular=popular)


@directors_bp.route('/profile/<int:director_id>')
def profile(director_id):
    director = tmdb_service.get_director_details(director_id)
    if not director:
        flash('Director not found.', 'danger')
        return redirect(url_for('directors.index'))

    charts = AnalyticsService.generate_director_dashboard(director_id)

    # All movies directed (from TMDB credits)
    all_movies = director.get('movies', [])
    total_movies = len(all_movies)

    # Compute stats from the basic movie data (no need to fetch each one individually)
    avg_rating = 0.0
    total_revenue = 0
    ratings = [m.get('vote_average', 0) for m in all_movies if m.get('vote_average') and m.get('vote_average') > 0]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0.0

    return render_template(
        'directors/profile.html',
        director=director,
        charts=charts,
        movies=all_movies,
        total_movies=total_movies,
        avg_rating=avg_rating,
        total_revenue=total_revenue
    )


@directors_bp.route('/compare')
def compare():
    dir1_id = request.args.get('dir1')
    dir2_id = request.args.get('dir2')

    charts = {}
    dir1 = None
    dir2 = None

    if dir1_id and dir2_id:
        try:
            dir1_id = int(dir1_id)
            dir2_id = int(dir2_id)
        except ValueError:
            flash('Invalid director IDs.', 'danger')
            return redirect(url_for('directors.index'))

        dir1 = tmdb_service.get_director_details(dir1_id)
        dir2 = tmdb_service.get_director_details(dir2_id)

        if not dir1 or not dir2:
            flash('One or both directors could not be found.', 'danger')
            return redirect(url_for('directors.index'))

        charts = AnalyticsService.generate_director_comparison(dir1_id, dir2_id)

    return render_template(
        'directors/compare.html',
        charts=charts,
        dir1=dir1,
        dir2=dir2
    )


@directors_bp.route('/search_api')
def search_api():
    """API endpoint for director search autocomplete."""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])

    results = tmdb_service.search_directors(query)
    return jsonify([{
        'id': d.get('id'),
        'name': d.get('name'),
        'profile_path': d.get('profile_path', '')
    } for d in results[:8]])
