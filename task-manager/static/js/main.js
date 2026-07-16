/**
 * main.js — TaskFlow
 * Handles: dark/light theme persistence, flash-message -> toast conversion,
 * page-load spinner, mobile sidebar toggle, AJAX task status toggling,
 * and delete confirmations.
 */

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initFlashToasts();
    hidePageLoader();
    initMobileSidebar();
    initStatusToggles();
    initDeleteConfirmations();
    initFormLoadingState();
});

/* ---------------------------------------------------------------------
 * Theme (dark / light) toggle — persisted in localStorage
 * ------------------------------------------------------------------- */
function initThemeToggle() {
    const root = document.documentElement;
    const toggleBtn = document.getElementById('themeToggle');
    const icon = document.getElementById('themeIcon');

    const savedTheme = localStorage.getItem('taskflow-theme') || 'light';
    root.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const current = root.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-theme', next);
            localStorage.setItem('taskflow-theme', next);
            updateThemeIcon(next);
        });
    }

    function updateThemeIcon(theme) {
        if (!icon) return;
        icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    }
}

/* ---------------------------------------------------------------------
 * Convert Flask flash messages into Bootstrap toasts
 * ------------------------------------------------------------------- */
function initFlashToasts() {
    const flashData = document.getElementById('flashData');
    const toastContainer = document.getElementById('toastContainer');
    if (!flashData || !toastContainer) return;

    let messages = [];
    try {
        messages = JSON.parse(flashData.dataset.messages);
    } catch (e) {
        console.error('Could not parse flash messages', e);
        return;
    }

    const categoryMap = {
        success: { icon: 'bi-check-circle-fill', bg: 'text-bg-success' },
        danger: { icon: 'bi-exclamation-triangle-fill', bg: 'text-bg-danger' },
        warning: { icon: 'bi-exclamation-circle-fill', bg: 'text-bg-warning' },
        info: { icon: 'bi-info-circle-fill', bg: 'text-bg-info' },
        message: { icon: 'bi-info-circle-fill', bg: 'text-bg-primary' },
    };

    messages.forEach((item, index) => {
        const style = categoryMap[item.category] || categoryMap.info;
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center ${style.bg} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${style.icon} me-2"></i>${item.message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>`;
        toastContainer.appendChild(toastEl);

        setTimeout(() => {
            const toast = new bootstrap.Toast(toastEl, { delay: 4500 });
            toast.show();
        }, index * 150);
    });
}

/* ---------------------------------------------------------------------
 * Page loader — hides once the DOM is ready
 * ------------------------------------------------------------------- */
function hidePageLoader() {
    const loader = document.getElementById('page-loader');
    if (loader) {
        setTimeout(() => loader.classList.add('hidden'), 250);
    }
}

/* ---------------------------------------------------------------------
 * Mobile sidebar toggle
 * ------------------------------------------------------------------- */
function initMobileSidebar() {
    const toggleBtn = document.getElementById('mobileSidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (!toggleBtn || !sidebar) return;

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
        if (sidebar.classList.contains('open') &&
            !sidebar.contains(e.target) &&
            !toggleBtn.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

/* ---------------------------------------------------------------------
 * AJAX task status toggling (list badge + detail page button)
 * ------------------------------------------------------------------- */
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

function initStatusToggles() {
    document.querySelectorAll('.status-toggle, .status-toggle-btn').forEach((el) => {
        el.addEventListener('click', async (e) => {
            e.preventDefault();
            const taskId = el.dataset.taskId;
            if (!taskId) return;

            const originalContent = el.innerHTML;
            el.style.opacity = '0.6';

            try {
                const response = await fetch(`/tasks/${taskId}/toggle-status`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken(),
                        'Content-Type': 'application/json',
                    },
                });
                const data = await response.json();

                if (data.success) {
                    // Simplest reliable UX: reload so all badges/labels stay in sync.
                    window.location.reload();
                } else {
                    el.style.opacity = '1';
                    el.innerHTML = originalContent;
                }
            } catch (err) {
                console.error('Failed to toggle task status', err);
                el.style.opacity = '1';
            }
        });
    });
}

/* ---------------------------------------------------------------------
 * Confirm before deleting a task
 * ------------------------------------------------------------------- */
function initDeleteConfirmations() {
    document.querySelectorAll('.delete-task-form').forEach((form) => {
        form.addEventListener('submit', (e) => {
            const confirmed = window.confirm('Delete this task? This action cannot be undone.');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
}

/* ---------------------------------------------------------------------
 * Show a subtle loading state on form submit buttons
 * ------------------------------------------------------------------- */
function initFormLoadingState() {
    document.querySelectorAll('form:not(.delete-task-form):not(#filterForm)').forEach((form) => {
        form.addEventListener('submit', () => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.dataset.originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Please wait...';
            }
        });
    });
}
