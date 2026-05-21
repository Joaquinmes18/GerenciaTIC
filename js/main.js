tailwind.config = {
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            colors: {
                background: '#030712',
                surface: '#111827',
                primary: '#3b82f6',
                secondary: '#6366f1',
                accent: '#10b981',
                alert: '#ef4444',
            }
        }
    }
};

// Mobile nav toggle with animations + icon swap + outside-click close
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('nav-toggle');
    const menu = document.getElementById('mobile-menu');
    if (!btn || !menu) return;
    const hamburger = btn.querySelector('.hamburger-icon');
    const closeIcon = btn.querySelector('.close-icon');
    const ENTER_MS = 200;
    const LEAVE_MS = 160;

    const openMenu = () => {
        menu.classList.remove('hidden');
        menu.classList.remove('menu-leave');
        // trigger enter animation
        void menu.offsetWidth;
        menu.classList.add('menu-enter');
        if (hamburger) hamburger.classList.add('hidden');
        if (closeIcon) closeIcon.classList.remove('hidden');
        btn.setAttribute('aria-expanded', 'true');
    };

    const closeMenu = () => {
        menu.classList.remove('menu-enter');
        menu.classList.add('menu-leave');
        if (hamburger) hamburger.classList.remove('hidden');
        if (closeIcon) closeIcon.classList.add('hidden');
        btn.setAttribute('aria-expanded', 'false');
        setTimeout(() => menu.classList.add('hidden'), LEAVE_MS);
    };

    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (menu.classList.contains('hidden')) openMenu(); else closeMenu();
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
        if (!menu.classList.contains('hidden') && !btn.contains(e.target) && !menu.contains(e.target)) {
            closeMenu();
        }
    });

    // Close when resizing to desktop
    window.addEventListener('resize', () => {
        if (window.innerWidth >= 768 && !menu.classList.contains('hidden')) {
            menu.classList.add('hidden');
            menu.classList.remove('menu-enter', 'menu-leave');
            if (hamburger) hamburger.classList.remove('hidden');
            if (closeIcon) closeIcon.classList.add('hidden');
            btn.setAttribute('aria-expanded', 'false');
        }
    });
});