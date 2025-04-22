document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Confirm before voting
    const voteForms = document.querySelectorAll('.vote-form');
    voteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const candidateName = this.querySelector('.candidate-name').textContent;
            if (!confirm(`Are you sure you want to vote for ${candidateName}?`)) {
                e.preventDefault();
            }
        });
    });

    // Real-time vote count update (example)
    if (document.getElementById('voteChart')) {
        fetch('/get_vote_data/')
            .then(response => response.json())
            .then(data => {
                const ctx = document.getElementById('voteChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: data,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    precision: 0
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            title: {
                                display: true,
                                text: 'Vote Distribution',
                                font: {
                                    size: 16
                                }
                            }
                        }
                    }
                });
            });
    }

    // Auto-update results every 30 seconds
    if (document.querySelector('.results-table')) {
        setInterval(() => {
            fetch('/results/')
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newTable = doc.querySelector('.results-table');
                    if (newTable) {
                        document.querySelector('.results-table').innerHTML = newTable.innerHTML;
                    }
                });
        }, 30000);
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

// Form validation for registration
function validateRegistration() {
    const password1 = document.getElementById('id_password1').value;
    const password2 = document.getElementById('id_password2').value;
    
    if (password1 !== password2) {
        alert('Passwords do not match!');
        return false;
    }
    
    if (password1.length < 8) {
        alert('Password must be at least 8 characters long!');
        return false;
    }
    
    return true;
}