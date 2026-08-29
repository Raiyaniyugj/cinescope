from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.services.tmdb import tmdb_service
from app.services.recommendations import RecommendationEngine
from app.models import db, Watchlist, Watched, User, followers
import random

main_bp = Blueprint('main', __name__)

@main_bp.context_processor
def inject_user_movie_states():
    if current_user.is_authenticated:
        watched_ids = [w.tmdb_id for w in Watched.query.filter_by(user_id=current_user.id).all()]
        watchlist_ids = [w.tmdb_id for w in Watchlist.query.filter_by(user_id=current_user.id).all()]
        return dict(
            user_watched_ids=watched_ids,
            user_watchlist_ids=watchlist_ids
        )
    return dict(user_watched_ids=[], user_watchlist_ids=[])

@main_bp.route('/activity')
@login_required
def activity():
    """Activity feed — recent logs from users you follow."""
    followed_ids = [u.id for u in current_user.followed.all()]
    followed_ids.append(current_user.id)  # include own activity
    
    recent_activity = Watched.query.filter(
        Watched.user_id.in_(followed_ids)
    ).order_by(Watched.watched_at.desc()).limit(30).all()
    
    # Attach usernames
    user_map = {}
    users = User.query.filter(User.id.in_(followed_ids)).all()
    for u in users:
        user_map[u.id] = u
    
    activity_items = []
    for item in recent_activity:
        activity_items.append({
            'user': user_map.get(item.user_id),
            'item': item
        })
    
    return render_template('main/activity.html', activity_items=activity_items)

@main_bp.route('/')
@main_bp.route('/explorer')
def index():
    trending = tmdb_service.get_trending_movies()
    popular = tmdb_service.get_popular_movies()
    now_playing = tmdb_service.get_now_playing()
    genres = tmdb_service.get_genres_list()
    most_watched, _ = tmdb_service.get_all_movies(sort_by='most-watched')

    # Get recommendations if authenticated
    recommendations = []
    if current_user.is_authenticated:
        recommendations = RecommendationEngine.get_recommendations(current_user.id, num_recommendations=6)

    # Pick a featured movie for the hero backdrop
    featured = None
    if trending:
        # Pick one with a backdrop
        backdrop_movies = [m for m in trending if m.get('backdrop_path')]
        if backdrop_movies:
            featured = random.choice(backdrop_movies[:5])

    demo_mode = tmdb_service.is_demo_mode

    # Get friend activity for logged-in users
    friend_activity = []
    if current_user.is_authenticated:
        followed_ids = [u.id for u in current_user.followed.all()]
        followed_ids.append(current_user.id)
        recent = Watched.query.filter(
            Watched.user_id.in_(followed_ids)
        ).order_by(Watched.watched_at.desc()).limit(6).all()
        
        user_map = {}
        users_list = User.query.filter(User.id.in_(followed_ids)).all()
        for u in users_list:
            user_map[u.id] = u
        
        for item in recent:
            friend_activity.append({
                'user': user_map.get(item.user_id),
                'item': item
            })

    return render_template(
        'main/index.html',
        trending=trending,
        popular=popular,
        now_playing=now_playing,
        genres=genres,
        recommendations=recommendations,
        featured=featured,
        demo_mode=demo_mode,
        friend_activity=friend_activity,
        most_watched=most_watched
    )

@main_bp.route('/films/')
@main_bp.route('/films/page/<int:page>')
@main_bp.route('/films/by/<string:sort_by>')
@main_bp.route('/films/by/<string:sort_by>/page/<int:page>')
@main_bp.route('/films/popular/<string:timeframe>')
@main_bp.route('/films/popular/<string:timeframe>/page/<int:page>')
def films(sort_by=None, timeframe=None, page=1):
    """Dedicated films page with robust sorting, pagination, and timeframes."""
    # Check for legacy tab parameter
    tab = request.args.get('tab')
    if tab:
        if tab == 'new': sort_by = 'release-newest'
        elif tab == 'top': sort_by = 'rating-highest'
        elif tab in ['upcoming', 'coming-soon']: sort_by = 'release-newest'; timeframe = 'upcoming'
        else: sort_by = 'popularity'
    
    # Actually, if tab='upcoming', we should just use the get_upcoming method, or we can use the new get_all_movies.
    # TMDB 'upcoming' is a specific endpoint. Let's stick to get_all_movies for now unless tab is set explicitly.
    if tab and tab in ['upcoming', 'coming-soon']:
        movies = tmdb_service.get_upcoming()
        total_results = len(movies)
    else:
        # Default sort if none provided
        if not sort_by:
            sort_by = 'popularity'
            
        # Get 72 movies (4 pages of TMDB results)
        movies = []
        total_results = 0
        
        start_page = (page - 1) * 4 + 1
        end_page = start_page + 3
        
        for p in range(start_page, end_page + 1):
            batch, total = tmdb_service.get_all_movies(sort_by=sort_by, timeframe=timeframe, page=p)
            if not batch:
                break
            movies.extend(batch)
            total_results = total

    total_pages = (total_results + 71) // 72 if total_results else 1
    genres = tmdb_service.get_genres_list()
    
    return render_template('main/films.html', 
                           movies=movies, 
                           demo_mode=tmdb_service.is_demo_mode,
                           genres=genres,
                           sort_by=sort_by,
                           timeframe=timeframe,
                           current_page=page,
                           total_pages=total_pages)


