/* ============================================
   CineScope — Minimal JS
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

    // Auto-dismiss flash messages after 4s
    document.querySelectorAll('.alert-cinescope').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    });

    // Active nav link
    const path = window.location.pathname;
    document.querySelectorAll('.navbar-cinescope .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '/' && path.startsWith(href)) {
            link.classList.add('active');
        } else if (href === '/' && path === '/') {
            link.classList.add('active');
        }
    });

    // Rating selectors
    initRatingSelectors();
});

function initRatingSelectors() {
    document.querySelectorAll('.rating-selector').forEach(selector => {
        const stars = selector.querySelectorAll('.star-btn');
        const hiddenInput = selector.querySelector('input[type="hidden"]');
        const currentRating = parseInt(hiddenInput?.value) || 0;

        stars.forEach((star, idx) => {
            if (idx < currentRating) {
                star.classList.add('active');
                star.innerHTML = '★';
            }

            star.addEventListener('mouseenter', () => {
                stars.forEach((s, i) => {
                    s.innerHTML = i <= idx ? '★' : '☆';
                    s.style.color = i <= idx ? '#00c030' : '';
                });
            });

            star.addEventListener('click', () => {
                const rating = idx + 1;
                if (hiddenInput) hiddenInput.value = rating;
                stars.forEach((s, i) => {
                    s.classList.toggle('active', i < rating);
                    s.innerHTML = i < rating ? '★' : '☆';
                });
                const form = selector.closest('form');
                if (form) form.submit();
            });
        });

        selector.addEventListener('mouseleave', () => {
            const val = parseInt(hiddenInput?.value) || 0;
            stars.forEach((s, i) => {
                s.classList.toggle('active', i < val);
                s.innerHTML = i < val ? '★' : '☆';
                s.style.color = '';
            });
        });
    });
}

function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
        btn.innerHTML = '<i class="bi bi-eye-slash-fill"></i>';
    } else {
        input.type = "password";
        btn.innerHTML = '<i class="bi bi-eye-fill"></i>';
    }
}
