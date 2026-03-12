// ==================== UTILITY FUNCTIONS ====================

function getToken() {
    return localStorage.getItem('token');
}

function getAuthHeaders() {
    const token = getToken();
    return {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
    };
}

function formatCurrency(amount) {
    return `₹${parseFloat(amount || 0).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN');
}

// ==================== MAIN DASHBOARD LOADER ====================

async function loadDashboard() {
    console.log('Loading dashboard...');
    
    try {
        const response = await fetch(`${API_URL}/dashboard/stats/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Unauthorized - redirecting to login');
                localStorage.clear();
                window.location.href = 'index.html';
                return;
            }
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Dashboard data:', data);
        
        if (data.success) {
            renderDashboardStats(data.data);
            
            // Load recent sales
            loadRecentSales();
            
            // Load low stock products
            loadLowStockProducts();
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        document.getElementById('statsGrid').innerHTML = 
            '<p style="color: red;">Error loading dashboard. Please refresh.</p>';
    }
}

// ==================== RENDER DASHBOARD STATS ====================

function renderDashboardStats(stats) {
    const statsGrid = document.getElementById('statsGrid');
    if (!statsGrid) return;

    const totalProducts = stats.products?.total || 0;
    const lowStock = stats.products?.lowStock || 0;
    const todayRevenue = stats.sales?.today?.totalRevenue || 0;
    const monthRevenue = stats.sales?.thisMonth?.totalRevenue || 0;

    statsGrid.innerHTML = `
        <div class="stat-card">
            <div class="stat-icon">📦</div>
            <div class="stat-content">
                <div class="stat-value">${totalProducts}</div>
                <div class="stat-label">Total Products</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">⚠️</div>
            <div class="stat-content">
                <div class="stat-value">${lowStock}</div>
                <div class="stat-label">Low Stock</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-content">
                <div class="stat-value">${formatCurrency(todayRevenue)}</div>
                <div class="stat-label">Today's Sales</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
                <div class="stat-value">${formatCurrency(monthRevenue)}</div>
                <div class="stat-label">Monthly Revenue</div>
            </div>
        </div>
    `;
}

// ==================== LOAD RECENT SALES ====================

async function loadRecentSales() {
    try {
        const response = await fetch(`${API_URL}/sales/?limit=5`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            renderRecentSales(data.data);
        }
    } catch (error) {
        console.error('Error loading recent sales:', error);
        const container = document.getElementById('recentSales');
        if (container) {
            container.innerHTML = '<p>Unable to load recent sales</p>';
        }
    }
}

