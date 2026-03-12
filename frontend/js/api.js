const API_URL = 'http://127.0.0.1:8000/api';

// Existing API object...
const API = {
    // Existing endpoints...
    auth: {
        login: `${API_URL}/auth/login/`,
        logout: `${API_URL}/auth/logout/`,
        me: `${API_URL}/auth/me/`,
        customerRegister: `${API_URL}/auth/customer-register/`,  // NEW - Feature 4
    },
    
    products: {
        list: `${API_URL}/products/`,
        create: `${API_URL}/products/create/`,
        detail: (barcode) => `${API_URL}/products/${barcode}/`,
        update: (barcode) => `${API_URL}/products/${barcode}/update/`,
        delete: (barcode) => `${API_URL}/products/${barcode}/delete/`,
        lowStock: `${API_URL}/products/low-stock/`,
        topSelling: `${API_URL}/products/top-selling/`,          // NEW - Feature 6
        searchBarcode: (barcode) => `${API_URL}/products/barcode/${barcode}/`,  // NEW - Feature 9
    },
    
    sales: {
        list: `${API_URL}/sales/`,
        create: `${API_URL}/sales/create/`,
        detail: (id) => `${API_URL}/sales/${id}/`,
        customerPurchase: `${API_URL}/sales/customer-purchase/`,  // NEW - Feature 11
    },
    
    employees: {
        list: `${API_URL}/employees/`,
        create: `${API_URL}/employees/create/`,                   // NEW - Feature 3
        salaries: `${API_URL}/employees/salaries/`,               // NEW - Feature 8
        detail: (id) => `${API_URL}/employees/${id}/`,
        update: (id) => `${API_URL}/employees/${id}/update/`,
        delete: (id) => `${API_URL}/employees/${id}/delete/`,
    },
    
    customers: {
        list: `${API_URL}/customers/`,
        create: `${API_URL}/customers/create/`,
        detail: (id) => `${API_URL}/customers/${id}/`,
        update: (id) => `${API_URL}/customers/${id}/update/`,
        delete: (id) => `${API_URL}/customers/${id}/delete/`,
        purchases: (id) => `${API_URL}/customers/${id}/purchases/`,
    },
    
    expenses: {
        list: `${API_URL}/expenses/`,
        add: `${API_URL}/expenses/add/`,                          // NEW - Feature 2
        summary: `${API_URL}/expenses/summary/`,                  // NEW - Feature 2
        detail: (id) => `${API_URL}/expenses/${id}/`,
    },
    
    reports: {
        profitLoss: `${API_URL}/reports/profit-loss/`,           // NEW - Feature 7
        inventory: `${API_URL}/reports/inventory/`,
        salesTrend: `${API_URL}/reports/sales-trend/`,
    },
    
    alerts: {
        list: `${API_URL}/alerts/`,
        lowStock: `${API_URL}/alerts/low-stock/`,                // NEW - Feature 6
        markRead: (id) => `${API_URL}/alerts/${id}/read/`,
    },
    
    dashboard: {
        stats: `${API_URL}/dashboard/stats/`,
        enhanced: `${API_URL}/dashboard/enhanced/`,              // NEW - Feature 10
    },
    
    admin: {
        addMonthlySalaries: `${API_URL}/admin/add-monthly-salaries/`,  // NEW - Feature 8
    },
    getProducts: async function() {
        return await apiCall(this.products.list);
    },
    
    createProduct: async function(data) {
        return await apiCall(this.products.create, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    deleteProduct: async function(barcode) {
        return await apiCall(this.products.delete(barcode), {
            method: 'DELETE'
        });
    },
    
    getSales: async function(params = {}) {
        const limit = params.limit || 50;
        return await apiCall(`${this.sales.list}?limit=${limit}`);
    },
    
    createSale: async function(data) {
        return await apiCall(this.sales.create, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
};

async function apiCall(url, options = {}) {
    const token = localStorage.getItem('token');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
        ...options,
        headers,
    });
    
    return response.json();
}