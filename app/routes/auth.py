from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify

from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Watchlist, Watched, CustomList, UserFavorite

from app.services.tmdb import tmdb_service
from app.services.analytics import AnalyticsService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('Please fill out all fields.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        # Check existing user
        if User.query.filter_by(username=username).first():
            flash('Username is already taken.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return render_template('auth/register.html')

        # Create user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('Account created successfully! Welcome to CineScope.', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Profile settings
        new_username = request.form.get('username')
        if new_username and new_username != current_user.username:
            if User.query.filter_by(username=new_username).first():
                flash('Username is already taken.', 'danger')
            else:
                current_user.username = new_username

        new_email = request.form.get('email')
        if new_email and new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                flash('Email is already registered.', 'danger')
            else:
                current_user.email = new_email
        
        # Password update
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        if current_password and new_password:
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
                flash('Password updated successfully.', 'success')
            else:
                flash('Incorrect current password.', 'danger')

        # Other fields
        current_user.given_name = request.form.get('given_name')
        current_user.family_name = request.form.get('family_name')
        current_user.location = request.form.get('location')
        current_user.website = request.form.get('website')
        current_user.bio = request.form.get('bio')
        current_user.pronoun = request.form.get('pronoun')
        # Handle Avatar
        avatar_type = request.form.get('avatar_type')
        if avatar_type == 'gravatar':
            import hashlib
            email_hash = hashlib.md5(current_user.email.lower().encode('utf-8')).hexdigest()
            current_user.avatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=identicon"
        elif avatar_type == 'custom':
            avatar_cropped_data = request.form.get('avatar_cropped_data')
            if avatar_cropped_data and avatar_cropped_data.startswith('data:image'):
                import os
                import base64
                import time
                from werkzeug.utils import secure_filename
                from flask import current_app
                
                header, encoded = avatar_cropped_data.split(",", 1)
                data = base64.b64decode(encoded)
                
                filename = secure_filename(f"{current_user.id}_{int(time.time())}.png")
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                
                with open(file_path, "wb") as f:
                    f.write(data)
                    
                current_user.avatar_url = url_for('static', filename=f"uploads/{filename}")
        
        db.session.commit()
        flash('Settings saved successfully.', 'success')
        return redirect(url_for('auth.settings'))

    user_favorites = {f.order: f for f in current_user.favorites}
    return render_template('auth/settings.html', user=current_user, user_favorites=user_favorites)



@auth_bp.route('/profile')
@auth_bp.route('/profile/<username>')
@login_required
def profile(username=None):
    if username is None:
        user = current_user
    else:
        user = User.query.filter_by(username=username).first_or_404()

    demo_mode = tmdb_service.is_demo_mode
    
    watchlist_count = Watchlist.query.filter_by(user_id=user.id).count()
    favorites_count = Watched.query.filter_by(user_id=user.id, is_favorite=True).count()
    reviews_count = Watched.query.filter(Watched.user_id == user.id, Watched.review != None, Watched.review != '').count()
    lists_count = CustomList.query.filter_by(user_id=user.id).count()
    
    dashboard_data = AnalyticsService.generate_cinephile_dashboard(user.id)
    cinephile_stats = dashboard_data.get('stats', {}) if dashboard_data else {}
    
    recent = Watched.query.filter_by(user_id=user.id).order_by(Watched.watched_at.desc()).limit(20).all()
    
    # Get all watched films for the Films tab
    all_watched = Watched.query.filter_by(user_id=user.id).order_by(Watched.watched_at.desc()).all()
    
    # Get recent likes
    recent_likes = Watched.query.filter_by(user_id=user.id, is_favorite=True).order_by(Watched.watched_at.desc()).limit(4).all()
    
    # Get watchlist preview
    watchlist_preview = Watchlist.query.filter_by(user_id=user.id).order_by(Watchlist.added_at.desc()).limit(4).all()
    
    # Get top 4 favorites
    user_favorites = {f.order: f for f in user.favorites}

    return render_template('auth/profile.html', 
                           user=user,
                           demo_mode=demo_mode,
                           watchlist_count=watchlist_count,
                           favorites_count=favorites_count,
                           reviews_count=reviews_count,
                           lists_count=lists_count,
                           cinephile_stats=cinephile_stats,
                           recent=recent,
                           all_watched=all_watched,
                           recent_likes=recent_likes,
                           watchlist_preview=watchlist_preview,
                           user_favorites=user_favorites)

@auth_bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.', 'danger')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!', 'warning')
        return redirect(url_for('auth.profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {username}!', 'success')
    return redirect(url_for('auth.profile', username=username))

@auth_bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.', 'danger')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!', 'warning')
        return redirect(url_for('auth.profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}.', 'info')
    return redirect(url_for('auth.profile', username=username))

@auth_bp.route('/api/update_favorites', methods=['POST'])
@login_required
def update_favorites():
    data = request.json
    if not data or not isinstance(data, list):
        return jsonify({'success': False, 'error': 'Invalid data format'})
        
    for fav in data:
        order = fav.get('order')
        tmdb_id = fav.get('tmdb_id')
        if not order or not tmdb_id:
            continue
            
        details = tmdb_service.get_movie_details(tmdb_id)
        if not details:
            continue
            
        existing = UserFavorite.query.filter_by(user_id=current_user.id, order=order).first()
        if existing:
            existing.tmdb_id = tmdb_id
            existing.title = details.get('title', 'Unknown')
            existing.poster_path = details.get('poster_path')
        else:
            new_fav = UserFavorite(
                user_id=current_user.id,
                tmdb_id=tmdb_id,
                title=details.get('title', 'Unknown'),
                poster_path=details.get('poster_path'),
                order=order
            )
            db.session.add(new_fav)
            
    db.session.commit()
    return jsonify({'success': True})

@auth_bp.route('/api/remove_favorite', methods=['POST'])
@login_required
def remove_favorite():
    order = request.json.get('order')
    if order:
        fav = UserFavorite.query.filter_by(user_id=current_user.id, order=order).first()
        if fav:
            db.session.delete(fav)
            db.session.commit()
            return jsonify({'success': True})
    return jsonify({'success': False})

@auth_bp.route('/firebase-login', methods=['POST'])
def firebase_login():
    import firebase_admin
    from firebase_admin import auth
    
    id_token = request.json.get('idToken')
    if not id_token:
        return jsonify({'success': False, 'error': 'No token provided'}), 400
        
    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(id_token)
        google_id = decoded_token.get('uid')
        email = decoded_token.get('email')
        name_str = decoded_token.get('name', '')
        
        name = name_str.split()
        given_name = name[0] if name else ''
        family_name = name[1] if len(name) > 1 else ''
        
        # 1. Try to find user by google_id
        user = User.query.filter_by(google_id=google_id).first()
        
        # 2. Try to find user by email
        if not user:
            user = User.query.filter_by(email=email).first()
            if user:
                # Link existing account to Google
                user.google_id = google_id
                db.session.commit()
                
        # 3. Create new user
        if not user:
            username = email.split('@')[0]
            # Ensure unique username
            base_username = username
            counter = 1
            while User.query.filter_by(username=username).first():
                username = f"{base_username}{counter}"
                counter += 1
                
            user = User(
                username=username,
                email=email,
                google_id=google_id,
                given_name=given_name,
                family_name=family_name
            )
            # password_hash is nullable now, so we can leave it empty
            db.session.add(user)
            db.session.commit()
            
        login_user(user, remember=True)
        return jsonify({'success': True, 'redirect': url_for('main.index')})
        
    except Exception as e:
        print(f"Firebase login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 401
