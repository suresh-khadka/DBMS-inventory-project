// Expense Management Module - CORRECTED VERSION

// const API_URL = 'http://127.0.0.1:8000/api';

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

// ==================== LOAD EXPENSES ====================

async function loadExpenses() {
    console.log('Loading expenses...');
    
    try {
        const response = await fetch(`${API_URL}/expenses/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        console.log('Expenses response status:', response.status);
        
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
        console.log('Expenses data:', data);
        
        if (data.success) {
            renderExpensesTable(data.data);
            loadExpenseSummary();
        } else {
            throw new Error(data.error || 'Failed to load expenses');
        }
    } catch (error) {
        console.error('Error loading expenses:', error);
        const container = document.getElementById('expensesTable');
        if (container) {
            container.innerHTML = '<p style="color: red;">Error loading expenses. Please refresh.</p>';
        }
    }
}

// ==================== RENDER EXPENSES TABLE ====================

function renderExpensesTable(expenses) {
    const container = document.getElementById('expensesTable');
    if (!container) {
        console.error('expensesTable container not found!');
        return;
    }

    if (!expenses || expenses.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px;">
                <p>No expenses found. Start by adding your first expense!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Amount</th>
                    <th>Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${expenses.map(expense => `
                    <tr>
                        <td>${expense.id}</td>
                        <td>${expense.expense_type || 'N/A'}</td>
                        <td>${expense.description || 'N/A'}</td>
                        <td>${formatCurrency(expense.amount)}</td>
                        <td>${formatDate(expense.expense_date)}</td>
                        <td>
                            <button class="btn btn-sm btn-secondary" onclick="editExpense(${expense.id})">Edit</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteExpense(${expense.id})">Delete</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ==================== LOAD EXPENSE SUMMARY ====================

async function loadExpenseSummary() {
    try {
        const response = await fetch(`${API_URL}/expenses/summary/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            console.warn('Expense summary endpoint not available');
            return;
        }
        
        const data = await response.json();
        console.log('Expense summary:', data);
        
        if (data.success) {
            const summaryEl = document.getElementById('expenseSummary');
            if (summaryEl) {
                summaryEl.innerHTML = `
                    <div class="expense-summary">
                        <h3>Total Expenses: ${formatCurrency(data.total_expenses)}</h3>
                        ${data.breakdown ? `
                            <div style="margin-top: 15px;">
                                <h4>Breakdown by Type:</h4>
                                ${data.breakdown.map(item => `
                                    <div style="display: flex; justify-content: space-between; padding: 5px 0;">
                                        <span>${item.expense_type}</span>
                                        <strong>${formatCurrency(item.total)}</strong>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error loading expense summary:', error);
    }
}

// ==================== SHOW ADD EXPENSE MODAL ====================

function showAddExpenseModal() {
    const modalContainer = document.getElementById('modalContainer');
    if (!modalContainer) {
        console.error('modalContainer not found!');
        alert('Modal container not found. Please refresh the page.');
        return;
    }
    
    modalContainer.innerHTML = `
        <div class="modal active">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add New Expense</h3>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <form id="expenseForm" onsubmit="submitExpense(event)">
                    <div class="form-group">
                        <label>Expense Type *</label>
                        <select name="expense_type" required>
                            <option value="">Select Type</option>
                            <option value="product_cost">Product Cost</option>
                            <option value="employee_salary">Employee Salary</option>
                            <option value="rent">Rent</option>
                            <option value="utilities">Utilities</option>
                            <option value="marketing">Marketing</option>
                            <option value="maintenance">Maintenance</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea name="description" rows="3" placeholder="Enter expense details..."></textarea>
                    </div>
                    <div class="form-group">
                        <label>Amount (₹) *</label>
                        <input type="number" name="amount" step="0.01" min="0.01" required placeholder="0.00">
                    </div>
                    <div class="form-group">
                        <label>Expense Date *</label>
                        <input type="date" name="expense_date" value="${new Date().toISOString().split('T')[0]}" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Create Expense</button>
                </form>
            </div>
        </div>
    `;
}

// ==================== SUBMIT EXPENSE ====================

async function submitExpense(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    console.log('Submitting expense:', data);

    try {
        const response = await fetch(`${API_URL}/expenses/add/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });

        console.log('Response status:', response.status);
        
        const result = await response.json();
        console.log('Response data:', result);
        
        if (response.ok && result.success) {
            alert('Expense created successfully!');
            closeModal();
            loadExpenses();
        } else {
            const errorMsg = result.error || result.message || JSON.stringify(result.errors || result);
            alert(`Error creating expense:\n${errorMsg}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error creating expense:\n${error.message}`);
    }
}

// ==================== DELETE EXPENSE ====================

async function deleteExpense(expenseId) {
    if (!confirm('Are you sure you want to delete this expense?')) return;

    console.log('Deleting expense:', expenseId);

    try {
        // Check if delete endpoint exists
        const response = await fetch(`${API_URL}/expenses/${expenseId}/`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        console.log('Delete response status:', response.status);
        
        const result = await response.json();
        console.log('Delete response data:', result);
        
        if (response.ok && result.success) {
            alert('Expense deleted successfully');
            loadExpenses();
        } else {
            alert(`Error deleting expense: ${result.error || result.message}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error deleting expense: ${error.message}`);
    }
}

// ==================== EDIT EXPENSE ====================

async function editExpense(expenseId) {
    console.log('Editing expense:', expenseId);
    
    try {
        const response = await fetch(`${API_URL}/expenses/${expenseId}/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();
        console.log('Expense data:', result);
        
        const expense = result.data || result;

        const modalContainer = document.getElementById('modalContainer');
        modalContainer.innerHTML = `
            <div class="modal active">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Edit Expense</h3>
                        <button class="modal-close" onclick="closeModal()">&times;</button>
                    </div>
                    <form id="editExpenseForm" onsubmit="submitEditExpense(event, ${expenseId})">
                        <div class="form-group">
                            <label>Expense Type *</label>
                            <select name="expense_type" required>
                                <option value="product_cost" ${expense.expense_type === 'product_cost' ? 'selected' : ''}>Product Cost</option>
                                <option value="employee_salary" ${expense.expense_type === 'employee_salary' ? 'selected' : ''}>Employee Salary</option>
                                <option value="rent" ${expense.expense_type === 'rent' ? 'selected' : ''}>Rent</option>
                                <option value="utilities" ${expense.expense_type === 'utilities' ? 'selected' : ''}>Utilities</option>
                                <option value="marketing" ${expense.expense_type === 'marketing' ? 'selected' : ''}>Marketing</option>
                                <option value="maintenance" ${expense.expense_type === 'maintenance' ? 'selected' : ''}>Maintenance</option>
                                <option value="other" ${expense.expense_type === 'other' ? 'selected' : ''}>Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea name="description" rows="3">${expense.description || ''}</textarea>
                        </div>
                        <div class="form-group">
                            <label>Amount (₹) *</label>
                            <input type="number" name="amount" step="0.01" value="${expense.amount || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Expense Date *</label>
                            <input type="date" name="expense_date" value="${expense.expense_date || ''}" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Update Expense</button>
                    </form>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading expense:', error);
        alert(`Error loading expense details: ${error.message}`);
    }
}

// ==================== SUBMIT EDIT EXPENSE ====================

async function submitEditExpense(event, expenseId) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    console.log('Updating expense:', expenseId, data);

    try {
        const response = await fetch(`${API_URL}/expenses/${expenseId}/`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });

        console.log('Update response status:', response.status);
        
        const result = await response.json();
        console.log('Update response data:', result);
        
        if (response.ok && result.success) {
            alert('Expense updated successfully');
            closeModal();
            loadExpenses();
        } else {
            alert(`Error updating expense: ${result.error || JSON.stringify(result.errors)}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error updating expense: ${error.message}`);
    }
}

// ==================== CLOSE MODAL ====================

function closeModal() {
    const modalContainer = document.getElementById('modalContainer');
    if (modalContainer) {
        modalContainer.innerHTML = '';
    }
}

// ==================== AUTO-LOAD ON EXPENSES VIEW ====================

// This will be called by ui.js when navigating to expenses view
if (typeof window !== 'undefined') {
    window.loadExpenses = loadExpenses;
    window.showAddExpenseModal = showAddExpenseModal;
    window.submitExpense = submitExpense;
    window.deleteExpense = deleteExpense;
    window.editExpense = editExpense;
    window.submitEditExpense = submitEditExpense;
}

console.log('Expenses.js loaded successfully');