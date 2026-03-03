document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.querySelector('.theme-toggle');
    const body = document.body;
    const themeIcon = themeToggleBtn.querySelector('.material-symbols-rounded');

    // Check for saved theme
    const savedTheme = localStorage.getItem('hive-theme');
    if (savedTheme) {
        body.className = savedTheme;
        updateThemeIcon(savedTheme);
    }

    themeToggleBtn.addEventListener('click', () => {
        if (body.classList.contains('light-theme')) {
            body.classList.replace('light-theme', 'dark-theme');
            localStorage.setItem('hive-theme', 'dark-theme');
            updateThemeIcon('dark-theme');
        } else {
            body.classList.replace('dark-theme', 'light-theme');
            localStorage.setItem('hive-theme', 'light-theme');
            updateThemeIcon('light-theme');
        }
    });

    function updateThemeIcon(theme) {
        if (theme === 'dark-theme') {
            themeIcon.textContent = 'light_mode';
        } else {
            themeIcon.textContent = 'dark_mode';
        }
    }
});
