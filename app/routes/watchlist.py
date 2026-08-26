from flask import Blueprint, request, redirect, url_for, flash, render_template, Response
from flask_login import login_required, current_user
from datetime import datetime, timezone
from app.models import db, Watchlist, Watched, User
from app.services.tmdb import tmdb_service
from itertools import groupby
import csv
import io

watchlist_bp = Blueprint('watchlist', __name__)

@watchlist_bp.route('/diary')
@login_required
def diary():
    """Diary view — all logged films grouped by month."""
    watched_items = Watched.query.filter_by(user_id=current_user.id).order_by(Watched.watched_at.desc()).all()
    
    # Group by month
    grouped = {}
    for item in watched_items:
        if item.watched_at:
            key = item.watched_at.strftime('%B %Y')
        else:
            key = 'Unknown'
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    
    return render_template('watchlist/diary.html', grouped=grouped)

@watchlist_bp.route('/watchlist')
@watchlist_bp.route('/<username>/watchlist')
@login_required
def index(username=None):
    """View the user's Watchlist."""
    if username is None:
        user = current_user
    else:
        user = User.query.filter_by(username=username).first_or_404()

    watchlist_items = Watchlist.query.filter_by(user_id=user.id).order_by(Watchlist.added_at.desc()).all()
    watched_items = Watched.query.filter_by(user_id=user.id).order_by(Watched.watched_at.desc()).all()
    
    return render_template(
        'watchlist/watchlist.html',
        watchlist=watchlist_items,
        collection=watched_items,
        user=user
    )

@watchlist_bp.route('/watchlist/add/<int:movie_id>', methods=['POST'])
@login_required
def add_watchlist(movie_id):
    """Add a movie to watchlist."""
    existing = Watchlist.query.filter_by(user_id=current_user.id, tmdb_id=movie_id).first()
    if existing:
        flash(f'"{existing.title}" is already in your watchlist.', 'info')
        return redirect(request.referrer or url_for('watchlist.index'))

    movie = tmdb_service.get_movie_details(movie_id)
    if not movie:
        flash('Could not fetch movie details.', 'danger')
        return redirect(request.referrer or url_for('main.index'))

    new_item = Watchlist(
        user_id=current_user.id,
        tmdb_id=movie_id,
        title=movie.get('title'),
        poster_path=movie.get('poster_path'),
        release_date=movie.get('release_date'),
        vote_average=movie.get('vote_average', 0)
    )
    db.session.add(new_item)
    db.session.commit()
    flash(f'Added "{new_item.title}" to your watchlist!', 'success')
    return redirect(request.referrer or url_for('watchlist.index'))

