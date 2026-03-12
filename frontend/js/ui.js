// UI Utilities

// Navigate to view
function navigateToView(viewName) {
    // Hide all views
    document.querySelectorAll('.content-view').forEach(view => {
        view.classList.remove('active');
    });

    // Show selected view
    const selectedView = document.getElementById(`${viewName}View`);
    if (selectedView) {
        selectedView.classList.add('active');
    }

    // Update navigation active state
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    const activeNav = document.querySelector(`[data-page="${viewName}"]`);
    if (activeNav) {
        activeNav.classList.add('active');
    }

    // Load data for view
    loadViewData(viewName);
}

// Load data for specific view
async function loadViewData(viewName) {
    switch (viewName) {
        case 'dashboard':
            await loadDashboard();
            break;
        case 'products':
            await loadProducts();
            break;
        case 'sales':
            await loadSales();
            break;
        case 'employees':
            await loadEmployees();
            break;
        case 'customers':
            if (typeof loadCustomers === 'function') {
                await loadCustomers();
            }
            break;
        case 'expenses':
            if (typeof loadExpenses === 'function') {
                await loadExpenses();
            }
            break;
        case 'reports':
            if (typeof loadReports === 'function') {
                await loadReports();
            }
            break;
        case 'alerts':
            await loadAlerts();
            break;
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    // You can implement a toast notification here
    console.log(`${type}: ${message}`);
}

// Format currency
function formatCurrency(amount) {
    return `Rs${parseFloat(amount || 0).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Initialize navigation
document.addEventListener('DOMContentLoaded', () => {
    // Setup navigation click handlers
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            const page = item.getAttribute('data-page');
            navigateToView(page);
        });
    });

    // Display user info
    const user = getCurrentUser();
    if (user) {
        const userInfoEl = document.getElementById('userInfo');
        if (userInfoEl) {
            userInfoEl.textContent = `${user.username} (${user.role})`;
        }
    }
});
