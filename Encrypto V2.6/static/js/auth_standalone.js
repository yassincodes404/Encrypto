document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selectors ---
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const langToggle = document.getElementById('lang-toggle');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const switchToRegisterLink = document.getElementById('switch-to-register');
    const switchToLoginLink = document.getElementById('switch-to-login');
    const translatableElements = document.querySelectorAll('[data-translate]');
    const htmlElement = document.documentElement;
    const messageArea = document.getElementById('message-area');
    const termsLinkRegister = document.getElementById('terms-link-register');
    const termsModalOverlay = document.getElementById('terms-modal-overlay');
    const closeModalMain = document.getElementById('modal-close-main');
    const closeModalSecondary = document.getElementById('modal-close-secondary');
    const acceptTermsButton = document.getElementById('modal-accept-terms');
    const termsCheckbox = document.getElementById('terms-checkbox');
    const registerSubmitButton = document.getElementById('register-submit-button');
    const passwordToggleIcons = document.querySelectorAll('.password-toggle-icon');
    const allInputGroups = document.querySelectorAll('.input-group');

    // --- Translations Data ---
    const translations = {
        en: {
            page_title: "Login / Register - Encrypto",
            login_header: "Login",
            register_header: "Register",
            email_username_label: "Email", // Simplified for login
            email_label: "Email",
            password_label: "Password",
            confirm_password_label: "Confirm Password",
            fullname_label: "Username", // Changed from Full Name
            login_button: "Login",
            register_button: "Register",
            no_account_prompt: "Don't have an account?",
            register_link: "Register",
            have_account_prompt: "Already have an account?",
            login_link: "Login",
            lang_toggle: "AR", // Button shows the OTHER language
            agree_text_start: "I agree to the",
            terms_link_inline: "Terms & Conditions",
            modal_close_button: "Close",
            modal_accept_button: "Accept",
            terms_link: "View Terms & Conditions", // Not directly used, kept for reference
            terms_modal_title: "Terms & Conditions",
            show_password_label: "Show password",
            hide_password_label: "Hide password",
            passwords_no_match: "Passwords do not match!",
            terms_agree_required: "You must agree to the Terms & Conditions."
        },
        ar: {
            page_title: "تسجيل الدخول / تسجيل - Encrypto",
            login_header: "تسجيل الدخول",
            register_header: "تسجيل حساب جديد",
            email_username_label: "البريد الإلكتروني", // Simplified for login
            email_label: "البريد الإلكتروني",
            password_label: "كلمة المرور",
            confirm_password_label: "تأكيد كلمة المرور",
            fullname_label: "اسم المستخدم", // Changed from Full Name
            login_button: "تسجيل الدخول",
            register_button: "تسجيل",
            no_account_prompt: "ليس لديك حساب؟",
            register_link: "سجل الآن",
            have_account_prompt: "هل لديك حساب بالفعل؟",
            login_link: "تسجيل الدخول",
            lang_toggle: "EN", // Button shows the OTHER language
            agree_text_start: "أوافق على",
            terms_link_inline: "الشروط والأحكام",
            modal_close_button: "إغلاق",
            modal_accept_button: "قبول",
            terms_link: "عرض الشروط والأحكام", // Not directly used, kept for reference
            terms_modal_title: "الشروط والأحكام",
            show_password_label: "إظهار كلمة المرور",
            hide_password_label: "إخفاء كلمة المرور",
            passwords_no_match: "كلمتا المرور غير متطابقتين!",
            terms_agree_required: "يجب الموافقة على الشروط والأحكام."
        }
    };

    // --- State Variables ---
    let currentLang = localStorage.getItem('language') || 'en';
    let currentTheme = localStorage.getItem('theme') || 'light'; // Default to light

    // --- Core Functions ---

    function applyTranslations() {
        const langPack = translations[currentLang];
        translatableElements.forEach(el => {
            const key = el.dataset.translate;
            if (langPack[key]) {
                // Handle specific elements or use textContent directly
                if (el.tagName === 'INPUT' && el.type !== 'checkbox' && el.type !== 'hidden') {
                    el.setAttribute('aria-label', langPack[key]); // Update aria-label for inputs
                } else {
                    el.textContent = langPack[key]; // Update text for most elements
                }
            }
        });

        // Set button text for language toggle
        langToggle.textContent = langPack.lang_toggle;

        // Update password toggle aria-labels
        updatePasswordToggleLabels();

        // Set HTML attributes
        htmlElement.lang = currentLang;
        htmlElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';

        // Store preference
        localStorage.setItem('language', currentLang);
        console.log(`Language applied: ${currentLang}`);
    }

    function applyTheme() {
        htmlElement.dataset.theme = currentTheme; // Use data attribute for CSS targeting
        if (currentTheme === 'dark') {
            themeIcon.className = 'fa-solid fa-moon';
            themeToggle.setAttribute('aria-label', 'Switch to light mode');
        } else {
            themeIcon.className = 'fa-solid fa-sun';
            themeToggle.setAttribute('aria-label', 'Switch to dark mode');
        }
        // Store preference
        localStorage.setItem('theme', currentTheme);
        console.log(`Theme applied: ${currentTheme}`);
    }

    function switchForm(targetForm) {
        // Clear any previous messages
        if (messageArea) messageArea.textContent = '';
        messageArea.style.color = 'var(--primary-color)'; // Reset color

        const currentlyActive = document.querySelector('.auth-form.active');
        const targetElement = (targetForm === 'register') ? registerForm : loginForm;

        if (!targetElement || (currentlyActive === targetElement)) return; // Do nothing if target invalid or already active

        if (currentlyActive) {
            currentlyActive.classList.remove('active');
        }

        // Reset register form state if switching to it
        if (targetForm === 'register') {
            if (termsCheckbox) termsCheckbox.checked = false;
            // Trigger change event to update button state
            if (termsCheckbox) termsCheckbox.dispatchEvent(new Event('change'));
        }

        targetElement.classList.add('active');
        console.log(`Switched to ${targetForm} form`);
    }

    function togglePasswordVisibility(icon) {
        const targetInputId = icon.dataset.target;
        const targetInput = document.getElementById(targetInputId);
        if (!targetInput) return;

        const isPassword = targetInput.type === 'password';
        targetInput.type = isPassword ? 'text' : 'password';
        // Add data attribute for CSS styling if needed (like adjusting padding)
        targetInput.dataset.isPassword = !isPassword;
        icon.classList.toggle('fa-eye', !isPassword);
        icon.classList.toggle('fa-eye-slash', isPassword);

        // Update aria-label after toggling
        updatePasswordToggleLabels();
    }

    function updatePasswordToggleLabels() {
        const langPack = translations[currentLang];
        passwordToggleIcons.forEach(icon => {
            const targetInputId = icon.dataset.target;
            const targetInput = document.getElementById(targetInputId);
            if (targetInput) {
                const isPasswordVisible = targetInput.type === 'text';
                icon.setAttribute('aria-label', isPasswordVisible ? langPack.hide_password_label : langPack.show_password_label);
            }
        });
    }

    function openModal() {
        if (termsModalOverlay) termsModalOverlay.classList.add('visible');
    }

    function closeModal() {
        if (termsModalOverlay) termsModalOverlay.classList.remove('visible');
    }

    // --- Event Listeners ---

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            currentTheme = currentTheme === 'light' ? 'dark' : 'light';
            applyTheme();
        });
    }

    if (langToggle) {
        langToggle.addEventListener('click', () => {
            currentLang = currentLang === 'en' ? 'ar' : 'en';
            applyTranslations();
        });
    }

    if (switchToRegisterLink) {
        switchToRegisterLink.addEventListener('click', (e) => {
            e.preventDefault(); switchForm('register');
        });
    }

    if (switchToLoginLink) {
        switchToLoginLink.addEventListener('click', (e) => {
            e.preventDefault(); switchForm('login');
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            // REMOVED: e.preventDefault(); // Allow form submission to Flask
            console.log('Login form submitting to backend...');
            // Backend will handle validation and messages via flash()
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            // Client-side checks before allowing submission
            const langPack = translations[currentLang];
            let errors = false;

            if (termsCheckbox && !termsCheckbox.checked) {
                 messageArea.textContent = langPack.terms_agree_required;
                 messageArea.style.color = 'red';
                 errors = true;
            }

            const passwordInput = document.getElementById('register-password');
            const confirmPasswordInput = document.getElementById('register-confirm-password');
            if (passwordInput && confirmPasswordInput && passwordInput.value !== confirmPasswordInput.value) {
                messageArea.textContent = langPack.passwords_no_match;
                messageArea.style.color = 'red';
                 errors = true;
            }

            if (errors) {
                 e.preventDefault(); // Prevent submission if client-side errors found
                 return;
            }

             // REMOVED: e.preventDefault(); // Allow form submission if checks pass
            console.log('Register form submitting to backend...');
             // Backend will handle validation and messages via flash()
        });
    }

    if (termsLinkRegister) termsLinkRegister.addEventListener('click', (e) => { e.preventDefault(); openModal(); });
    if (closeModalMain) closeModalMain.addEventListener('click', closeModal);
    if (closeModalSecondary) closeModalSecondary.addEventListener('click', closeModal);

    if (termsModalOverlay) {
        termsModalOverlay.addEventListener('click', (e) => {
            // Close if clicked outside the content area
            if (e.target === termsModalOverlay) closeModal();
        });
    }

    if (acceptTermsButton) {
        acceptTermsButton.addEventListener('click', () => {
            if (termsCheckbox) {
                termsCheckbox.checked = true;
                // Manually trigger change event to update button state
                termsCheckbox.dispatchEvent(new Event('change'));
            }
            closeModal();
        });
    }

    if (termsCheckbox && registerSubmitButton) {
        termsCheckbox.addEventListener('change', () => {
            registerSubmitButton.disabled = !termsCheckbox.checked;
            // Clear terms error message if checkbox is checked
            const langPack = translations[currentLang];
             if (termsCheckbox.checked && messageArea && messageArea.textContent === langPack.terms_agree_required) {
                messageArea.textContent = '';
                messageArea.style.color = 'var(--primary-color)'; // Reset color
             }
        });
    }

    passwordToggleIcons.forEach(icon => {
        icon.addEventListener('click', () => togglePasswordVisibility(icon));
        // Accessibility: Allow toggle with Enter/Space
        icon.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault(); togglePasswordVisibility(icon);
            }
        });
    });

    // Floating label interaction enhancement
    allInputGroups.forEach(group => {
        const input = group.querySelector('input');
        const label = group.querySelector('label');
        if (input && label) {
            // Check initial state (e.g., for filled values on error redirect)
            if (input.value) {
                label.style.top = '-10px';
                label.style.fontSize = '0.8em';
                label.style.color = 'var(--primary-color)';
            }
            input.addEventListener('focus', () => {
                 label.style.top = '-10px';
                 label.style.fontSize = '0.8em';
                 label.style.color = 'var(--primary-color)';
            });
            input.addEventListener('blur', () => {
                if (!input.value) {
                    label.style.top = '13px'; // Adjust based on your CSS
                    label.style.fontSize = '1em'; // Adjust based on your CSS
                    label.style.color = 'var(--text-muted-color)';
                }
            });
        }
    });


    // --- Initial Setup ---
    applyTheme();       // Apply theme on load
    applyTranslations(); // Apply language on load
    switchForm('login'); // Start with the login form active
    if (registerSubmitButton) registerSubmitButton.disabled = true; // Ensure register button is initially disabled

    console.log('Auth page initialized.');
});