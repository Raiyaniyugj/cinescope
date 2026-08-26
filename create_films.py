content = '''{% extends "base.html" %}
{% block title %}Films — CineScope{% endblock %}

{% block content %}
<div class="container py-4">
    <!-- Header & Tabs -->
    <div class="d-flex justify-content-between align-items-end mb-2 pb-2">
        <h2 class="fw-normal mb-1 text-white" style="font-size: 1.8rem; font-family: 'Georgia', serif;">Films</h2>
    </div>
    
    <div class="d-flex gap-4 mb-4 border-bottom text-uppercase fw-bold pb-2" style="font-size: 0.75rem; letter-spacing: 1px; border-color: #2C3440 !important;">
        <a href="#" class="text-white text-decoration-none" style="border-bottom: 2px solid #00E054; padding-bottom: 3px;">POPULAR</a>
        <a href="#" class="text-decoration-none hover-white" style="color: #678;">NEW</a>
        <a href="#" class="text-decoration-none hover-white" style="color: #678;">TOP</a>
        <a href="#" class="text-decoration-none hover-white" style="color: #678;">COMING SOON</a>
    </div>

    <!-- Browse By Bar -->
    <div class="browse-by-bar d-flex align-items-center mb-4 p-2 rounded" style="background-color: #2C3440; color: #8AA8B9; font-size: 0.75rem; letter-spacing: 1px; text-transform: uppercase; font-weight: bold;">
        <span class="me-3 ps-2">BROWSE BY</span>
        <div class="d-flex gap-3">
            <a href="#" class="text-decoration-none d-flex align-items-center gap-1 hover-white" style="color: #8AA8B9;">YEAR <i class="bi bi-chevron-down" style="font-size: 0.6rem;"></i></a>
            <a href="#" class="text-decoration-none d-flex align-items-center gap-1 hover-white" style="color: #8AA8B9;">RATING <i class="bi bi-chevron-down" style="font-size: 0.6rem;"></i></a>
            <a href="#" class="text-decoration-none d-flex align-items-center gap-1 hover-white" style="color: #8AA8B9;">POPULAR <i class="bi bi-chevron-down" style="font-size: 0.6rem;"></i></a>
            <a href="#" class="text-decoration-none d-flex align-items-center gap-1 hover-white" style="color: #8AA8B9;">GENRE <i class="bi bi-chevron-down" style="font-size: 0.6rem;"></i></a>
            <a href="#" class="text-decoration-none d-flex align-items-center gap-1 hover-white" style="color: #8AA8B9;">SERVICE <i class="bi bi-chevron-down" style="font-size: 0.6rem;"></i></a>
        </div>
    </div>

    <!-- Posters Grid -->
    <div class="row g-3">
        {% for movie in trending %}
        <div class="col-4 col-sm-3 col-md-2 mb-3">
            <a href="{{ url_for('main.movie_detail', movie_id=movie.id) }}" class="text-decoration-none">
                <div class="poster-wrapper position-relative" style="border-radius: 4px; overflow: hidden; border: 1px solid #14181C; transition: transform 0.2s;">
                    {% if movie.poster_path %}
                    <img src="{{ movie.poster_path|poster_url }}" alt="{{ movie.title }}" style="width: 100%; aspect-ratio: 2/3; object-fit: cover;">
                    {% else %}
                    <div style="width: 100%; aspect-ratio: 2/3; background: #2C3440; display:flex; align-items:center; justify-content:center;"><i class="bi bi-film text-secondary"></i></div>
                    {% endif %}
                </div>
            </a>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}'''

with open('app/templates/main/films.html', 'w', encoding='utf-8') as f:
    f.write(content)
