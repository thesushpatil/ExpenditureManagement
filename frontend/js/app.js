/**
 * App Logic - Shared functions used across all pages.
 */

// ===== AUTH GUARD =====
function requireAuth() {
    if (!getAccessToken()) {
        window.location.href = 'login.html';
    }
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(e) {
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.querySelector('.menu-toggle');
    if (sidebar && sidebar.classList.contains('open')) {
        if (!sidebar.contains(e.target) && e.target !== menuBtn && !menuBtn.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    }
});

async function handleLogout() {
    await apiLogout();
    window.location.href = 'login.html';
}

async function loadUserName() {
    const profile = await apiGetProfile();
    if (profile) {
        const el = document.getElementById('user-name');
        if (el) el.textContent = profile.first_name || profile.username;
    }
}

// ===== TOAST =====
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${message}`;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
}

// ===== UTILITIES =====
function formatCurrency(amount) {
    return '₹' + Number(amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function getTodayDate() {
    return new Date().toISOString().split('T')[0];
}

function toggleForm(formId) {
    document.getElementById(formId).classList.toggle('hidden');
}

// ===== DASHBOARD =====
async function loadDashboard() {
    const data = await apiGetDashboard();
    if (!data) return;

    document.getElementById('stat-income').textContent = formatCurrency(data.total_income);
    document.getElementById('stat-expenses').textContent = formatCurrency(data.total_expenses);
    document.getElementById('stat-savings').textContent = formatCurrency(data.total_savings);
    document.getElementById('stat-balance').textContent = formatCurrency(data.balance);

    // Category chart
    const chartEl = document.getElementById('category-chart');
    const catData = data.expenses_by_category || [];
    if (catData.length === 0) {
        chartEl.innerHTML = '<p class="empty-state">No expense data this month</p>';
    } else {
        const max = Math.max(...catData.map(c => c.total));
        chartEl.innerHTML = '<div class="chart-bar-container">' + catData.map(item => `
            <div class="chart-bar-item">
                <span class="chart-bar-label">${item.category}</span>
                <div class="chart-bar-track">
                    <div class="chart-bar-fill" style="width:${(item.total/max)*100}%;background:${item.color||'#6366f1'}">
                        <span class="chart-bar-value">${Math.round((item.total/max)*100)}%</span>
                    </div>
                </div>
                <span class="chart-bar-amount">${formatCurrency(item.total)}</span>
            </div>`).join('') + '</div>';
    }

    // Budget overview
    const budgetEl = document.getElementById('budget-overview');
    const budgets = data.budget_overview || [];
    if (budgets.length === 0) {
        budgetEl.innerHTML = '<p class="empty-state">No budgets set this month</p>';
    } else {
        budgetEl.innerHTML = budgets.map(b => {
            const pct = b.percentage_used || 0;
            const cls = pct > 90 ? 'progress-red' : pct > 70 ? 'progress-yellow' : 'progress-green';
            return `<div style="margin-bottom:14px">
                <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">
                    <span>${b.category_name}</span><span style="font-weight:600">${formatCurrency(b.spent)} / ${formatCurrency(b.limit)}</span>
                </div>
                <div class="progress-bar"><div class="progress-fill ${cls}" style="width:${Math.min(pct,100)}%"></div></div>
            </div>`;
        }).join('');
    }

    // Recent expenses
    const tbody = document.getElementById('recent-expenses-table');
    const recent = data.recent_expenses || [];
    if (recent.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--gray-400)">No recent expenses</td></tr>';
    } else {
        tbody.innerHTML = recent.map(e => `<tr>
            <td><span class="category-badge"><span class="category-dot" style="background:${e.category_color}"></span>${e.category_name}</span></td>
            <td>${e.description || '-'}</td><td>${e.date}</td>
            <td class="amount-negative">${formatCurrency(e.amount)}</td>
        </tr>`).join('');
    }
}

// ===== EXPENSES =====
async function loadExpenses() {
    const params = {};
    const search = document.getElementById('exp-search');
    const cat = document.getElementById('exp-filter-category');
    const month = document.getElementById('exp-filter-month');
    if (search && search.value) params.search = search.value;
    if (cat && cat.value) params.category = cat.value;
    if (month && month.value) params.month = month.value;

    const expenses = await apiGetExpenses(params);
    const tbody = document.getElementById('expenses-table');
    const empty = document.getElementById('expenses-empty');

    if (expenses.length === 0) { tbody.innerHTML = ''; empty.classList.remove('hidden'); return; }
    empty.classList.add('hidden');
    tbody.innerHTML = expenses.map(e => `<tr>
        <td><span class="category-badge"><span class="category-dot" style="background:${e.category_color}"></span>${e.category_name}</span></td>
        <td>${e.description || '-'}</td><td>${e.date}</td>
        <td class="amount-negative">${formatCurrency(e.amount)}</td>
        <td><button class="btn-delete" onclick="deleteExpense(${e.id})"><i class="fas fa-trash"></i></button></td>
    </tr>`).join('');
}

async function deleteExpense(id) {
    if (!confirm('Delete this expense?')) return;
    if (await apiDeleteExpense(id)) { showToast('Deleted'); loadExpenses(); }
    else showToast('Failed', 'error');
}

// ===== INCOME =====
async function loadIncomes() {
    const incomes = await apiGetIncomes();
    const tbody = document.getElementById('income-table');
    const empty = document.getElementById('income-empty');

    if (incomes.length === 0) { tbody.innerHTML = ''; empty.classList.remove('hidden'); return; }
    empty.classList.add('hidden');
    tbody.innerHTML = incomes.map(i => `<tr>
        <td><span class="category-badge"><span class="category-dot" style="background:var(--green)"></span>${i.source}</span></td>
        <td>${i.description || '-'}</td><td>${i.date}</td>
        <td class="amount-positive">+${formatCurrency(i.amount)}</td>
        <td><button class="btn-delete" onclick="deleteIncome(${i.id})"><i class="fas fa-trash"></i></button></td>
    </tr>`).join('');
}

async function deleteIncome(id) {
    if (!confirm('Delete this income?')) return;
    if (await apiDeleteIncome(id)) { showToast('Deleted'); loadIncomes(); }
    else showToast('Failed', 'error');
}

// ===== SAVINGS =====
async function loadSavings() {
    const savings = await apiGetSavings();
    const summary = await apiGetSavingsSummary();
    const tbody = document.getElementById('savings-table');
    const empty = document.getElementById('savings-empty');

    if (summary) {
        const totalEl = document.getElementById('savings-total');
        const monthEl = document.getElementById('savings-monthly');
        if (totalEl) totalEl.textContent = formatCurrency(summary.total_savings);
        if (monthEl) monthEl.textContent = formatCurrency(summary.monthly_savings);
    }

    if (savings.length === 0) { tbody.innerHTML = ''; empty.classList.remove('hidden'); return; }
    empty.classList.add('hidden');
    tbody.innerHTML = savings.map(s => `<tr>
        <td><span class="category-badge"><span class="category-dot" style="background:var(--blue)"></span>${s.goal}</span></td>
        <td>${s.description || '-'}</td><td>${s.date}</td>
        <td class="amount-positive">+${formatCurrency(s.amount)}</td>
        <td><button class="btn-delete" onclick="deleteSaving(${s.id})"><i class="fas fa-trash"></i></button></td>
    </tr>`).join('');
}

async function deleteSaving(id) {
    if (!confirm('Delete this saving?')) return;
    if (await apiDeleteSaving(id)) { showToast('Deleted'); loadSavings(); }
    else showToast('Failed', 'error');
}

// ===== BUDGETS =====
async function loadBudgets() {
    const now = new Date();
    const budgets = await apiGetBudgets(now.getMonth() + 1, now.getFullYear());
    const grid = document.getElementById('budgets-grid');
    const empty = document.getElementById('budgets-empty');

    if (budgets.length === 0) { grid.innerHTML = ''; empty.classList.remove('hidden'); return; }
    empty.classList.add('hidden');
    grid.innerHTML = budgets.map(b => {
        const pct = b.percentage_used || 0;
        const cls = pct > 90 ? 'progress-red' : pct > 70 ? 'progress-yellow' : 'progress-green';
        const color = pct > 100 ? 'var(--red)' : pct > 70 ? 'var(--orange)' : 'var(--green)';
        return `<div class="budget-card">
            <div class="budget-card-header"><h4>${b.category_name}</h4>
                <button class="btn-delete" onclick="deleteBudget(${b.id})"><i class="fas fa-trash"></i></button></div>
            <div class="budget-stats"><span>${formatCurrency(b.spent)} spent</span><span>${formatCurrency(b.limit)} limit</span></div>
            <div class="progress-bar"><div class="progress-fill ${cls}" style="width:${Math.min(pct,100)}%"></div></div>
            <div class="budget-stats"><span style="color:${color};font-weight:600">${pct.toFixed(1)}% used</span>
                <span>${b.remaining >= 0 ? formatCurrency(b.remaining)+' left' : formatCurrency(Math.abs(b.remaining))+' over'}</span></div>
        </div>`;
    }).join('');
}

async function deleteBudget(id) {
    if (!confirm('Delete this budget?')) return;
    if (await apiDeleteBudget(id)) { showToast('Deleted'); loadBudgets(); }
    else showToast('Failed', 'error');
}

// ===== PDF EXPORT =====
async function exportExpensePDF() {
    const monthInput = document.getElementById('pdf-month');
    if (!monthInput || !monthInput.value) { showToast('Please select a month', 'error'); return; }

    const [year, month] = monthInput.value.split('-');
    const expenses = await apiGetExpenses({ month: monthInput.value });

    if (expenses.length === 0) { showToast('No expenses found for this month', 'error'); return; }

    const total = expenses.reduce((s, e) => s + parseFloat(e.amount), 0);
    const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];

    // Generate PDF-style HTML and open in new window for printing
    const html = `<!DOCTYPE html><html><head><title>Expense Report - ${monthNames[parseInt(month)-1]} ${year}</title>
    <style>
        body{font-family:Arial,sans-serif;padding:40px;color:#333}
        h1{text-align:center;color:#4f46e5;margin-bottom:5px}
        .subtitle{text-align:center;color:#666;margin-bottom:30px}
        table{width:100%;border-collapse:collapse;margin:20px 0}
        th{background:#4f46e5;color:white;padding:12px;text-align:left}
        td{padding:10px 12px;border-bottom:1px solid #eee}
        tr:nth-child(even){background:#f9fafb}
        .total{text-align:right;font-size:18px;font-weight:bold;margin-top:20px;color:#4f46e5}
        .footer{text-align:center;margin-top:40px;color:#999;font-size:12px}
        @media print{body{padding:20px}}
    </style></head><body>
    <h1>Expense Report</h1>
    <p class="subtitle">${monthNames[parseInt(month)-1]} ${year}</p>
    <table><thead><tr><th>Category</th><th>Description</th><th>Date</th><th>Amount</th></tr></thead><tbody>
    ${expenses.map(e => `<tr><td>${e.category_name}</td><td>${e.description||'-'}</td><td>${e.date}</td><td>₹${Number(e.amount).toLocaleString()}</td></tr>`).join('')}
    </tbody></table>
    <p class="total">Total Expenses: ₹${total.toLocaleString('en-IN',{minimumFractionDigits:2})}</p>
    <p class="footer">Generated by ExpManage on ${new Date().toLocaleDateString()}</p>
    <script>window.print();<\/script></body></html>`;

    const win = window.open('', '_blank');
    win.document.write(html);
    win.document.close();
}
