from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import User
from sqlalchemy import func

members_bp = Blueprint('members', __name__, url_prefix='/members')

@members_bp.route('/')
def index():
    """List all members with optional search."""
    query = request.args.get('q', '').strip()
    
    # Base query: all users
    users_query = User.query
    
    if query:
        users_query = users_query.filter(User.username.ilike(f'%{query}%'))
        
    # Sort by number of followers if possible, otherwise just ID or created_at
    # We'll just do a basic order for now
    users = users_query.order_by(User.id.desc()).all()
    
    return render_template('members/index.html', users=users, query=query)
