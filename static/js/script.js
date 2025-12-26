// ai_healthcare_portal/static/js/main.js

/**
 * Global functions for UI interaction across the site.
 */

document.addEventListener('DOMContentLoaded', () => {
    // ------------------------------------------
    // 1. Flash Message Auto-Hide Logic
    // ------------------------------------------
    const flashMessages = document.querySelectorAll('.flash-messages .alert');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transition = 'opacity 0.5s ease-out';
            setTimeout(() => msg.remove(), 500);
        }, 5000); // Messages fade after 5 seconds
    });

    // ------------------------------------------
    // 2. Dashboard Utility - Toggle Details Row
    // ------------------------------------------
    const detailButtons = document.querySelectorAll('[data-toggle]');
    detailButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-toggle');
            const detailsRow = document.getElementById(targetId);
            if (detailsRow) {
                detailsRow.classList.toggle('hidden');
                this.textContent = detailsRow.classList.contains('hidden') ? 'View Details' : 'Hide Details';
            }
        });
    });

    // ------------------------------------------
    // NOTE: The main form and prediction logic for detect.html 
    // is currently in the <script> block of detect.html to access 
    // the Jinja2 variables easily. For a larger app, you'd fetch 
    // the DISEASE_PARAMETERS via an API endpoint instead.
    // ------------------------------------------
});


/**
 * Helper function to map risk result to CSS class for dynamic styling.
 * (Used by the partials/prediction_result.html template)
 */
function getResultClass(result) {
    switch (result) {
        case 'Healthy': return 'result-healthy';
        case 'Borderline': return 'result-borderline';
        case 'Risky': return 'result-risky';
        default: return 'result-unknown';
    }
}

// Attach the helper function to the window object so it's globally available for Jinja
window.getResultClass = getResultClass;