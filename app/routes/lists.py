from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, CustomList, CustomListMovie
from app.services.tmdb import tmdb_service

lists_bp = Blueprint('lists', __name__, url_prefix='/lists')

@lists_bp.route('/')
@login_required
def index():
    """Show all user lists."""
    user_lists = CustomList.query.filter_by(user_id=current_user.id).order_by(CustomList.created_at.desc()).all()
    return render_template('lists/index.html', user_lists=user_lists)

@lists_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_list():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        if name:
            new_list = CustomList(user_id=current_user.id, name=name, description=description)
            db.session.add(new_list)
            db.session.flush() # get new_list.id
            
            # handle added movies
            movies = request.form.getlist('movies[]')
            for tmdb_id in movies:
                details = tmdb_service.get_movie_details(tmdb_id)
                if details:
                    lm = CustomListMovie(
                        list_id=new_list.id,
                        tmdb_id=int(tmdb_id),
                        title=details.get('title', 'Unknown'),
                        poster_path=details.get('poster_path'),
                        release_date=details.get('release_date'),
                        vote_average=details.get('vote_average')
                    )
                    db.session.add(lm)
            
            db.session.commit()
            flash(f'List "{name}" created.', 'success')
            return redirect(url_for('lists.view_list', list_id=new_list.id))
    return render_template('lists/edit.html', custom_list=None)

@lists_bp.route('/<int:list_id>')
@login_required
def view_list(list_id):
    """View a specific list."""
    custom_list = CustomList.query.get_or_404(list_id)
    if custom_list.user_id != current_user.id:
        flash("You do not have permission to view this list.", "danger")
        return redirect(url_for('lists.index'))
        
    sort_by = request.args.get('sort', 'added')
    if sort_by == 'title':
        sorted_movies = sorted(custom_list.movies, key=lambda x: x.title)
    elif sort_by == 'year':
        sorted_movies = sorted(custom_list.movies, key=lambda x: x.release_date or '', reverse=True)
    elif sort_by == 'rating':
        sorted_movies = sorted(custom_list.movies, key=lambda x: x.vote_average or 0, reverse=True)
    else:
        sorted_movies = sorted(custom_list.movies, key=lambda x: x.id, reverse=True)

    return render_template('lists/view_list.html', custom_list=custom_list, sorted_movies=sorted_movies, current_sort=sort_by)

@lists_bp.route('/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_list(list_id):
    custom_list = CustomList.query.get_or_404(list_id)
    if custom_list.user_id == current_user.id:
        db.session.delete(custom_list)
        db.session.commit()
        flash('List deleted.', 'info')
    return redirect(url_for('lists.index'))

@lists_bp.route('/<int:list_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_list(list_id):
    custom_list = CustomList.query.get_or_404(list_id)
    if custom_list.user_id != current_user.id:
        flash("You do not have permission to edit this list.", "danger")
        return redirect(url_for('lists.index'))

    if request.method == 'POST':
        new_name = request.form.get('name')
        if new_name:
            custom_list.name = new_name
            custom_list.description = request.form.get('description', '')
            
            # For editing, we expect the frontend to send the final array of movie IDs
            # Delete old movies not in the new array, add new ones.
            # Easiest: delete all and re-add to preserve order if we had ordering, 
            # but we can just use the add/remove api for dynamic updates on edit.
            # Actually, to make it simple, let's just update name/desc here, 
            # and rely on the dynamic add/remove JS API for movie changes during edit.
            db.session.commit()
            flash('List updated.', 'success')
            return redirect(url_for('lists.view_list', list_id=list_id))

    return render_template('lists/edit.html', custom_list=custom_list)

@lists_bp.route('/<int:list_id>/add', methods=['POST'])
@login_required
def add_movie(list_id):
    custom_list = CustomList.query.get_or_404(list_id)
    if custom_list.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    tmdb_id = request.form.get('tmdb_id')
    if not tmdb_id:
        return jsonify({"success": False, "error": "Missing tmdb_id"}), 400

    # check if already in list
    existing = CustomListMovie.query.filter_by(list_id=list_id, tmdb_id=int(tmdb_id)).first()
    if existing:
        return jsonify({"success": False, "error": "Movie already in list"})

    details = tmdb_service.get_movie_details(tmdb_id)
    if not details:
        return jsonify({"success": False, "error": "Movie not found"})

    lm = CustomListMovie(
        list_id=list_id,
        tmdb_id=int(tmdb_id),
        title=details.get('title', 'Unknown'),
        poster_path=details.get('poster_path'),
        release_date=details.get('release_date'),
        vote_average=details.get('vote_average')
    )
    db.session.add(lm)
    db.session.commit()
    return jsonify({"success": True})

@lists_bp.route('/<int:list_id>/remove', methods=['POST'])
@login_required
def remove_movie(list_id):
    tmdb_id = request.form.get('tmdb_id')
    custom_list = CustomList.query.get_or_404(list_id)
    if custom_list.user_id == current_user.id:
        movie = CustomListMovie.query.filter_by(list_id=list_id, tmdb_id=int(tmdb_id)).first()
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return jsonify({"success": True})
    return jsonify({"success": False})
