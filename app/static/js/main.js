// Format number with commas
function formatNumber(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Format currency
function formatCurrency(amount) {
    return formatNumber(amount) + " تومان";
}

// Format date
function formatDate(date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}/${month}/${day}`;
}

// Show confirmation dialog
function confirmAction(message) {
    return confirm(message);
}

// Show success message
function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success mb-4';
    alert.innerHTML = `<span>${message}</span>`;
    document.querySelector('main').prepend(alert);
    setTimeout(() => alert.remove(), 3000);
}

// Show error message
function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-error mb-4';
    alert.innerHTML = `<span>${message}</span>`;
    document.querySelector('main').prepend(alert);
    setTimeout(() => alert.remove(), 3000);
}

// Handle form submission
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (form.dataset.confirm) {
                if (!confirmAction(form.dataset.confirm)) {
                    e.preventDefault();
                }
            }
        });
    });
});

// Handle flash messages
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => alert.remove(), 3000);
    });
}); 