@main_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        results = tmdb_service.search_multi(query)

    return render_template('main/search.html', query=query, results=results)

@main_bp.route('/studio/<int:company_id>')
def studio(company_id):
    page = request.args.get('page', 1, type=int)
    data = tmdb_service.get_company_movies(company_id, page=page)
    
    # Optional: fetch company details using another endpoint if needed.
    # For now, we'll just pass the ID and movies.
    movies = data.get('results', [])
    total_results = data.get('total_results', 0)
    total_pages = data.get('total_pages', 1)
    
    return render_template('main/studio.html',
                           company_id=company_id,
                           movies=movies,
                           total_results=total_results,
                           current_page=page,
                           total_pages=total_pages)

from flask import jsonify

@main_bp.route('/api/search')
def api_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'results': []})
    results = tmdb_service.search_multi(query)
    # Filter to only movies for the log feature
    movies = [r for r in results if r.get('media_type') == 'movie' or 'title' in r]
    return jsonify({'results': movies})

@main_bp.route('/api/refresh/<string:section>')
def refresh_section(section):
    if section == 'trending':
        movies = tmdb_service.get_trending_movies()
        random.shuffle(movies)
        movies = movies[:8]
    elif section == 'now_playing':
        movies = tmdb_service.get_now_playing()
        random.shuffle(movies)
        movies = movies[:8]
    elif section == 'recommendations':
        if current_user.is_authenticated:
            movies = RecommendationEngine.get_recommendations(current_user.id, num_recommendations=20)
            random.shuffle(movies)
            movies = movies[:8]
        else:
            movies = []
    elif section == 'most_watched':
        timeframe = request.args.get('timeframe', 'all-time')
        tf = timeframe if timeframe != 'all-time' else None
        movies, _ = tmdb_service.get_all_movies(sort_by='most-watched', timeframe=tf)
        movies = movies[:12] # Up to 12 for the layout
    else:
        movies = []
        
    return render_template('components/movie_grid_partial.html', movies=movies)


@main_bp.route('/tv/<int:tv_id>')
def tv_detail(tv_id):
    tmdb_service.last_error = None
    tv_show = tmdb_service.get_tv_details(tv_id)
    if not tv_show:
        if tmdb_service.last_error:
            flash('Could not load TV show details - connection issue with TMDB. Please try again.', 'warning')
            return redirect(request.referrer or url_for('main.index'))
        return render_template('errors/404.html'), 404
        
    return render_template('main/tv_detail.html', tv_show=tv_show)


@main_bp.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    tmdb_service.last_error = None  # Clear stale errors
    movie = tmdb_service.get_movie_details(movie_id)
    if not movie:
        if tmdb_service.last_error:
            flash('Could not load movie details — connection issue with TMDB. Please try again.', 'warning')
            return redirect(request.referrer or url_for('main.index'))
        return render_template('errors/404.html'), 404

    # Everything is now embedded from the single append_to_response call
    similar = movie.pop('_similar_movies', [])
    watch_providers = movie.pop('_watch_providers', None)

    # Check watchlist status
    in_watchlist = False
    is_watched = False
    user_rating = None
    user_review = None
    is_favorite = False

    if current_user.is_authenticated:
        from app.models import Watchlist, Watched
        watchlist_item = Watchlist.query.filter_by(user_id=current_user.id, tmdb_id=movie_id).first()
        if watchlist_item:
            in_watchlist = True
            
        watched_item = Watched.query.filter_by(user_id=current_user.id, tmdb_id=movie_id).first()
        if watched_item:
            is_watched = True
            user_rating = watched_item.rating
            user_review = watched_item.review
            is_favorite = watched_item.is_favorite
            
        from app.models import CustomList
        user_lists = CustomList.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'main/movie_detail.html',
        movie=movie,
        similar=similar,
        watch_providers=watch_providers,
        in_watchlist=in_watchlist,
        is_watched=is_watched,
        user_rating=user_rating,
        user_review=user_review,
        is_favorite=is_favorite,
        user_lists=user_lists if current_user.is_authenticated else []
    )