@watchlist_bp.route('/watchlist/remove/<int:movie_id>', methods=['POST'])
@login_required
def remove_watchlist(movie_id):
    item = Watchlist.query.filter_by(user_id=current_user.id, tmdb_id=movie_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash(f'Removed "{item.title}" from your watchlist.', 'success')
    return redirect(request.referrer or url_for('watchlist.index'))


@watchlist_bp.route('/watched/log/<int:movie_id>', methods=['POST'])
@login_required
def log_watched(movie_id):
    """Log a movie as watched, optionally with rating, review, and favorite."""
    item = Watched.query.filter_by(user_id=current_user.id, tmdb_id=movie_id).first()
    
    rating_val = request.form.get('rating')
    review_text = request.form.get('review')
    is_fav = request.form.get('is_favorite') == 'on'

    if rating_val and rating_val.strip():
        try:
            rating_val = float(rating_val)
            if not (0.5 <= rating_val <= 5.0):
                raise ValueError
        except ValueError:
            rating_val = None
    else:
        rating_val = None

    if not item:
        movie = tmdb_service.get_movie_details(movie_id)
        if not movie:
            flash('Movie not found.', 'danger')
            return redirect(request.referrer or url_for('main.index'))
        item = Watched(
            user_id=current_user.id,
            tmdb_id=movie_id,
            title=movie.get('title'),
            poster_path=movie.get('poster_path'),
            release_date=movie.get('release_date'),
            vote_average=movie.get('vote_average'),
            rating=rating_val,
            review=review_text,
            is_favorite=is_fav
        )
        db.session.add(item)
        flash(f'Logged "{item.title}"!', 'success')
    else:
        # Update existing
        if rating_val is not None:
            item.rating = rating_val
        if review_text is not None:
            item.review = review_text
        if is_fav is not None:
            item.is_favorite = is_fav
        flash(f'Updated log for "{item.title}".', 'success')

    db.session.commit()
    return redirect(request.referrer or url_for('watchlist.index'))

@watchlist_bp.route('/watched/log_modal_submit', methods=['POST'])
@login_required
def log_modal_submit():
    """Log a movie from the global modal."""
    movie_id_str = request.form.get('tmdb_id')
    if not movie_id_str:
        flash('No movie selected.', 'danger')
        return redirect(request.referrer or url_for('main.index'))
    
    try:
        movie_id = int(movie_id_str)
    except ValueError:
        flash('Invalid movie ID.', 'danger')
        return redirect(request.referrer or url_for('main.index'))

    item = Watched.query.filter_by(user_id=current_user.id, tmdb_id=movie_id).first()
    
    rating_val = request.form.get('rating')
    review_text = request.form.get('review')
    is_fav = request.form.get('is_favorite') == 'on'
    watched_date = request.form.get('watched_date')

    if rating_val and rating_val.strip():
        try:
            rating_val = float(rating_val)
            if not (0.5 <= rating_val <= 5.0):
                raise ValueError
        except ValueError:
            rating_val = None
    else:
        rating_val = None

    if not item:
        movie = tmdb_service.get_movie_details(movie_id)
        if not movie:
            flash('Movie not found.', 'danger')
            return redirect(request.referrer or url_for('main.index'))
        item = Watched(
            user_id=current_user.id,
            tmdb_id=movie_id,
            title=movie.get('title'),
            poster_path=movie.get('poster_path'),
            release_date=movie.get('release_date'),
            vote_average=movie.get('vote_average'),
            rating=rating_val,
            review=review_text,
            is_favorite=is_fav,
            watched_date=watched_date
        )
        db.session.add(item)
        flash(f'Logged "{item.title}" successfully!', 'success')
    else:
        # Update existing
        if rating_val is not None:
            item.rating = rating_val
        if review_text is not None:
            item.review = review_text
        if is_fav is not None:
            item.is_favorite = is_fav
        flash(f'Updated log for "{item.title}".', 'success')

    db.session.commit()
    return redirect(request.referrer or url_for('auth.profile'))


@watchlist_bp.route('/watched/remove/<int:movie_id>', methods=['POST'])
@login_required
def remove_watched(movie_id):
    item = Watched.query.filter_by(user_id=current_user.id, tmdb_id=movie_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash(f'Removed "{item.title}" from your watched history.', 'success')
    return redirect(request.referrer or url_for('watchlist.index'))


@watchlist_bp.route('/export')
@login_required
def export_csv():
    """Export user's watched history and watchlist."""
    watched = Watched.query.filter_by(user_id=current_user.id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Collection', 'Title', 'TMDB ID', 'Release Date', 'Your Rating', 'Review', 'Favorite', 'Date'])

    for item in watched:
        writer.writerow([
            'Watched', item.title, item.tmdb_id, item.release_date or '',
            item.rating or '', item.review or '', 'Yes' if item.is_favorite else 'No',
            item.watched_at.strftime('%Y-%m-%d') if item.watched_at else ''
        ])
        
    watchlist = Watchlist.query.filter_by(user_id=current_user.id).all()
    for item in watchlist:
        writer.writerow([
            'Watchlist', item.title, item.tmdb_id, item.release_date or '',
            '', '', '', item.added_at.strftime('%Y-%m-%d') if item.added_at else ''
        ])

    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=cinescope_data_{current_user.username}.csv'}
    )
    return response
