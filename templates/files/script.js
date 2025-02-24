// let logbtn=document.querySelector(".log-in")
// logbtn.addEventListener('click',()=>{
//     window.location.href = "login.html";
// })

// script.js
let income = 0;
let expenses = [];
let budgets = {};

document.getElementById('income').addEventListener('change', () => {
    income = parseFloat(document.getElementById('income').value) || 0;
    updateSummary();
});


function addExpense() {
    const category = document.getElementById('category').value;
    const amount = parseFloat(document.getElementById('amount').value) || 0;
    const date = new Date().toLocaleDateString(); // Get current date
    expenses.push({ category, amount, date });
    renderExpenses();
    updateSummary();
    document.getElementById('amount').value = ''; // Clear input field
}

function setBudget() {
    const category = document.getElementById('budget-category').value;
    const amount = parseFloat(document.getElementById('budget-amount').value) || 0;
    budgets[category] = amount;
    renderBudgets();
    updateSummary();
    document.getElementById('budget-amount').value = ''; // Clear input field
}

function renderExpenses() {
    const tableBody = document.getElementById('expense-table').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = ''; // Clear existing rows
    expenses.forEach(expense => {
        const row = tableBody.insertRow();
        const categoryCell = row.insertCell();
        const amountCell = row.insertCell();
        const dateCell = row.insertCell();
        const actionCell = row.insertCell();

        categoryCell.textContent = expense.category;
        amountCell.textContent = expense.amount;
        dateCell.textContent = expense.date;
        actionCell.innerHTML = '<button onclick="deleteExpense(this)">Delete</button>'; // Delete button
    });
}

function renderBudgets() {
    const tableBody = document.getElementById('budget-table').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = ''; // Clear existing rows
    for (const category in budgets) {
        const row = tableBody.insertRow();
        const categoryCell = row.insertCell();
        const amountCell = row.insertCell();

        categoryCell.textContent = category;
        amountCell.textContent = budgets[category];
    }
}

function deleteExpense(button) {
    const row = button.parentNode.parentNode; // Get the row to delete
    const index = row.rowIndex - 1; // Get the row index (subtract 1 for header)
    expenses.splice(index, 1); // Remove from array
    renderExpenses(); // Re-render table
    updateSummary(); // Update summary
}

function updateSummary() {
    const totalExpenses = expenses.reduce((sum, expense) => sum + expense.amount, 0);
    const remainingBudget = income - totalExpenses;
    const savings = remainingBudget; // In this basic example, savings = remaining budget

    document.getElementById('total-expenses').textContent = totalExpenses.toFixed(2);
    document.getElementById('remaining-budget').textContent = remainingBudget.toFixed(2);
    document.getElementById('savings').textContent = savings.toFixed(2);
}

// Initial render (if needed)
renderExpenses();
renderBudgets();