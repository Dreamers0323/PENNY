document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality
    const tabs = document.querySelectorAll('.tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabContainer = this.closest('.tabs');
            const tabContents = tabContainer.nextElementSibling.parentElement.querySelectorAll('.tab-content');
            const targetTab = this.getAttribute('data-tab');
            
            // Update active tab
            tabContainer.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show target tab content, hide others
            tabContents.forEach(content => {
                if (content.id === `${targetTab}-tab`) {
                    content.classList.remove('hidden');
                    content.classList.add('active');
                } else {
                    content.classList.add('hidden');
                    content.classList.remove('active');
                }
            });
        });
    });
    
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                window.location.href = this.href;
            }
        });
    }

    // Signup form validation
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirm_password');
        const errorMessage = document.getElementById('errorMessage');
    
        // Create password strength meter
        const strengthMeter = document.createElement('div');
        strengthMeter.className = 'password-strength';
        const strengthBar = document.createElement('div');
        strengthBar.className = 'strength-meter';
        strengthMeter.appendChild(strengthBar);
    
        const strengthText = document.createElement('div');
        strengthText.className = 'strength-text';
    
        passwordInput.parentNode.appendChild(strengthMeter);
        passwordInput.parentNode.appendChild(strengthText);
    
        // Password strength calculation
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            let text = '';
        
            if (password.length > 0) {
                // Length check
                if (password.length >= 8) strength += 1;
            
                // Character variety checks
                if (/[A-Z]/.test(password)) strength += 1;
                if (/[0-9]/.test(password)) strength += 1;
                if (/[^A-Za-z0-9]/.test(password)) strength += 1;
            
                // Update strength meter
                strengthBar.classList.remove('strength-weak', 'strength-medium', 'strength-strong');
            
                if (strength <= 1) {
                    strengthBar.classList.add('strength-weak');
                    text = 'Weak password';
                } else if (strength <= 3) {
                    strengthBar.classList.add('strength-medium');
                    text = 'Medium strength password';
                } else {
                    strengthBar.classList.add('strength-strong');
                    text = 'Strong password';
                }
            } else {
                strengthBar.classList.remove('strength-weak', 'strength-medium', 'strength-strong');
                text = '';
            }
        
            strengthText.textContent = text;
        });
    
        // Form submission validation
        signupForm.addEventListener('submit', function(e) {
            let isValid = true;
            let errorMsg = '';
        
            // Username validation
            const username = document.getElementById('username').value;
            if (username.length < 3 || username.length > 20) {
                isValid = false;
                errorMsg = 'Username must be between 3 and 20 characters.';
            } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
                isValid = false;
                errorMsg = 'Username can only contain letters, numbers, and underscores.';
            }
        
            // Password validation
            const password = passwordInput.value;
            if (password.length < 8) {
                isValid = false;
                errorMsg = 'Password must be at least 8 characters long.';
            }
        
            // Password confirmation
            if (password !== confirmPasswordInput.value) {
                isValid = false;
                errorMsg = 'Passwords do not match.';
            }
        
            // Terms agreement
            if (!document.getElementById('terms').checked) {
                isValid = false;
                errorMsg = 'You must agree to the Terms of Service.';
            }
        
            if (!isValid) {
                e.preventDefault();
                errorMessage.textContent = errorMsg;
                errorMessage.style.display = 'block';
            
                // Hide error after 5 seconds
                setTimeout(() => {
                    errorMessage.style.display = 'none';
                }, 5000);
            }
        });
    }
    
    // NOTE: Chat functionality removed from here - handled by penny.js instead
    
    // Loan calculator
    const calculateBtn = document.getElementById('calculate-btn');
    if (calculateBtn) {
        calculateBtn.addEventListener('click', function() {
            alert('Loan calculation functionality would be implemented here.');
        });
    }
    
    // Background animation for login page
    if (document.body.classList.contains('login-page')) {
        const background = document.getElementById('backgroundAnimation');
        if (background) {
            const colors = ['rgba(187, 134, 252, 0.05)', 'rgba(156, 39, 176, 0.05)', 'rgba(103, 58, 183, 0.05)'];
            
            for (let i = 0; i < 15; i++) {
                const circle = document.createElement('div');
                circle.classList.add('circle');
                
                // Random properties
                const size = Math.random() * 100 + 50;
                const posX = Math.random() * window.innerWidth;
                const posY = Math.random() * window.innerHeight;
                const delay = Math.random() * 5;
                const duration = Math.random() * 10 + 15;
                const color = colors[Math.floor(Math.random() * colors.length)];
                
                // Apply styles
                circle.style.width = `${size}px`;
                circle.style.height = `${size}px`;
                circle.style.left = `${posX}px`;
                circle.style.top = `${posY}px`;
                circle.style.animationDelay = `${delay}s`;
                circle.style.animationDuration = `${duration}s`;
                circle.style.background = color;
                
                background.appendChild(circle);
            }
        }
        
        // Form validation - Only prevent default if validation fails
        const loginForm = document.getElementById('loginForm');
        const errorMessage = document.getElementById('errorMessage');
        
        if (loginForm) {
            loginForm.addEventListener('submit', function(e) {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                // Simple validation
                if (username.length < 3) {
                    e.preventDefault();
                    showError('Username must be at least 3 characters long');
                    return;
                }
                
                if (password.length < 6) {
                    e.preventDefault();
                    showError('Password must be at least 6 characters long');
                    return;
                }
                
                // If validation passes, allow form submission
            });
            
            function showError(message) {
                if (errorMessage) {
                    errorMessage.textContent = message;
                    errorMessage.style.display = 'block';
                    
                    // Hide error after 5 seconds
                    setTimeout(() => {
                        errorMessage.style.display = 'none';
                    }, 5000);
                }
            }
        }
    }
});