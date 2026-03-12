// Products Management Module
// import { API } from './api.js';

let allProducts = []; // Store all products for search
let isSubmittingProduct = false; // Prevent race condition on product submission

function renderProductsTable(products) {
    const container = document.getElementById('productsTable');
    if (!container) return;

    if (!products || products.length === 0) {
        container.innerHTML = '<p class="text-center">No products found</p>';
        return;
    }

    const currentUser = getCurrentUser();
    const isCustomer = currentUser && currentUser.role === 'customer';

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Barcode</th>
                    <th>Product Name</th>
                    <th>Category</th>
                    <th>Price</th>
                    <th>price after Discount</th>
                    <th>Stock</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${products.map(product => {
                    const hasDiscount = product.discount_price && product.discount_price < product.selling_price;
                    const discountPercentage = (product.discount_percentage && parseFloat(product.discount_percentage)) || 0;
                    const actionsHtml = isCustomer ? `
                        <td>
                            ${product.stock_level > 0 ? `
                                <button class="btn btn-sm btn-primary" onclick="showBuyModal('${product.barcode}', '${product.product_name}', ${product.discount_price || product.selling_price})">Buy</button>
                            ` : `
                                <button class="btn btn-sm btn-danger" disabled>Out of Stock</button>
                            `}
                        </td>
                    ` : `
                        <td>
                            <button class="btn btn-sm btn-secondary" onclick="editProduct('${product.barcode}')">Edit</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteProduct('${product.barcode}')">Delete</button>
                        </td>
                    `;
                    return `
                        <tr>
                            <td><code>${product.barcode}</code></td>
                            <td>${product.product_name}</td>
                            <td>${product.category || 'N/A'}</td>
                            <td>
                                ${hasDiscount ? `
                                    <div style="font-size: 0.9em;">
                                        <s>Rs${parseFloat(product.selling_price).toFixed(2)}</s>
                                    </div>
                                    <strong style="color: #ff4444;">Rs${parseFloat(product.discount_price).toFixed(2)}</strong>
                                    <div style="font-size: 0.8em; color: green; font-weight: bold;">${discountPercentage.toFixed(0)}% OFF</div>
                                ` : `
                                    Rs${parseFloat(product.selling_price).toFixed(2)}
                                `}
                            </td>
                            <td>${hasDiscount ? `Rs${(parseFloat(product.selling_price) - parseFloat(product.discount_price)).toFixed(2)}` : '-'}</td>
                            <td>${product.stock_level}</td>
                            ${actionsHtml}
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
}

function filterProducts(searchTerm) {
    if (!searchTerm.trim()) {
        renderProductsTable(allProducts);
        return;
    }
    
    const filtered = allProducts.filter(product => 
        product.barcode.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.product_name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    renderProductsTable(filtered);
}


async function loadProducts() {
    try {
        const data = await API.getProducts();
        if (data && data.success) {
            allProducts = data.data;
            // Sort products by creation date (most recent first) or by ID in reverse order
            if (allProducts && allProducts.length > 0) {
                allProducts.sort((a, b) => {
                    // Try sorting by created_at first
                    if (a.created_at && b.created_at) {
                        return new Date(b.created_at) - new Date(a.created_at);
                    }
                    // Fallback: sort by ID in reverse (assumes incrementing ID)
                    return (parseInt(b.id) || 0) - (parseInt(a.id) || 0);
                });
            }
            renderProductsTable(allProducts);
        }
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// products.js - Display products with discount

function renderProductCard(product) {
    const hasDiscount = product.discount_price && product.discount_price < product.selling_price;
    const discountPercentage = (product.discount_percentage && parseFloat(product.discount_percentage)) || 0;
    const currentUser = getCurrentUser();
    const isCustomer = currentUser && currentUser.role === 'customer';
    
    const actionsHtml = isCustomer ? `
        <div class="actions">
            ${product.stock_level > 0 ? `
                <button class="btn btn-primary" onclick="showBuyModal('${product.barcode}', '${product.product_name}', ${product.discount_price || product.selling_price})">Buy Now</button>
            ` : `
                <button class="btn btn-danger" disabled>Out of Stock</button>
            `}
        </div>
    ` : `
        <div class="actions">
            <button onclick="editProduct('${product.barcode}')">Edit</button>
            <button onclick="deleteProduct('${product.barcode}')">Delete</button>
        </div>
    `;
    
    return `
        <div class="product-card">
            <div class="product-header">
                <h3>${product.product_name}</h3>
                <code class="barcode">${product.barcode}</code>
            </div>
            
            <p class="description">${product.description || 'No description'}</p>
            
            <div class="pricing">
                ${hasDiscount ? `
                    <div class="discount-pricing">
                        <div class="original-price">
                            <s>Rs${parseFloat(product.selling_price).toFixed(2)}</s>
                        </div>
                        <div class="discount-price" style="color: #ff4444; font-size: 1.3em; font-weight: bold;">
                            Rs${parseFloat(product.discount_price).toFixed(2)}
                        </div>
                        <div class="discount-badge" style="color: green; font-weight: bold;">${discountPercentage.toFixed(0)}% OFF</div>
                        <div class="savings" style="color: green; font-size: 0.9em;">
                            Save Rs${(parseFloat(product.selling_price) - parseFloat(product.discount_price)).toFixed(2)}
                        </div>
                    </div>
                ` : `
                    <div class="regular-price">
                        <strong>Rs${parseFloat(product.selling_price).toFixed(2)}</strong>
                    </div>
                `}
            </div>
            
            <div class="stock-info">
                <span>Stock: ${product.stock_level}</span>
                <span class="category">${product.category || 'Uncategorized'}</span>
            </div>
            
            ${actionsHtml}
        </div>
    `;
}

function showAddProductModal() {
    const modalContainer = document.getElementById('modalContainer');
    modalContainer.innerHTML = `
        <div class="modal active">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add New Product</h3>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <form id="productForm" onsubmit="submitProduct(event)">
                    <div class="form-group">
                        <label>Product Name *</label>
                        <input type="text" name="product_name" required>
                        <small>Barcode will be auto-generated from product name</small>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea name="description" rows="3"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Cost Price *</label>
                        <input type="number" name="cost_price" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label>Selling Price *</label>
                        <input type="number" name="selling_price" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label>Stock Level *</label>
                        <input type="number" name="stock_level" value="0" required>
                    </div>
                    <div class="form-group">
                        <label>Min Stock Level</label>
                        <input type="number" name="min_stock_level" value="10">
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <input type="text" name="category">
                    </div>
                    <div class="form-group">
                        <label>Supplier</label>
                        <input type="text" name="supplier">
                    </div>
                    <button type="submit" class="btn btn-primary">Create Product</button>
                </form>
            </div>
        </div>
    `;
}

async function submitProduct(event) {
    event.preventDefault();
    
    if (isSubmittingProduct) {
        alert('Please wait for the current submission to complete');
        return;
    }
    isSubmittingProduct = true;
    
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Adding...';
    
    // Collect form data carefully
    const formData = new FormData(form);
    const data = {};
    
    // Manually build data object to ensure each field is captured correctly
    data['product_name'] = (formData.get('product_name') || '').trim();
    data['description'] = (formData.get('description') || '').trim();
    data['cost_price'] = formData.get('cost_price');
    data['selling_price'] = formData.get('selling_price');
    data['discount_price'] = formData.get('discount_price');
    data['stock_level'] = formData.get('stock_level');
    data['min_stock_level'] = formData.get('min_stock_level');
    data['category'] = (formData.get('category') || '').trim();
    data['supplier'] = (formData.get('supplier') || '').trim();
    
    // Validate required fields
    if (!data.product_name) {
        alert('Product name is required');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
        isSubmittingProduct = false;
        return;
    }
    if (!data.cost_price || !data.selling_price || !data.stock_level) {
        alert('Cost Price, Selling Price, and Stock Level are required');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
        isSubmittingProduct = false;
        return;
    }
    
    console.log('Submitting product data:', JSON.stringify(data));

    try {
        const result = await API.createProduct(data);
        console.log('API Response:', result);
        if (result && result.success) {
            alert(`Product created successfully! Barcode: ${result.product.barcode}`);
            form.reset();
            closeModal();
            await loadProducts();
        } else {
            const errorMsg = result.errors ? JSON.stringify(result.errors) : (result.error || 'Unknown error');
            alert(`Error creating product: ${errorMsg}`);
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error creating product: ${error.message}`);
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    } finally {
        isSubmittingProduct = false;
    }
}

function closeModal() {
    document.getElementById('modalContainer').innerHTML = '';
}

async function editProduct(barcode) {
    try {
        const response = await fetch(`${API_URL}/products/${barcode}/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();
        const product = result.data;

        const modalContainer = document.getElementById('modalContainer');
        modalContainer.innerHTML = `
            <div class="modal active">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Edit Product</h3>
                        <button class="modal-close" onclick="closeModal()">&times;</button>
                    </div>
                    <form id="editProductForm" onsubmit="submitEditProduct(event, '${barcode}')">
                        <div class="form-group">
                            <label>Product Name *</label>
                            <input type="text" name="product_name" value="${product.product_name || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea name="description" rows="3">${product.description || ''}</textarea>
                        </div>
                        <div class="form-group">
                            <label>Cost Price *</label>
                            <input type="number" name="cost_price" step="0.01" value="${product.cost_price || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Selling Price *</label>
                            <input type="number" name="selling_price" step="0.01" value="${product.selling_price || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Discount Price (Optional)</label>
                            <input type="number" name="discount_price" step="0.01" value="${product.discount_price || ''}" placeholder="Leave empty for no discount">
                            <small>Price must be less than selling price</small>
                        </div>
                        <div class="form-group">
                            <label>Stock Level *</label>
                            <input type="number" name="stock_level" value="${product.stock_level || 0}" required>
                        </div>
                        <div class="form-group">
                            <label>Min Stock Level</label>
                            <input type="number" name="min_stock_level" value="${product.min_stock_level || 10}">
                        </div>
                        <div class="form-group">
                            <label>Category</label>
                            <input type="text" name="category" value="${product.category || ''}">
                        </div>
                        <div class="form-group">
                            <label>Supplier</label>
                            <input type="text" name="supplier" value="${product.supplier || ''}">
                        </div>
                        <button type="submit" class="btn btn-primary">Update Product</button>
                    </form>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading product:', error);
        alert(`Error loading product details: ${error.message}`);
    }
}

async function submitEditProduct(event, barcode) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    try {
        const response = await fetch(`${API_URL}/products/${barcode}/update/`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (result.success) {
            alert('Product updated successfully');
            closeModal();
            loadProducts();
        } else {
            alert(`Error updating product: ${result.error || JSON.stringify(result.errors)}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error updating product: ${error.message}`);
    }
}

async function deleteProduct(barcode) {
    if (!confirm('Are you sure you want to delete this product?')) return;

    try {
        const result = await API.deleteProduct(barcode);
        if (result && result.success) {
            alert('Product deleted successfully');
            loadProducts();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting product');
    }
}
