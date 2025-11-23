// Custom JavaScript for ERP System

// Alert dismissal
document.addEventListener('DOMContentLoaded', function() {
    // Handle alert close buttons
    const closeButtons = document.querySelectorAll('.btn-close');
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.transition = 'opacity 0.15s linear';
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.remove();
                }, 150);
            }
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.parentNode) {
                alert.style.transition = 'opacity 0.15s linear';
                alert.style.opacity = '0';
                setTimeout(function() {
                    if (alert && alert.parentNode) {
                        alert.remove();
                    }
                }, 150);
            }
        }, 5000);
    });
});

