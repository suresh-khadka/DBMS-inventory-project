// Employee Management Module

async function loadEmployees() {
    try {
        const response = await fetch(`${API_URL}/employees/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            renderEmployeesTable(data.data);
        }
    } catch (error) {
        console.error('Error loading employees:', error);
        const container = document.getElementById('employeesTable');
        if (container) {
            container.innerHTML = '<p style="color: red;">Error loading employees. Please refresh.</p>';
        }
    }
}

function renderEmployeesTable(employees) {
    const container = document.getElementById('employeesTable');
    if (!container) return;

    if (!employees || employees.length === 0) {
        container.innerHTML = '<p class="text-center">No employees found</p>';
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Employee Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Salary</th>
                    <th>Hired Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${employees.map(emp => `
                    <tr>
                        <td>${emp.employee_name || 'N/A'}</td>
                        <td>${emp.email || 'N/A'}</td>
                        <td>${emp.phone || 'N/A'}</td>
                        <td>${emp.salary ? '₹' + parseFloat(emp.salary).toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2}) : 'N/A'}</td>
                        <td>${emp.hire_date || 'N/A'}</td>
                        <td>
                            <button class="btn btn-sm btn-secondary" onclick="editEmployee(${emp.id})">Edit</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteEmployee(${emp.id})">Delete</button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function showAddEmployeeModal() {
    const modalContainer = document.getElementById('modalContainer');
    modalContainer.innerHTML = `
        <div class="modal active">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add New Employee</h3>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <form id="employeeForm" onsubmit="submitEmployee(event)">
                    <div class="form-group">
                        <label>Employee Name *</label>
                        <input type="text" name="employee_name" required>
                    </div>
                    <div class="form-group">
                        <label>Username *</label>
                        <input type="text" name="username" required>
                        <small>Used for login</small>
                    </div>
                    <div class="form-group">
                        <label>Password *</label>
                        <input type="password" name="password" required>
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
                        <label>Salary *</label>
                        <input type="number" name="salary" step="0.01" required>
                    </div>
                    <div class="form-group">
                        <label>Hire Date *</label>
                        <input type="date" name="hire_date" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Create Employee</button>
                </form>
            </div>
        </div>
    `;
}

async function submitEmployee(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    try {
        const response = await fetch(`${API_URL}/employees/create/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (result.success) {
            alert(`Employee created successfully! Username: ${result.username}`);
            closeModal();
            loadEmployees();
        } else {
            const errorMsg = result.error || result.message || JSON.stringify(result.errors);
            alert(`Error creating employee:\n${errorMsg}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error creating employee:\n${error.message}`);
    }
}

async function deleteEmployee(employeeId) {
    if (!confirm('Are you sure you want to delete this employee?')) return;

    try {
        const response = await fetch(`${API_URL}/employees/${employeeId}/delete/`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        const result = await response.json();
        
        if (result.success) {
            alert('Employee deleted successfully');
            loadEmployees();
        } else {
            alert(`Error deleting employee: ${result.error || result.message}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error deleting employee: ${error.message}`);
    }
}

async function editEmployee(employeeId) {
    try {
        const response = await fetch(`${API_URL}/employees/${employeeId}/`, {
            method: 'GET',
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();
        const emp = result.data;

        const modalContainer = document.getElementById('modalContainer');
        modalContainer.innerHTML = `
            <div class="modal active">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Edit Employee</h3>
                        <button class="modal-close" onclick="closeModal()">&times;</button>
                    </div>
                    <form id="editEmployeeForm" onsubmit="submitEditEmployee(event, ${employeeId})">
                        <div class="form-group">
                            <label>Employee Name *</label>
                            <input type="text" name="employee_name" value="${emp.employee_name || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Email *</label>
                            <input type="email" name="email" value="${emp.email || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Phone</label>
                            <input type="tel" name="phone" value="${emp.phone || ''}">
                        </div>
                        <div class="form-group">
                            <label>Salary *</label>
                            <input type="number" name="salary" step="0.01" value="${emp.salary || ''}" required>
                        </div>
                        <div class="form-group">
                            <label>Hire Date *</label>
                            <input type="date" name="hire_date" value="${emp.hire_date || ''}" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Update Employee</button>
                    </form>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading employee:', error);
        alert(`Error loading employee details: ${error.message}`);
    }
}

async function submitEditEmployee(event, employeeId) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    try {
        const response = await fetch(`${API_URL}/employees/${employeeId}/update/`, {
            method: 'PUT',
            headers: getAuthHeaders(),
            body: JSON.stringify(data)
        });

        const result = await response.json();
        
        if (result.success) {
            alert('Employee updated successfully');
            closeModal();
            loadEmployees();
        } else {
            alert(`Error updating employee: ${result.error || JSON.stringify(result.errors)}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error updating employee: ${error.message}`);
    }
}

function closeModal() {
    document.getElementById('modalContainer').innerHTML = '';
}

console.log('Employees.js loaded successfully');