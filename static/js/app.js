// Theme Toggle Logic
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        if (theme === 'dark') {
            icon.classList.remove('bi-moon-fill');
            icon.classList.add('bi-sun-fill');
        } else {
            icon.classList.remove('bi-sun-fill');
            icon.classList.add('bi-moon-fill');
        }
    }
}

// Session Management
function getSessionId() {
    let sid = localStorage.getItem('session_id');
    if (!sid) {
        sid = 'sess_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('session_id', sid);
    }
    return sid;
}

// Progress Bar Updates
async function fetchProgress() {
    const sid = getSessionId();
    try {
        const res = await fetch(`/api/progress/${sid}`);
        const data = await res.json();
        return data;
    } catch (e) {
        console.error("Failed to fetch progress", e);
        return null;
    }
}

async function updateProgress(step, status) {
    const sid = getSessionId();
    try {
        await fetch(`/api/progress/${sid}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ step, status: status ? 1 : 0 })
        });
    } catch (e) {
        console.error("Failed to update progress", e);
    }
}

// Language Toggle (Basic)
function initLanguage() {
    const lang = localStorage.getItem('lang') || 'en';
    applyLanguage(lang);
}

function toggleLanguage() {
    let lang = localStorage.getItem('lang') || 'en';
    lang = lang === 'en' ? 'hi' : 'en';
    localStorage.setItem('lang', lang);
    applyLanguage(lang);
    // Reload page to apply logic if needed, or simply let the frontend handle it
    window.location.reload();
}

function applyLanguage(lang) {
    const langBtn = document.getElementById('lang-toggle-text');
    if (langBtn) {
        langBtn.innerText = lang === 'en' ? 'हिंदी' : 'English';
    }
    // For a real app, we would translate texts based on data attributes.
    // Here we just keep it simple and mock a few places if needed.
}

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initLanguage();
    
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }

    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) {
        langBtn.addEventListener('click', toggleLanguage);
    }
});
