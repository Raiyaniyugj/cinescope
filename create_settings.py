content = '''{% extends "base.html" %}
{% block title %}Account Settings - CineScope{% endblock %}

{% block content %}
<div class="container py-5" style="max-width: 900px; margin: 0 auto;">
    <div class="d-flex justify-content-between align-items-end mb-4 border-bottom border-secondary pb-3">
        <h2 class="fw-bold mb-0" style="color: #fff; font-family: 'Georgia', serif;">Account Settings</h2>
    </div>
    
    <div class="d-flex gap-4 mb-4 text-uppercase" style="font-size: 0.85rem; font-weight: 600; letter-spacing: 1px;">
        <a href="#" class="text-white text-decoration-none" style="border-bottom: 2px solid #00E054; padding-bottom: 2px;">Profile</a>
        <a href="#" class="text-secondary text-decoration-none hover-white">Auth</a>
        <a href="#" class="text-secondary text-decoration-none hover-white">Avatar</a>
        <a href="#" class="text-secondary text-decoration-none hover-white">Connections</a>
    </div>

    <form method="POST" action="{{ url_for('auth.settings') }}">
        <div class="row">
            <div class="col-md-7">
                <h4 class="text-white mb-4" style="font-size: 1.2rem;">Profile</h4>
                
                <div class="mb-3">
                    <label class="form-label text-secondary small fw-bold">Username</label>
                    <input type="text" class="form-control bg-dark border-secondary text-secondary" value="{{ current_user.username }}" disabled>
                </div>
                
                <div class="row mb-3">
                    <div class="col">
                        <label class="form-label text-secondary small fw-bold">Given name</label>
                        <input type="text" name="given_name" class="form-control bg-dark text-white border-0" style="background-color: #2C3440 !important;" value="{{ current_user.given_name or '' }}">
                    </div>
                    <div class="col">
                        <label class="form-label text-secondary small fw-bold">Family name</label>
                        <input type="text" name="family_name" class="form-control bg-dark text-white border-0" style="background-color: #2C3440 !important;" value="{{ current_user.family_name or '' }}">
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label text-secondary small fw-bold">Email address</label>
                    <input type="email" class="form-control bg-dark text-secondary border-0" style="background-color: #2C3440 !important;" value="{{ current_user.email }}" disabled>
                </div>
                
                <div class="row mb-3">
                    <div class="col">
                        <label class="form-label text-secondary small fw-bold">Location</label>
                        <input type="text" name="location" class="form-control bg-dark text-white border-0" style="background-color: #2C3440 !important;" value="{{ current_user.location or '' }}">
                    </div>
                    <div class="col">
                        <label class="form-label text-secondary small fw-bold">Website</label>
                        <input type="text" name="website" class="form-control bg-dark text-white border-0" style="background-color: #2C3440 !important;" value="{{ current_user.website or '' }}">
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label text-secondary small fw-bold">Bio</label>
                    <textarea name="bio" class="form-control bg-dark text-white border-0" style="background-color: #2C3440 !important; resize: none;" rows="4">{{ current_user.bio or '' }}</textarea>
                </div>

                <div class="mb-3">
                    <label class="form-label text-secondary small fw-bold">Pronoun</label>
                    <select name="pronoun" class="form-select bg-dark text-white border-0" style="background-color: #2C3440 !important;">
                        <option value="" {% if not current_user.pronoun %}selected{% endif %}></option>
                        <option value="He / him" {% if current_user.pronoun == 'He / him' %}selected{% endif %}>He / him</option>
                        <option value="She / her" {% if current_user.pronoun == 'She / her' %}selected{% endif %}>She / her</option>
                        <option value="They / their" {% if current_user.pronoun == 'They / their' %}selected{% endif %}>They / their</option>
                    </select>
                </div>

                <div class="mb-4">
                    <label class="form-label text-secondary small fw-bold">Avatar URL</label>
                    <input type="text" name="avatar_url" class="form-control bg-dark text-white border-0" style="background-color: #2C3440 !important;" value="{{ current_user.avatar_url or '' }}" placeholder="https://example.com/avatar.jpg">
                </div>
                
                <button type="submit" class="btn fw-bold mt-3" style="background-color: #00E054; color: #fff;">SAVE CHANGES</button>
            </div>
            
            <div class="col-md-5 ps-5">
                <h4 class="text-white mb-4 text-uppercase" style="font-size: 0.85rem; letter-spacing: 1px;">Favorite Films</h4>
                <div class="d-flex gap-2 mb-2">
                    {% for i in range(1, 5) %}
                        <div class="favorite-film-slot position-relative" style="width: 75px; height: 112px; background: #2C3440; border-radius: 4px; display: flex; align-items: center; justify-content: center; cursor: pointer;">
                            {% if i in user_favorites %}
                                {% set fav = user_favorites[i] %}
                                <img src="https://image.tmdb.org/t/p/w92{{ fav.poster_path }}" alt="{{ fav.title }}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 4px;">
                            {% else %}
                                <span style="color: #678; font-size: 1.5rem;">+</span>
                            {% endif %}
                        </div>
                    {% endfor %}
                </div>
                <small class="text-secondary">Edit your favorite films on your profile.</small>
            </div>
        </div>
    </form>
</div>

<style>
    .hover-white:hover { color: #fff !important; }
</style>
{% endblock %}'''

with open('app/templates/auth/settings.html', 'w', encoding='utf-8') as f:
    f.write(content)
