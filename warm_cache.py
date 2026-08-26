"""Cache Warmer — Run this once to pre-populate the API cache.
After running, all pages will load instantly from cache."""

import sys
import time

def warm_cache():
    from app import create_app
    from app.services.tmdb import tmdb_service
    
    app = create_app()
    with app.app_context():
        print("[*] Warming CineScope cache...\n")
        
        calls = [
            ("Trending movies", lambda: tmdb_service.get_trending_movies()),
            ("Popular movies", lambda: tmdb_service.get_popular_movies()),
            ("Now playing", lambda: tmdb_service.get_now_playing()),
            ("Genre list", lambda: tmdb_service.get_genres_list()),
            ("Top rated", lambda: tmdb_service.get_top_rated()),
            ("Upcoming", lambda: tmdb_service.get_upcoming()),
        ]
        
        total_start = time.time()
        
        for name, fn in calls:
            t = time.time()
            result = fn()
            elapsed = (time.time() - t) * 1000
            count = len(result) if result else 0
            status = f"[OK] {count} items" if result else "[FAIL]"
            print(f"  {name}: {status} ({elapsed:.0f}ms)")
        
        # Warm some popular movie details
        print("\n  Warming popular movie details...")
        trending = tmdb_service.get_trending_movies()
        if trending:
            for movie in trending[:5]:
                t = time.time()
                details = tmdb_service.get_movie_details(movie['id'])
                elapsed = (time.time() - t) * 1000
                title = details.get('title', '?') if details else '?'
                status = "[OK]" if details else "[FAIL]"
                print(f"    {status} {title} ({elapsed:.0f}ms)")
        
        total = time.time() - total_start
        print(f"\n[DONE] Cache warm complete in {total:.1f}s")
        print("   All pages will now load instantly!")

if __name__ == '__main__':
    warm_cache()