@main_bp.route('/movie/<int:movie_id>/similar')
@main_bp.route('/movie/<int:movie_id>/similar/page/<int:page>')
def similar_movies(movie_id, page=1):
    """View all similar movies."""
    movie = tmdb_service.get_movie_details(movie_id)
    if not movie:
        return render_template('errors/404.html'), 404
        
    movies, total_pages = tmdb_service.get_similar_movies(movie_id, page=page)
    
    return render_template(
        'main/similar_movies.html',
        movie=movie,
        movies=movies,
        current_page=page,
        total_pages=total_pages
    )

@main_bp.route('/genre/<int:genre_id>')
@main_bp.route('/genre/<int:genre_id>/page/<int:page>')
@main_bp.route('/genre/<int:genre_id>/by/<string:sort_by>')
@main_bp.route('/genre/<int:genre_id>/by/<string:sort_by>/page/<int:page>')
def genre_movies(genre_id, sort_by=None, page=1):
    """Browse movies by genre."""
    movies = []
    start_tmdb_page = (page - 1) * 4 + 1
    end_tmdb_page = start_tmdb_page + 3
    
    for page_num in range(start_tmdb_page, end_tmdb_page + 1):
        page_movies = tmdb_service.get_movies_by_genre(genre_id, sort_by=sort_by, page=page_num)
        movies.extend(page_movies)
        if len(page_movies) < 20:
            break
            
    movies = movies[:72]
    
    genres = tmdb_service.get_genres_list()
    genre_name = next((g['name'] for g in genres if g['id'] == genre_id), 'Unknown')
    
    # We lack total_results in get_movies_by_genre right now, assume an arbitrary large total pages for now or 100 pages
    total_pages = 100 
    
    return render_template(
        'main/genre.html', 
        movies=movies, 
        genre_name=genre_name, 
        genres=genres, 
        active_genre=genre_id,
        current_page=page,
        total_pages=total_pages,
        sort_by=sort_by
    )


@main_bp.route('/films/decade/<string:decade>')
@main_bp.route('/films/decade/<string:decade>/page/<int:page>')
@main_bp.route('/films/decade/<string:decade>/by/<string:sort_by>')
@main_bp.route('/films/decade/<string:decade>/by/<string:sort_by>/page/<int:page>')
@main_bp.route('/films/decade/<string:decade>/genre/<string:genre_name>')
@main_bp.route('/films/decade/<string:decade>/genre/<string:genre_name>/page/<int:page>')
@main_bp.route('/films/decade/<string:decade>/genre/<string:genre_name>/by/<string:sort_by>')
@main_bp.route('/films/decade/<string:decade>/genre/<string:genre_name>/by/<string:sort_by>/page/<int:page>')
def decade_movies(decade, genre_name=None, sort_by=None, page=1):
    """Browse movies by decade, optionally filtered by genre."""
    genres = tmdb_service.get_genres_list()
    
    genre_id = None
    active_genre_name = None
    if genre_name:
        # Find genre ID by name (case-insensitive)
        for g in genres:
            if g['name'].lower() == genre_name.lower():
                genre_id = g['id']
                active_genre_name = g['name']
                break
                
    # Fetch 4 TMDB pages to fill a 12x6 grid (72 movies)
    start_tmdb_page = (page - 1) * 4 + 1
    end_tmdb_page = start_tmdb_page + 3
    
    movies = []
    total_results = 0
    for page_num in range(start_tmdb_page, end_tmdb_page + 1):
        page_movies, current_total = tmdb_service.get_movies_by_decade(decade, genre_id=genre_id, sort_by=sort_by, page=page_num)
        movies.extend(page_movies)
        total_results = current_total
        if len(page_movies) < 20:
            break
            
    movies = movies[:72]
    
    try:
        decade_year = int(decade[:4])
    except ValueError:
        decade_year = 2020
        
    prev_decade = f"{decade_year - 10}s"
    next_decade = f"{decade_year + 10}s"
    
    # Generate list of years for this decade
    years = [str(y) for y in range(decade_year, decade_year + 10)]
    
    total_pages = (total_results + 71) // 72 if total_results else 1
    
    return render_template(
        'main/decade.html', 
        movies=movies, 
        decade=decade, 
        total_results=total_results,
        genres=genres,
        prev_decade=prev_decade,
        next_decade=next_decade,
        years=years,
        active_genre_name=active_genre_name,
        current_page=page,
        total_pages=total_pages,
        sort_by=sort_by
    )

