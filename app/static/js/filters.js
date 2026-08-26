document.addEventListener('DOMContentLoaded', function() {
    // Check local storage for existing filter preferences
    const filters = {
        'fade-watched': localStorage.getItem('filter_fade-watched') === 'true',
        'action-watched': localStorage.getItem('filter_action-watched') || 'show', // 'show' or 'hide'
        'action-watchlist': localStorage.getItem('filter_action-watchlist') || 'show',
        'action-doc': localStorage.getItem('filter_action-doc') || 'show'
    };

    // Initialize UI state based on localStorage
    const fadeToggle = document.getElementById('fadeWatchedToggle');
    if (fadeToggle) {
        fadeToggle.checked = filters['fade-watched'];
    }

    // Set active classes on the dropdown items
    document.querySelectorAll('.filter-action').forEach(el => {
        const actionStr = el.getAttribute('data-filter-action');
        // actionStr looks like 'show-watched' or 'hide-watched'
        if (actionStr) {
            const parts = actionStr.split('-');
            const state = parts[0]; // show or hide
            const target = parts[1]; // watched, watchlist, doc

            if (filters['action-' + target] === state) {
                el.classList.add('active-filter');
            }
        }
    });

    // Apply the filters to the DOM immediately
    applyFilters();

    // Listen for toggle switches (like fade watched)
    if (fadeToggle) {
        fadeToggle.addEventListener('change', function(e) {
            filters['fade-watched'] = e.target.checked;
            localStorage.setItem('filter_fade-watched', e.target.checked);
            applyFilters();
        });
    }

    // Listen for clicks on the filter actions (Show/Hide text links)
    document.querySelectorAll('.filter-action').forEach(el => {
        el.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Keep dropdown open when clicking these items

            const actionStr = this.getAttribute('data-filter-action');
            const parts = actionStr.split('-');
            const state = parts[0];
            const target = parts[1];

            // If clicking the currently active one, we might want to toggle it off?
            // Actually Letterboxd usually keeps it selected until you select the opposite.
            if (filters['action-' + target] !== state) {
                // Update state
                filters['action-' + target] = state;
                localStorage.setItem('filter_action-' + target, state);

                // Update UI classes
                document.querySelectorAll(`.filter-action[data-filter-action$="-${target}"]`).forEach(btn => {
                    btn.classList.remove('active-filter');
                });
                this.classList.add('active-filter');

                applyFilters();
            } else {
                // If clicking the active one, unselect it (reset to 'show')
                if (state === 'hide') {
                    filters['action-' + target] = 'show';
                    localStorage.setItem('filter_action-' + target, 'show');
                    this.classList.remove('active-filter');
                    const showBtn = document.querySelector(`.filter-action[data-filter-action="show-${target}"]`);
                    if(showBtn) showBtn.classList.add('active-filter');
                    applyFilters();
                }
            }
        });
    });

    function applyFilters() {
        const movieCards = document.querySelectorAll('.movie-card');
        
        movieCards.forEach(card => {
            const isWatched = card.getAttribute('data-watched') === 'true';
            const isWatchlist = card.getAttribute('data-watchlist') === 'true';
            const isDoc = card.getAttribute('data-documentary') === 'true';

            let shouldHide = false;
            let shouldFade = false;

            // Check Hide rules
            if (filters['action-watched'] === 'hide' && isWatched) shouldHide = true;
            if (filters['action-watchlist'] === 'hide' && isWatchlist) shouldHide = true;
            if (filters['action-doc'] === 'hide' && isDoc) shouldHide = true;

            // Fade watched rule
            if (filters['fade-watched'] && isWatched) shouldFade = true;

            // Apply classes
            if (shouldHide) {
                card.style.display = 'none';
            } else {
                card.style.display = 'block'; // Or flex/grid depending on layout, but the wrapper handles it
            }

            if (shouldFade && !shouldHide) {
                card.style.opacity = '0.35';
                card.style.filter = 'grayscale(30%)';
            } else {
                card.style.opacity = '1';
                card.style.filter = 'none';
            }
        });
    }
});
