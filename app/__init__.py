import os
from flask import Flask
from flask_login import LoginManager
from app.models import db, User
from config import Config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.watchlist import watchlist_bp
    from app.routes.directors import directors_bp
    from app.routes.analytics import analytics_bp
    from app.routes.lists import lists_bp
    from app.routes.profiles import profiles_bp
    from app.routes.members import members_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(watchlist_bp)
    app.register_blueprint(directors_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(lists_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(members_bp)

    # Context processors / filters
    @app.template_filter('poster_url')
    def poster_url_filter(path, size='w500'):
        """Helper to generate full image URL from TMDB path, or fallback to placeholder."""
        if not path:
            return "/static/css/placeholder_poster.png"  # fallback placeholder will be styled via CSS/fallback
        if path.startswith('http'):
            return path
        return f"{app.config['TMDB_IMAGE_BASE_URL']}/{size}{path}"

    @app.template_filter('backdrop_url')
    def backdrop_url_filter(path, size='original'):
        """Helper to generate full backdrop image URL from TMDB path."""
        if not path:
            return ""
        if path.startswith('http'):
            return path
        return f"{app.config['TMDB_IMAGE_BASE_URL']}/{size}{path}"

    # Auto create database tables
    with app.app_context():
        db.create_all()

    # Inject Firebase web config into all templates
    @app.context_processor
    def inject_firebase_config():
        return dict(
            firebase_config={
                'apiKey': os.environ.get('FIREBASE_API_KEY'),
                'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN'),
                'projectId': os.environ.get('FIREBASE_PROJECT_ID'),
                'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET'),
                'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
                'appId': os.environ.get('FIREBASE_APP_ID')
            }
        )

    # Initialize TMDB Service
    from app.services.tmdb import tmdb_service
    tmdb_service.init_app(app)

    return app
