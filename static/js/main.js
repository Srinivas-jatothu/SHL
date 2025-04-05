// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Handle form submission with loading indicator
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Create and show loading overlay
            const loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-white bg-opacity-75';
            loadingOverlay.style.zIndex = '9999';
            
            const loadingContent = document.createElement('div');
            loadingContent.className = 'text-center';
            
            const spinner = document.createElement('div');
            spinner.className = 'loader';
            
            const loadingText = document.createElement('p');
            loadingText.className = 'mt-3 text-primary fw-bold';
            loadingText.textContent = 'Analyzing job description...';
            
            loadingContent.appendChild(spinner);
            loadingContent.appendChild(loadingText);
            loadingOverlay.appendChild(loadingContent);
            
            document.body.appendChild(loadingOverlay);
            
            // Form will submit normally
        });
    });

    // Sample job description options
    const sampleDescriptions = [
        'Senior Software Engineer with Java expertise',
        'Financial Analyst with Excel and reporting skills',
        'Customer Service Representative for retail company',
        'Sales Manager with 5+ years of experience',
        'Project Manager for IT department'
    ];

    // Add sample description placeholder
    const jobTextarea = document.getElementById('job_description');
    if (jobTextarea) {
        const randomSample = sampleDescriptions[Math.floor(Math.random() * sampleDescriptions.length)];
        jobTextarea.placeholder = `Example: ${randomSample}`;
    }

    // Handle tab switching
    const textTab = document.getElementById('text-tab');
    const urlTab = document.getElementById('url-tab');
    const textPane = document.getElementById('text-pane');
    const urlPane = document.getElementById('url-pane');

    if (textTab && urlTab) {
        // Clear inputs when switching tabs
        textTab.addEventListener('click', function() {
            const urlInput = document.getElementById('job_url');
            if (urlInput) {
                urlInput.value = '';
            }
        });

        urlTab.addEventListener('click', function() {
            const textInput = document.getElementById('job_description');
            if (textInput) {
                textInput.value = '';
            }
        });
    }

    // Handle recommendation table interactions
    const clickableRows = document.querySelectorAll('.clickable-row');
    clickableRows.forEach(row => {
        row.addEventListener('click', function() {
            // Toggle active class for visual indication
            clickableRows.forEach(r => r.classList.remove('table-active'));
            this.classList.toggle('table-active');
        });
    });

    // Add URL validation
    const urlInput = document.getElementById('job_url');
    if (urlInput) {
        urlInput.addEventListener('input', function() {
            if (this.value && !isValidUrl(this.value)) {
                this.classList.add('is-invalid');
                
                // Add error message if not exists
                let errorMessage = this.nextElementSibling;
                if (!errorMessage || !errorMessage.classList.contains('invalid-feedback')) {
                    errorMessage = document.createElement('div');
                    errorMessage.className = 'invalid-feedback';
                    errorMessage.textContent = 'Please enter a valid URL';
                    this.parentNode.insertBefore(errorMessage, this.nextSibling);
                }
            } else {
                this.classList.remove('is-invalid');
                
                // Remove error message if exists
                const errorMessage = this.nextElementSibling;
                if (errorMessage && errorMessage.classList.contains('invalid-feedback')) {
                    errorMessage.remove();
                }
            }
        });
    }

    // Helper function to validate URLs
    function isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    // Handle "Show More" toggle for job description
    const showMoreBtn = document.getElementById('showMoreBtn');
    if (showMoreBtn) {
        showMoreBtn.addEventListener('click', function() {
            document.querySelector('.full-job-text').classList.remove('d-none');
            this.classList.add('d-none');
        });
    }

    // Add tooltip initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});