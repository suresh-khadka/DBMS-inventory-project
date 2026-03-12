// Alerts & Notifications Module

async function loadAlerts() {
    console.log('Loading alerts...');
    
    try {
        const response = await fetch(`${API_URL}/alerts/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            renderAlerts(data.data);
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
        const container = document.getElementById('alertsList');
        if (container) {
            container.innerHTML = '<p style="color: red;">Error loading alerts. Please refresh.</p>';
        }
    }
}

function renderAlerts(alerts) {
    const container = document.getElementById('alertsList');
    if (!container) return;

    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p class="text-center">✅ No alerts at this time</p>';
        return;
    }

    let html = '<div class="alerts-container">';
    
    const unreadAlerts = alerts.filter(a => !a.is_read);
    const readAlerts = alerts.filter(a => a.is_read);
    
    if (unreadAlerts.length > 0) {
        html += '<h3>🔴 Unread Alerts (' + unreadAlerts.length + ')</h3>';
        html += unreadAlerts.map(alert => `
            <div class="alert-item unread alert-${alert.alert_type}">
                <div class="alert-content">
                    <strong>${getAlertIcon(alert.alert_type)} ${alert.title}</strong>
                    <p>${alert.message}</p>
                    <small>${new Date(alert.created_at).toLocaleDateString('en-IN')}</small>
                </div>
                <div class="alert-actions">
                    <button class="btn btn-sm btn-secondary" onclick="markAlertAsRead(${alert.id})">Mark Read</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteAlert(${alert.id})">Delete</button>
                </div>
            </div>
        `).join('');
    }
    
    if (readAlerts.length > 0) {
        html += '<h3>✅ Read Alerts</h3>';
        html += readAlerts.map(alert => `
            <div class="alert-item read alert-${alert.alert_type}">
                <div class="alert-content">
                    <strong>${getAlertIcon(alert.alert_type)} ${alert.title}</strong>
                    <p>${alert.message}</p>
                    <small>${new Date(alert.created_at).toLocaleDateString('en-IN')}</small>
                </div>
                <div class="alert-actions">
                    <button class="btn btn-sm btn-danger" onclick="deleteAlert(${alert.id})">Delete</button>
                </div>
            </div>
        `).join('');
    }
    
    html += '</div>';
    container.innerHTML = html;
    
    updateAlertBadge(unreadAlerts.length);
}

function getAlertIcon(alertType) {
    switch(alertType) {
        case 'low_stock':
            return '⚠️';
        case 'out_of_stock':
            return '❌';
        case 'high_sales':
            return '📈';
        case 'low_sales':
            return '📉';
        case 'expiry':
            return '⏰';
        default:
            return '🔔';
    }
}

function updateAlertBadge(count) {
    const badge = document.getElementById('alertBadge');
    if (badge) {
        badge.textContent = count || 0;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

async function markAlertAsRead(alertId) {
    try {
        const response = await fetch(`${API_URL}/alerts/${alertId}/read/`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        
        if (result.success) {
            loadAlerts();
        } else {
            alert(`Error: ${result.error || result.message}`);
        }
    } catch (error) {
        console.error('Error marking alert as read:', error);
        alert(`Error: ${error.message}`);
    }
}

async function deleteAlert(alertId) {
    if (!confirm('Are you sure you want to delete this alert?')) return;

    try {
        const response = await fetch(`${API_URL}/alerts/${alertId}/delete/`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        const result = await response.json();
        
        if (result.success) {
            alert('Alert deleted successfully');
            loadAlerts();
        } else {
            alert(`Error deleting alert: ${result.error || result.message}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error deleting alert: ${error.message}`);
    }
}

function clearAllAlerts() {
    if (!confirm('Clear all alerts?')) return;
    
    const alerts = document.querySelectorAll('.alert-item');
    let count = 0;
    
    alerts.forEach((alert, index) => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, index * 50);
    });
    
    setTimeout(() => {
        loadAlerts();
    }, alerts.length * 50 + 300);
}

console.log('Alerts.js loaded successfully');
