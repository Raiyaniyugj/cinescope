import os
import threading
import time
from app import create_app

def run_server():
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Start the server in a daemon thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Wait for the server to start
    time.sleep(3)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        # Use a desktop viewport for nice screenshots
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print("Capturing Screenshot 1: Movie Explorer (Home Page)...")
        page.goto('http://127.0.0.1:5000/')
        
        # Remove lazy loading so Playwright fetches all posters for full_page screenshots
        page.evaluate('''
            document.querySelectorAll("img[loading='lazy']").forEach(img => img.removeAttribute("loading"));
        ''')
        page.wait_for_timeout(3000) # Give it 3 seconds to fetch the images

        page.screenshot(path='screenshot_1_home.png', full_page=True)

        import uuid
        unique_id = str(uuid.uuid4())[:8]
        print("Registering and logging in for authenticated views...")
        page.goto('http://127.0.0.1:5000/auth/register')
        page.fill('input[name="username"]', f'testuser_{unique_id}')
        page.fill('input[name="email"]', f'test_{unique_id}@example.com')
        page.fill('input[name="password"]', 'password123')
        page.fill('input[name="confirm_password"]', 'password123')
        page.click('button[type="submit"]')
        page.wait_for_timeout(1500)
        
        # Registration automatically logs the user in and redirects to home.

        print("Capturing Screenshot 2: Movie Detail Page...")
        # Get a movie ID (e.g., fallback data might have 155 for The Dark Knight or similar)
        # We can just click the first movie card on home page
        page.goto('http://127.0.0.1:5000/')
        page.wait_for_timeout(1000)
        href = page.eval_on_selector('.movie-grid a', 'el => el.href')
        if href:
            page.goto(href)
            page.wait_for_timeout(2000)
            
            # Add to watchlist
            add_btn = page.query_selector('form[action*="add_to_watchlist"] button')
            if add_btn:
                print("Adding movie to watchlist...")
                add_btn.click()
                page.wait_for_timeout(1000)
                # Ensure we are back on detail page if it redirects
                page.goto(href)
                page.wait_for_timeout(1000)
            
            page.evaluate('document.querySelectorAll("img[loading=\'lazy\']").forEach(img => img.removeAttribute("loading"));')
            page.wait_for_timeout(2000)
            page.screenshot(path='screenshot_2_movie_detail.png', full_page=True)
            
            # Add another movie to get recommendations
            page.goto('http://127.0.0.1:5000/')
            page.wait_for_timeout(1000)
            hrefs = page.eval_on_selector_all('.movie-grid a', 'els => els.map(e => e.href)')
            if len(hrefs) > 1:
                page.goto(hrefs[1])
                page.wait_for_timeout(1000)
                add_btn = page.query_selector('form[action*="add_to_watchlist"] button')
                if add_btn:
                    add_btn.click()
                    page.wait_for_timeout(1000)

        print("Capturing Screenshot 3: Personal Watchlist...")
        page.goto('http://127.0.0.1:5000/watchlist/')
        page.evaluate('document.querySelectorAll("img[loading=\'lazy\']").forEach(img => img.removeAttribute("loading"));')
        page.wait_for_timeout(2000)
        page.screenshot(path='screenshot_3_watchlist.png', full_page=True)

        print("Capturing Screenshot 4: Recommendation Engine Output...")
        page.goto('http://127.0.0.1:5000/')
        page.evaluate('document.querySelectorAll("img[loading=\'lazy\']").forEach(img => img.removeAttribute("loading"));')
        page.wait_for_timeout(2000)
        page.screenshot(path='screenshot_4_recommendations.png', full_page=True)

        print("Capturing Screenshot 5: Analytics Dashboard...")
        page.goto('http://127.0.0.1:5000/analytics/genres')
        page.evaluate('document.querySelectorAll("img[loading=\'lazy\']").forEach(img => img.removeAttribute("loading"));')
        page.wait_for_timeout(3000)
        page.screenshot(path='screenshot_5_analytics.png', full_page=True)

        print("Capturing Screenshot 6: Cinephile / User Profile Dashboard...")
        page.goto('http://127.0.0.1:5000/analytics/cinephile')
        page.evaluate('document.querySelectorAll("img[loading=\'lazy\']").forEach(img => img.removeAttribute("loading"));')
        page.wait_for_timeout(3000)
        page.screenshot(path='screenshot_6_profile.png', full_page=True)

        browser.close()
        print("Done capturing screenshots!")
