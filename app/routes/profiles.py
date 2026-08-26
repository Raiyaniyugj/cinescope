from flask import Blueprint, render_template, abort
from app.services.tmdb import tmdb_service

profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route('/person/<int:person_id>')
def person(person_id):
    """View Actor, Director, or Writer profile."""
    person_data = tmdb_service.get_person_details(person_id)
    if not person_data:
        abort(404)
    return render_template('profiles/person.html', person=person_data)

@profiles_bp.route('/studio/<int:company_id>')
def studio(company_id):
    """View Production Company profile."""
    company_data = tmdb_service.get_company_details(company_id)
    if not company_data:
        abort(404)
    
    # Optional: We could fetch a paginated list here or do it via AJAX
    movies = tmdb_service.get_movies_by_studio(company_id, page=1)
    
    return render_template('profiles/studio.html', company=company_data, movies=movies)
