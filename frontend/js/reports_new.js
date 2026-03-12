// Reports & Analytics Module

async function loadReports() {
    console.log('Loading reports...');
    
    try {
        // Load profit/loss report
        loadProfitLossReport();
        
        // Load inventory report
        loadInventoryReport();
        
        // Load sales trend report
        loadSalesTrendReport();
    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

async function loadProfitLossReport() {
    try {
        console.log('Fetching profit/loss report from:', `${API_URL}/reports/profit-loss/`);
        const response = await fetch(`${API_URL}/reports/profit-loss/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        console.log('Response status:', response.status, response.ok);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Profit/Loss report API response:', JSON.stringify(data, null, 2));
        
        if (data && data.success === true) {
            renderProfitLossReport(data);
        } else if (data && data.success === false) {
            console.error('API returned success: false', data);
            const container = document.getElementById('profitLossReport');
            if (container) {
                container.innerHTML = '<p style="color: red;">Failed to load report: ' + (data.error || 'Unknown error') + '</p>';
            }
        } else {
            console.error('Unexpected response structure:', data);
            const container = document.getElementById('profitLossReport');
            if (container) {
                container.innerHTML = '<p style="color: red;">Unexpected API response structure</p>';
            }
        }
    } catch (error) {
        console.error('Error loading profit/loss report:', error);
        const container = document.getElementById('profitLossReport');
        if (container) {
            container.innerHTML = '<p style="color: red;">Error loading profit/loss report: ' + error.message + '</p>';
        }
    }
}

function renderProfitLossReport(reportData) {
    const container = document.getElementById('profitLossReport');
    if (!container) return;
    
    // Safe extraction with proper null/undefined checks
    const totalRevenue = reportData && reportData.revenue ? parseFloat(reportData.revenue.amount || 0) : 0;
    const totalExpenses = reportData && reportData.expenses ? parseFloat(reportData.expenses.amount || 0) : 0;
    const totalProfit = reportData && reportData.profit_loss ? parseFloat(reportData.profit_loss.amount || 0) : 0;
    const profitPercentage = reportData && reportData.profit_loss ? parseFloat(reportData.profit_loss.percentage || 0) : 0;
    
    const profitClass = totalProfit >= 0 ? 'profit' : 'loss';
    const profitIcon = totalProfit >= 0 ? '✅' : '❌';
    
    const salesCount = reportData && reportData.revenue ? (reportData.revenue.sales_count || 0) : 0;
    const expenseCount = reportData && reportData.expenses ? (reportData.expenses.expense_count || 0) : 0;
    const periodLabel = reportData ? (reportData.period_label || 'Daily') : 'Daily';
    const status = reportData && reportData.profit_loss ? (reportData.profit_loss.status || 'N/A') : 'N/A';
    
    container.innerHTML = `
        <div class="report-section">
            <h2>📊 Profit & Loss Report - ${periodLabel}</h2>
            <div class="report-grid">
                <div class="report-card">
                    <h3>Total Revenue</h3>
                    <p class="report-value">₹${totalRevenue.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                    <p style="font-size: 0.85em; color: #666;">Sales: ${salesCount}</p>
                </div>
                <div class="report-card">
                    <h3>Total Expenses</h3>
                    <p class="report-value">₹${totalExpenses.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                    <p style="font-size: 0.85em; color: #666;">Expenses: ${expenseCount}</p>
                </div>
                <div class="report-card ${profitClass}">
                    <h3>Net ${totalProfit >= 0 ? 'Profit' : 'Loss'}</h3>
                    <p class="report-value">${profitIcon} ₹${Math.abs(totalProfit).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                </div>
                <div class="report-card">
                    <h3>Profit Margin</h3>
                    <p class="report-value">${profitPercentage.toFixed(2)}%</p>
                    <p style="font-size: 0.85em; color: #666;">Status: ${status}</p>
                </div>
            </div>
        </div>
    `;
}

async function loadInventoryReport() {
    try {
        console.log('Fetching inventory report from:', `${API_URL}/reports/inventory/`);
        const response = await fetch(`${API_URL}/reports/inventory/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        console.log('Inventory report response status:', response.status, response.ok);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const apiResponse = await response.json();
        console.log('Inventory report API response:', JSON.stringify(apiResponse, null, 2));
        
        if (apiResponse && apiResponse.success === true) {
            // The API returns data in apiResponse.data
            renderInventoryReport(apiResponse.data || {});
        } else {
            console.error('API returned success: false or invalid structure', apiResponse);
            const container = document.getElementById('inventoryReport');
            if (container) {
                container.innerHTML = '<p style="color: red;">Failed to load inventory report</p>';
            }
        }
    } catch (error) {
        console.error('Error loading inventory report:', error);
        const container = document.getElementById('inventoryReport');
        if (container) {
            container.innerHTML = '<p style="color: red;">Error loading inventory report: ' + error.message + '</p>';
        }
    }
}

function renderInventoryReport(reportData) {
    const container = document.getElementById('inventoryReport');
    if (!container) return;
    
    // Backend returns: totalProducts, totalValue, lowStock
    // Handle both naming conventions
    const totalProducts = reportData.totalProducts || reportData.total_products || 0;
    const totalValue = reportData.totalValue || reportData.total_value || 0;
    const lowStockCount = reportData.lowStock || reportData.low_stock_count || 0;
    const outOfStockCount = reportData.outOfStock || reportData.out_of_stock_count || 0;
    
    container.innerHTML = `
        <div class="report-section">
            <h2>📦 Inventory Report</h2>
            <div class="report-grid">
                <div class="report-card">
                    <h3>Total Products</h3>
                    <p class="report-value">${totalProducts}</p>
                </div>
                <div class="report-card">
                    <h3>Total Inventory Value</h3>
                    <p class="report-value">₹${parseFloat(totalValue).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                </div>
                <div class="report-card warning">
                    <h3>Low Stock</h3>
                    <p class="report-value">${lowStockCount}</p>
                </div>
                ${outOfStockCount > 0 ? `
                <div class="report-card danger">
                    <h3>Out of Stock</h3>
                    <p class="report-value">${outOfStockCount}</p>
                </div>
                ` : ''}
            </div>
        </div>
    `;

                    `<p class="report-value">⚠️ ${lowStockCount}</p>
                </div>
                <div class="report-card danger">
                    <h3>Out of Stock</h3>
                    <p class="report-value">❌ ${outOfStockCount}</p>
                </div>
            </div>
        </div>
    `;
}

async function loadSalesTrendReport() {
    try {
        const response = await fetch(`${API_URL}/reports/sales-trend/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            renderSalesTrendReport(data.data);
        }
    } catch (error) {
        console.error('Error loading sales trend report:', error);
    }
}

function renderSalesTrendReport(reportData) {
    const container = document.getElementById('salesTrendReport');
    if (!container) return;
    
    const dailyData = reportData.daily || [];
    const monthlyData = reportData.monthly || [];
    
    let html = `
        <div class="report-section">
            <h2>📈 Sales Trend Report</h2>
    `;
    
    if (dailyData && dailyData.length > 0) {
        html += `
            <h3>Daily Sales (Last 7 Days)</h3>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Sales Count</th>
                        <th>Total Amount</th>
                    </tr>
                </thead>
                <tbody>
                    ${dailyData.map(row => `
                        <tr>
                            <td>${new Date(row.date).toLocaleDateString('en-IN')}</td>
                            <td>${row.count}</td>
                            <td>₹${parseFloat(row.total).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
    
    if (monthlyData && monthlyData.length > 0) {
        html += `
            <h3>Monthly Sales</h3>
            <table>
                <thead>
                    <tr>
                        <th>Month</th>
                        <th>Sales Count</th>
                        <th>Total Amount</th>
                    </tr>
                </thead>
                <tbody>
                    ${monthlyData.map(row => `
                        <tr>
                            <td>${row.month}</td>
                            <td>${row.count}</td>
                            <td>₹${parseFloat(row.total).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
    
    if ((!dailyData || dailyData.length === 0) && (!monthlyData || monthlyData.length === 0)) {
        html += `<p class="text-center">No sales data available</p>`;
    }
    
    html += `</div>`;
    
    container.innerHTML = html;
}

function exportReportToCSV(reportType) {
    alert(`Exporting ${reportType} report... (Feature coming soon)`);
}

function printReport() {
    window.print();
}

console.log('Reports.js loaded successfully');
