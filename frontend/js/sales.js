// Sales Management Module

async function loadSales() {
    try {
        const data = await API.getSales({ limit: 50 });
        if (data && data.success) {
            renderSalesTable(data.data);
        }
    } catch (error) {
        console.error('Error loading sales:', error);
    }
}

function renderSalesTable(sales) {
    const container = document.getElementById('salesTable');
    if (!container) return;

    if (!sales || sales.length === 0) {
        container.innerHTML = '<p class="text-center">No sales found</p>';
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Product</th>
                    <th>Barcode</th>
                    <th>Quantity</th>
                    <th>Amount</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                ${sales.map(sale => `
                    <tr>
                        <td>${sale.id}</td>
                        <td>${sale.product_name || 'N/A'}</td>
                        <td><code>${sale.barcode}</code></td>
                        <td>${sale.quantity_sold}</td>
                        <td>${formatCurrency(sale.total_amount)}</td>
                        <td>${new Date(sale.sale_date).toLocaleDateString()}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function showAddSaleModal() {
    // First load products for the dropdown
    API.getProducts().then(data => {
        if (!data || !data.success) {
            alert('Error loading products');
            return;
        }

        const products = data.data;
        const modalContainer = document.getElementById('modalContainer');
        modalContainer.innerHTML = `
            <div class="modal active">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>New Sale</h3>
                        <button class="modal-close" onclick="closeModal()">&times;</button>
                    </div>
                    <form id="saleForm" onsubmit="submitSale(event)">
                        <div class="form-group">
                            <label>Product *</label>
                            <select name="barcode" id="saleProduct" required onchange="updateSalePrice()">
                                <option value="">Select Product</option>
                                ${products.map(p => `
                                    <option value="${p.barcode}" 
                                            data-price="${p.selling_price}" 
                                            data-stock="${p.stock_level}">
                                        ${p.product_name} (${p.barcode}) - Stock: ${p.stock_level}
                                    </option>
                                `).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Quantity *</label>
                            <input type="number" name="quantity_sold" id="saleQuantity" min="1" required onchange="updateSaleTotal()">
                        </div>
                        <div class="form-group">
                            <label>Unit Price</label>
                            <input type="number" name="unit_price" id="salePrice" step="0.01" readonly>
                        </div>
                        <div class="form-group">
                            <label>Total Amount</label>
                            <input type="number" id="saleTotal" step="0.01" readonly>
                        </div>
                        <div class="form-group">
                            <label>Payment Method</label>
                            <select name="payment_method">
                                <option value="cash">Cash</option>
                                <option value="card">Card</option>
                                <option value="online">Online</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary">Process Sale</button>
                    </form>
                </div>
            </div>
        `;
    });
}

function updateSalePrice() {
    const select = document.getElementById('saleProduct');
    const priceInput = document.getElementById('salePrice');
    const option = select.options[select.selectedIndex];
    
    if (option && option.dataset.price) {
        priceInput.value = option.dataset.price;
        updateSaleTotal();
    }
}

function updateSaleTotal() {
    const quantity = parseFloat(document.getElementById('saleQuantity').value) || 0;
    const price = parseFloat(document.getElementById('salePrice').value) || 0;
    const total = quantity * price;
    document.getElementById('saleTotal').value = total.toFixed(2);
}

async function submitSale(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    // Check stock
    const select = document.getElementById('saleProduct');
    const option = select.options[select.selectedIndex];
    const stock = parseInt(option.dataset.stock);
    const quantity = parseInt(data.quantity_sold);

    if (quantity > stock) {
        alert(`Insufficient stock! Available: ${stock}`);
        return;
    }

    try {
        const result = await API.createSale(data);
        if (result && result.success) {
            alert('Sale processed successfully!');
            closeModal();
            loadSales();
        } else {
            alert('Error processing sale');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error processing sale');
    }
}

// Feature 9: Barcode Scanner
function showBarcodeScanner() {
    const scannerHTML = `
        <div class="barcode-scanner">
            <h3>Scan Barcode</h3>
            <input type="text" id="barcodeInput" placeholder="Enter or scan barcode" autofocus>
            <button onclick="searchByBarcode()">Search</button>
            <div id="scanResults"></div>
        </div>
    `;
    
    document.getElementById('scannerContainer').innerHTML = scannerHTML;
    
    // Auto-submit on Enter
    document.getElementById('barcodeInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchByBarcode();
        }
    });
}

async function searchByBarcode() {
    const barcode = document.getElementById('barcodeInput').value;
    
    if (!barcode) {
        alert('Please enter a barcode');
        return;
    }
    
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/products/barcode/${barcode}/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultsDiv = document.getElementById('scanResults');
            const discountPercentage = (data.product.discount_percentage && parseFloat(data.product.discount_percentage)) || 0;
            
            // Show product
            let html = `
                <div class="scanned-product">
                    <h4>${data.product.product_name}</h4>
                    <p>Barcode: ${data.product.barcode}</p>
                    <p>Price: ₹${data.product.final_price}</p>
                    ${data.product.has_discount ? `
                        <p class="discount">
                            Original: ₹${data.product.selling_price}
                            <span class="badge">${discountPercentage.toFixed(0)}% OFF</span>
                        </p>
                    ` : ''}
                    <p>Stock: ${data.product.stock_level}</p>
                </div>
            `;
            
            // Show recommendations
            if (data.recommendations.count > 0) {
                html += '<h4>Related Products:</h4>';
                data.recommendations.products.forEach(rec => {
                    html += `
                        <div class="recommendation">
                            <strong>${rec.product_name}</strong>
                            <span>₹${rec.final_price}</span>
                        </div>
                    `;
                });
            }
            
            resultsDiv.innerHTML = html;
        } else {
            alert(data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Barcode search failed');
    }
}

function closeModal() {
    const modalContainer = document.getElementById('modalContainer');
    if (modalContainer) {
        modalContainer.innerHTML = '';
    }
}