// Customer Management Module

async function loadCustomers() {
    try {
        const response = await fetch(`${API_URL}/customers/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            renderCustomersTable(data.data);
        }
    } catch (error) {
        console.error('Error loading customers:', error);
        const container = document.getElementById('customersTable');
        if (container) {
            container.innerHTML = '<p style="color: red;">Error loading customers. Please refresh.</p>';
        }
    }
}

function renderCustomersTable(customers) {
    const container = document.getElementById('customersTable');
    if (!container) return;

    if (!customers || customers.length === 0) {
        container.innerHTML = '<p class="text-center">No customers found</p>';
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Customer Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Total Purchases</th>
                    <th>Total Spent</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${customers.map(customer => `
                    <tr>
                        <td>${customer.customer_name || 'N/A'}</td>
                        <td>${customer.email || 'N/A'}</td>
                        <td>${customer.phone || 'N/A'}</td>
                        <td>${customer.total_purchases || 0}</td>
                        <td>₹${parseFloat(customer.total_spent || 0).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        <td>
                            <button class="btn btn-sm btn-secondary" onclick="editCustomer(${customer.id})">Edit</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteCustomer(${customer.id})">Delete</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function showAddCustomerModal() {
    const modalContainer = document.getElementById('modalContainer');
    modalContainer.innerHTML = `
        <div class="modal active">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add New Customer</h3>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <form id="customerForm" onsubmit="submitCustomer(event)">
                    <div class="form-group">
                        <label>Customer Name *</label>
                        <input type="text" name="customer_name" required>
                    </div>
                    <div class="form-group">
                        <label>Email *</label>
                        <input type="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" name="phone">
                    </div>
                    <div class="form-group">
                        <label>Address</label>
                        <textarea name="address" rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Create Customer</button>
                </form>
            </div>
        </div>
    `;
}

async function submitCustomer(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    try {
        const response = await fetch(`${API_URL}/customers/create/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (result.success) {
            alert(`Customer created successfully! ID: ${result.data.id}`);
            closeModal();
            loadCustomers();
        } else {
            const errorMsg = result.error || result.message || JSON.stringify(result.errors);
            alert(`Error creating customer:\n${errorMsg}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error creating customer:\n${error.message}`);
    }
}

async function deleteCustomer(customerId) {
    if (!confirm('Are you sure you want to delete this customer?')) return;

    try {
        const response = await fetch(`${API_URL}/customers/${customerId}/delete/`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        const result = await response.json();
        
        if (result.success) {
            alert('Customer deleted successfully');
            loadCustomers();
        } else {
            alert(`Error deleting customer: ${result.error || result.message}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error deleting customer: ${error.message}`);
    }
}

async function editCustomer(customerId) {
    try {
        const response = await fetch(`${API_URL}/customers/${customerId}/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();
        const customer = result.data;

        const modalContainer = document.getElementById('modalContainer');
        modalContainer.innerHTML = `
            <div class="modal active">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Edit Customer</h3>
                        <button class="modal-close" onclick="closeModal()">&times;</button>
                    </div>
                    <form id="editCustomerForm" onsubmit="submitEditCustomer(event, ${customerId})">
                        <div class="form-group">
                            <label>Customer Name *</label>
                            <input type="text" name="customer_name" value="${customer.customer_name || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Email *</label>
                            <input type="email" name="email" value="${customer.email || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Phone</label>
                            <input type="tel" name="phone" value="${customer.phone || ''}">
                        </div>
                        <div class="form-group">
                            <label>Address</label>
                            <textarea name="address" rows="3">${customer.address || ''}</textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Update Customer</button>
                    </form>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading customer:', error);
        alert(`Error loading customer details: ${error.message}`);
    }
}

async function submitEditCustomer(event, customerId) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    try {
        const response = await fetch(`${API_URL}/customers/${customerId}/update/`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (result.success) {
            alert('Customer updated successfully');
            closeModal();
            loadCustomers();
        } else {
            alert(`Error updating customer: ${result.error || JSON.stringify(result.errors)}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error updating customer: ${error.message}`);
    }
}

function closeModal() {
    document.getElementById('modalContainer').innerHTML = '';
}

console.log('Customers.js loaded successfully');