@main_bp.route('/films/year/<string:year>')
@main_bp.route('/films/year/<string:year>/page/<int:page>')
@main_bp.route('/films/year/<string:year>/by/<string:sort_by>')
@main_bp.route('/films/year/<string:year>/by/<string:sort_by>/page/<int:page>')
@main_bp.route('/films/year/<string:year>/genre/<string:genre_name>')
@main_bp.route('/films/year/<string:year>/genre/<string:genre_name>/page/<int:page>')
@main_bp.route('/films/year/<string:year>/genre/<string:genre_name>/by/<string:sort_by>')
@main_bp.route('/films/year/<string:year>/genre/<string:genre_name>/by/<string:sort_by>/page/<int:page>')
def year_movies(year, genre_name=None, sort_by=None, page=1):
    """Browse movies by year, optionally filtered by genre."""
    genres = tmdb_service.get_genres_list()
    
    genre_id = None
    active_genre_name = None
    if genre_name:
        for g in genres:
            if g['name'].lower() == genre_name.lower():
                genre_id = g['id']
                active_genre_name = g['name']
                break
                
    start_tmdb_page = (page - 1) * 4 + 1
    end_tmdb_page = start_tmdb_page + 3
    
    movies = []
    total_results = 0
    for page_num in range(start_tmdb_page, end_tmdb_page + 1):
        page_movies, current_total = tmdb_service.get_movies_by_year(year, genre_id=genre_id, sort_by=sort_by, page=page_num)
        movies.extend(page_movies)
        total_results = current_total
        if len(page_movies) < 20:
            break
            
    movies = movies[:72]
    
    try:
        y = int(year)
    except ValueError:
        y = 2020
        
    decade_start = (y // 10) * 10
    decade = f"{decade_start}s"
    
    prev_decade = f"{decade_start - 10}s"
    next_decade = f"{decade_start + 10}s"
    
    years = [str(decade_start + i) for i in range(10)]
    
    total_pages = (total_results + 71) // 72 if total_results else 1
    
    return render_template(
        'main/decade.html', 
        movies=movies, 
        decade=decade,
        active_year=year,
        total_results=total_results,
        genres=genres,
        prev_decade=prev_decade,
        next_decade=next_decade,
        years=years,
        active_genre_name=active_genre_name,
        current_page=page,
        total_pages=total_pages,
        sort_by=sort_by
    )

# Curated list of famous studios with TMDB company IDs
STUDIOS = [
    {'id': 41077, 'name': 'A24', 'logo': 'a24'},
    {'id': 4, 'name': 'Paramount Pictures', 'logo': 'paramount'},
    {'id': 174, 'name': 'Warner Bros. Pictures', 'logo': 'warner'},
    {'id': 420, 'name': 'Marvel Studios', 'logo': 'marvel'},
    {'id': 2, 'name': 'Walt Disney Pictures', 'logo': 'disney'},
    {'id': 33, 'name': 'Universal Pictures', 'logo': 'universal'},
    {'id': 5, 'name': 'Columbia Pictures', 'logo': 'columbia'},
    {'id': 25, 'name': '20th Century Studios', 'logo': 'fox'},
    {'id': 7505, 'name': 'Lionsgate', 'logo': 'lionsgate'},
    {'id': 21, 'name': 'Metro-Goldwyn-Mayer', 'logo': 'mgm'},
    {'id': 3268, 'name': 'HBO Films', 'logo': 'hbo'},
    {'id': 7, 'name': 'DreamWorks Pictures', 'logo': 'dreamworks'},
    {'id': 9993, 'name': 'DC Studios', 'logo': 'dc'},
    {'id': 3, 'name': 'Pixar', 'logo': 'pixar'},
    {'id': 34, 'name': 'Sony Pictures', 'logo': 'sony'},
    {'id': 923, 'name': 'Legendary Pictures', 'logo': 'legendary'},
]


@main_bp.route('/studios')
def studios():
    """Browse movies by studio."""
    return render_template('main/studios.html', studios=STUDIOS)


@main_bp.route('/studio/<int:company_id>')
def studio_movies(company_id):
    """Show movies from a specific studio."""
    movies = tmdb_service.get_movies_by_studio(company_id)
    studio = next((s for s in STUDIOS if s['id'] == company_id), {'name': 'Studio', 'id': company_id})
    return render_template('main/studio_detail.html', movies=movies, studio=studio)


@main_bp.route('/lists')
def lists():
    """Curated movie lists like Letterboxd."""
    top_rated = tmdb_service.get_top_rated()
    upcoming = tmdb_service.get_upcoming()
    now_playing = tmdb_service.get_now_playing()
    trending = tmdb_service.get_trending_movies()
    return render_template('main/lists.html',
                           top_rated=top_rated,
                           upcoming=upcoming,
                           now_playing=now_playing,
                           trending=trending)

