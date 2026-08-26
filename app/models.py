from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
)

class User(db.Model, UserMixin):
    """User database model for authentication and profiles."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Profile fields
    given_name = db.Column(db.String(100), nullable=True)
    family_name = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    pronoun = db.Column(db.String(50), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)

    # Relationships
    watchlist_items = db.relationship('Watchlist', backref='user', lazy=True, cascade="all, delete-orphan")
    watched_items = db.relationship('Watched', backref='user', lazy=True, cascade="all, delete-orphan")
    custom_lists = db.relationship('CustomList', backref='user', lazy=True, cascade="all, delete-orphan")
    
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    favorites = db.relationship('UserFavorite', backref='user', lazy=True, cascade="all, delete-orphan", order_by="UserFavorite.order")

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    def set_password(self, password):
        """Hashes the password using a secure algorithm."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Watchlist(db.Model):
    """Watchlist model representing a user's movie catalog."""
    __tablename__ = 'watchlists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    tmdb_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    poster_path = db.Column(db.String(256), nullable=True)
    release_date = db.Column(db.String(20), nullable=True)
    vote_average = db.Column(db.Float, nullable=True)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Watchlist User:{self.user_id} Movie:{self.title}>"


class Watched(db.Model):
    """Watched model representing movies a user has seen, reviewed, or rated."""
    __tablename__ = 'watched'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    tmdb_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    poster_path = db.Column(db.String(256), nullable=True)
    release_date = db.Column(db.String(20), nullable=True)
    vote_average = db.Column(db.Float, nullable=True)
    
    # Interaction features
    rating = db.Column(db.Float, nullable=True)  # User rating: 0.5 - 5.0
    review = db.Column(db.Text, nullable=True)
    is_favorite = db.Column(db.Boolean, default=False, nullable=False)
    watched_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    watched_date = db.Column(db.String(10), nullable=True)  # User-specified date YYYY-MM-DD

    def __repr__(self):
        return f"<Watched User:{self.user_id} Movie:{self.title} Rating:{self.rating}>"


class CustomList(db.Model):
    """Model representing user-created custom lists."""
    __tablename__ = 'custom_lists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    movies = db.relationship('CustomListMovie', backref='list', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CustomList User:{self.user_id} Name:{self.name}>"


class CustomListMovie(db.Model):
    """Model representing movies inside a custom list."""
    __tablename__ = 'custom_list_movies'

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('custom_lists.id', ondelete='CASCADE'), nullable=False)
    tmdb_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    poster_path = db.Column(db.String(256), nullable=True)
    release_date = db.Column(db.String(20), nullable=True)
    vote_average = db.Column(db.Float, nullable=True)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<CustomListMovie List:{self.list_id} Movie:{self.title}>"


class UserFavorite(db.Model):
    """Model representing a user's top 4 favorite movies."""
    __tablename__ = 'user_favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    tmdb_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(256), nullable=False)
    poster_path = db.Column(db.String(256), nullable=True)
    order = db.Column(db.Integer, nullable=False) # 1, 2, 3, or 4

    def __repr__(self):
        return f"<UserFavorite User:{self.user_id} Movie:{self.title} Order:{self.order}>"


class APICache(db.Model):
    """Cache for caching TMDB API request responses to minimize API hits and work offline."""
    __tablename__ = 'api_caches'

    url_key = db.Column(db.String(512), primary_key=True)
    response_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<APICache Key:{self.url_key[:50]}... Created:{self.created_at}>"
