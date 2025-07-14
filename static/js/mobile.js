// Mobile-specific JavaScript enhancements for KitchenCrate

document.addEventListener('DOMContentLoaded', function() {
    window.scrollTo(0, 0); // Always scroll to top on page load
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        initializeMobileEnhancements();
    }
    
    function initializeMobileEnhancements() {
        // Enhanced touch feedback
        enhanceTouchFeedback();
        
        // Mobile navigation improvements
        enhanceMobileNavigation();
        
        // Form improvements
        enhanceMobileForms();
        
        // Payment method selection
        enhancePaymentSelection();
    }
    
    function enhanceTouchFeedback() {
        const buttons = document.querySelectorAll('.btn, .nav-link, .dropdown-item');
        
        buttons.forEach(button => {
            button.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.95)';
                this.style.transition = 'transform 0.1s ease';
            });
            
            button.addEventListener('touchend', function() {
                this.style.transform = '';
                this.style.transition = '';
            });
        });
    }
    
    function enhanceMobileNavigation() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarToggler && navbarCollapse) {
            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                    if (navbarCollapse.classList.contains('show')) {
                        navbarToggler.click();
                    }
                }
            });
            
            // Close menu when clicking on links
            const navLinks = navbarCollapse.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    if (navbarCollapse.classList.contains('show')) {
                        setTimeout(() => {
                            navbarToggler.click();
                        }, 100);
                    }
                });
            });
        }
    }
    
    function enhanceMobileForms() {
        // Prevent zoom on input focus (iOS)
        const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], input[type="number"], textarea');
        
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.style.fontSize = '16px';
            });
            
            input.addEventListener('blur', function() {
                this.style.fontSize = '';
            });
        });
    }
    
    function enhancePaymentSelection() {
        const paymentOptions = document.querySelectorAll('.payment-option');
        
        paymentOptions.forEach(option => {
            const label = option.querySelector('.payment-label');
            const radio = option.querySelector('.payment-radio');
            
            if (label && radio) {
                label.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Uncheck all other options
                    paymentOptions.forEach(opt => {
                        opt.classList.remove('selected');
                        const optRadio = opt.querySelector('.payment-radio');
                        if (optRadio) optRadio.checked = false;
                    });
                    
                    // Check this option
                    option.classList.add('selected');
                    radio.checked = true;
                    
                    // Add visual feedback
                    this.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        this.style.transform = '';
                    }, 150);
                });
            }
        });
    }
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 100);
    });
}); 