function renderRecentSales(sales) {
    const container = document.getElementById('recentSales');
    if (!container) return;

    if (!sales || sales.length === 0) {
        container.innerHTML = '<p class="text-center">No recent sales</p>';
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Amount</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                ${sales.map(sale => `
                    <tr>
                        <td>${sale.product_name || 'N/A'}</td>
                        <td>${formatCurrency(sale.total_amount)}</td>
                        <td>${formatDate(sale.sale_date)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ==================== LOAD LOW STOCK PRODUCTS ====================

async function loadLowStockProducts() {
    try {
        const response = await fetch(`${API_URL}/products/low-stock/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            renderLowStock(data.data);
        }
    } catch (error) {
        console.error('Error loading low stock products:', error);
        const container = document.getElementById('lowStockProducts');
        if (container) {
            container.innerHTML = '<p>Unable to load low stock products</p>';
        }
    }
}

function renderLowStock(products) {
    const container = document.getElementById('lowStockProducts');
    if (!container) return;

    if (!products || products.length === 0) {
        container.innerHTML = '<p class="text-center">✅ All products well stocked!</p>';
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Stock</th>
                    <th>Min Level</th>
                </tr>
            </thead>
            <tbody>
                ${products.map(product => `
                    <tr>
                        <td>${product.product_name}</td>
                        <td><span style="color: #e74c3c; font-weight: bold;">${product.stock_level}</span></td>
                        <td>${product.min_stock_level}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ==================== ENHANCED DASHBOARD (Features 6, 10) ====================

async function loadEnhancedDashboard() {
    console.log('Loading enhanced dashboard...');
    
    try {
        const response = await fetch(`${API_URL}/dashboard/enhanced/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            console.warn('Enhanced dashboard not available, using basic dashboard');
            return;
        }
        
        const data = await response.json();
        console.log('Enhanced data:', data);
        
        if (data.success) {
            // Display Today's Revenue
            const todayRevenueEl = document.getElementById('todayRevenue');
            if (todayRevenueEl) {
                todayRevenueEl.textContent = formatCurrency(data.today_sales.revenue);
            }
            
            const todaySalesCountEl = document.getElementById('todaySalesCount');
            if (todaySalesCountEl) {
                todaySalesCountEl.textContent = data.today_sales.count;
            }
            
            // Display Total Expenses
            const totalExpensesEl = document.getElementById('totalExpenses');
            if (totalExpensesEl) {
                totalExpensesEl.textContent = formatCurrency(data.total_expenses);
            }
            
            // Display Profit/Loss
            const profitAmountEl = document.getElementById('profitAmount');
            const profitPercentageEl = document.getElementById('profitPercentage');
            const profitStatusEl = document.getElementById('profitStatus');
            
            if (profitAmountEl && profitPercentageEl && profitStatusEl) {
                profitAmountEl.textContent = formatCurrency(Math.abs(data.profit_loss.amount));
                profitPercentageEl.textContent = `${data.profit_loss.percentage.toFixed(2)}%`;
                
                if (data.profit_loss.status === 'profit') {
                    profitAmountEl.style.color = 'green';
                    profitStatusEl.textContent = '✅ Profit';
                    profitStatusEl.style.background = '#d4edda';
                    profitStatusEl.style.color = '#155724';
                } else {
                    profitAmountEl.style.color = 'red';
                    profitStatusEl.textContent = '❌ Loss';
                    profitStatusEl.style.background = '#f8d7da';
                    profitStatusEl.style.color = '#721c24';
                }
            }
            
            // Display Today's Products List
            const todayProductsListEl = document.getElementById('todayProductsList');
            if (todayProductsListEl && data.today_sales.products) {
                if (data.today_sales.products.length === 0) {
                    todayProductsListEl.innerHTML = '<p class="text-center">No products sold today yet</p>';
                } else {
                    todayProductsListEl.innerHTML = data.today_sales.products.map(p => `
                        <div class="product-sale-item">
                            <strong>${p.barcode__product_name}</strong>
                            <span>Qty: ${p.total_qty}</span>
                            <span>${formatCurrency(p.total_amount)}</span>
                        </div>
                    `).join('');
                }
            }
        }
    } catch (error) {
        console.error('Error loading enhanced dashboard:', error);
    }
}

// ==================== TOP SELLING PRODUCTS (Feature 6) ====================

async function loadTopProducts() {
    console.log('Loading top products...');
    
    try {
        const response = await fetch(`${API_URL}/products/top-selling/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Top products:', data);
        
        if (data.success) {
            const topList = document.getElementById('topProductsList');
            if (topList) {
                if (data.top_products.length === 0) {
                    topList.innerHTML = '<p class="text-center">No sales data yet</p>';
                } else {
                    topList.innerHTML = data.top_products.map((p, index) => `
                        <div class="top-product-card">
                            <div class="rank">#${index + 1}</div>
                            <h4>${p.product_name}</h4>
                            <p>Sales: ${p.total_sales_count} units</p>
                            <p>Revenue: ${formatCurrency(p.total_revenue)}</p>
                            <p>Price: ${formatCurrency(p.selling_price)}</p>
                        </div>
                    `).join('');
                }
            }
        }
    } catch (error) {
        console.error('Error loading top products:', error);
    }
}

// ==================== LOW STOCK ALERTS (Feature 6) ====================

async function loadLowStockAlerts() {
    console.log('Loading low stock alerts...');
    
    try {
        const response = await fetch(`${API_URL}/alerts/low-stock/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Low stock alerts:', data);
        
        if (data.success) {
            const alertsList = document.getElementById('lowStockAlerts');
            if (!alertsList) return;
            
            let html = '';
            
            // Out of stock products
            if (data.out_of_stock && data.out_of_stock.count > 0) {
                html += '<h4>❌ Out of Stock</h4>';
                data.out_of_stock.products.forEach(p => {
                    html += `
                        <div class="alert-item out-of-stock">
                            <strong>${p.product_name}</strong>
                            <span class="badge-danger">Out of Stock</span>
                        </div>
                    `;
                });
            }
            
            // Low stock products
            if (data.low_stock && data.low_stock.count > 0) {
                html += '<h4>⚠️ Low Stock</h4>';
                data.low_stock.products.forEach(p => {
                    html += `
                        <div class="alert-item low-stock">
                            <strong>${p.product_name}</strong>
                            <span>Stock: ${p.stock_level} / Min: ${p.min_stock_level}</span>
                        </div>
                    `;
                });
            }
            
            if (data.total_alerts === 0) {
                html = '<p class="text-center">✅ All products have sufficient stock!</p>';
            }
            
            alertsList.innerHTML = html;
            
            // Update alert badge
            const alertBadge = document.getElementById('alertBadge');
            if (alertBadge) {
                alertBadge.textContent = data.total_alerts || 0;
            }
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

// ==================== ROLE-BASED UI (Feature 1) ====================

function applyRoleBasedUI() {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
        window.location.href = 'index.html';
        return;
    }
    
    try {
        const user = JSON.parse(userStr);
        console.log('User role:', user.role);
        
        // Show "Add New Product" button only for admin/employee
        const addProductBtn = document.getElementById('addProductBtn');
        if (addProductBtn) {
            if (user.role === 'admin' || user.role === 'employee') {
                addProductBtn.style.display = 'inline-block';
            } else {
                addProductBtn.style.display = 'none';
            }
        }
        
        // Hide menu items based on role
        if (user.role === 'employee') {
            // Employees can only see: Dashboard, Products, Sales, Customers
            const menuItems = document.querySelectorAll('.nav-item');
            menuItems.forEach(item => {
                const page = item.getAttribute('data-page');
                if (page === 'employees' || page === 'expenses' || page === 'reports') {
                    item.style.display = 'none';
                }
            });
        } else if (user.role === 'customer') {
            // Customers can only see Products
            const menuItems = document.querySelectorAll('.nav-item');
            menuItems.forEach(item => {
                const page = item.getAttribute('data-page');
                if (page !== 'products') {
                    item.style.display = 'none';
                }
            });
            
            // Redirect customer to products page
            setTimeout(() => {
                if (typeof navigateToView === 'function') {
                    navigateToView('products');
                }
            }, 100);
        }
    } catch (error) {
        console.error('Error applying role-based UI:', error);
    }
}

// ==================== INITIALIZE DASHBOARD ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initializing...');
    
    // Check authentication
    const token = getToken();
    const userStr = localStorage.getItem('user');
    
    if (!token || !userStr) {
        console.log('No auth - redirecting to login');
        window.location.href = 'index.html';
        return;
    }
    
    try {
        const user = JSON.parse(userStr);
        console.log('Logged in as:', user.username, '(' + user.role + ')');
        
        // Apply role-based UI restrictions
        applyRoleBasedUI();
        
        // Load dashboard data based on role
        if (user.role === 'admin' || user.role === 'employee') {
            console.log('Loading full dashboard for', user.role);
            loadDashboard();
            loadEnhancedDashboard();
            loadTopProducts();
            loadLowStockAlerts();
            
            // Load alerts and expenses on init
            if (typeof loadAlerts === 'function') {
                loadAlerts();
            }
            if (typeof loadExpenses === 'function') {
                loadExpenses();
            }
        } else if (user.role === 'customer') {
            console.log('Customer login - showing products only');
            // Customers don't need dashboard
        }
    } catch (error) {
        console.error('Error during initialization:', error);
        localStorage.clear();
        window.location.href = 'index.html';
    }
});

console.log('Dashboard.js loaded successfully');