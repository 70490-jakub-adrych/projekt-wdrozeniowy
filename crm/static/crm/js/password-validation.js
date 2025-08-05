/**
 * Dynamic Password Validation with Visual Feedback
 * Shows real-time password validation with green/red indicators
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all password fields that need validation
    const passwordFields = document.querySelectorAll('input[type="password"][name*="password1"], input[type="password"][name*="new_password1"]');
    
    passwordFields.forEach(function(passwordField) {
        setupPasswordValidation(passwordField);
    });
});

function setupPasswordValidation(passwordField) {
    // Create the validation requirements container
    const validationContainer = createValidationContainer();
    
    // Insert the validation container after the password field
    const helpText = passwordField.parentNode.querySelector('.form-text, .help-text');
    if (helpText) {
        // Replace existing help text with our dynamic validation
        helpText.style.display = 'none';
        helpText.parentNode.insertBefore(validationContainer, helpText.nextSibling);
    } else {
        // If no help text exists, add after the password field
        passwordField.parentNode.appendChild(validationContainer);
    }
    
    // Add event listeners for real-time validation
    passwordField.addEventListener('input', function() {
        validatePassword(passwordField.value, validationContainer);
    });
    
    passwordField.addEventListener('keyup', function() {
        validatePassword(passwordField.value, validationContainer);
    });
    
    // Check if there's a username field for similarity validation
    const usernameField = passwordField.form.querySelector('input[name="username"]');
    const emailField = passwordField.form.querySelector('input[name="email"]');
    const firstNameField = passwordField.form.querySelector('input[name="first_name"]');
    const lastNameField = passwordField.form.querySelector('input[name="last_name"]');
    
    if (usernameField) {
        usernameField.addEventListener('input', function() {
            validatePassword(passwordField.value, validationContainer, {
                username: usernameField.value,
                email: emailField ? emailField.value : '',
                first_name: firstNameField ? firstNameField.value : '',
                last_name: lastNameField ? lastNameField.value : ''
            });
        });
    }
    
    if (emailField) {
        emailField.addEventListener('input', function() {
            validatePassword(passwordField.value, validationContainer, {
                username: usernameField ? usernameField.value : '',
                email: emailField.value,
                first_name: firstNameField ? firstNameField.value : '',
                last_name: lastNameField ? lastNameField.value : ''
            });
        });
    }
    
    if (firstNameField) {
        firstNameField.addEventListener('input', function() {
            validatePassword(passwordField.value, validationContainer, {
                username: usernameField ? usernameField.value : '',
                email: emailField ? emailField.value : '',
                first_name: firstNameField.value,
                last_name: lastNameField ? lastNameField.value : ''
            });
        });
    }
    
    if (lastNameField) {
        lastNameField.addEventListener('input', function() {
            validatePassword(passwordField.value, validationContainer, {
                username: usernameField ? usernameField.value : '',
                email: emailField ? emailField.value : '',
                first_name: firstNameField ? firstNameField.value : '',
                last_name: lastNameField.value
            });
        });
    }
    
    // Initial validation
    validatePassword(passwordField.value, validationContainer);
}

function createValidationContainer() {
    const container = document.createElement('div');
    container.className = 'password-validation-container mt-3 mb-3';
    container.style.cssText = `
        margin-top: 0.75rem !important;
        margin-bottom: 0.75rem !important;
        padding: 0.75rem;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        background-color: #f8f9fa;
    `;
    
    container.innerHTML = `
        <div class="password-requirements">
            <h6 class="mb-2" style="color: #495057; font-size: 0.9rem; font-weight: 600;">
                <i class="fas fa-shield-alt me-1"></i> Wymagania dotyczące hasła:
            </h6>
            <div class="requirement-list">
                <div class="requirement-item" data-rule="similarity">
                    <i class="fas fa-times text-danger requirement-icon"></i>
                    <span class="requirement-text">Twoje hasło nie może być zbyt podobne do twoich innych danych osobistych</span>
                </div>
                <div class="requirement-item" data-rule="length">
                    <i class="fas fa-times text-danger requirement-icon"></i>
                    <span class="requirement-text">Twoje hasło musi zawierać co najmniej 8 znaków</span>
                </div>
                <div class="requirement-item" data-rule="common">
                    <i class="fas fa-times text-danger requirement-icon"></i>
                    <span class="requirement-text">Twoje hasło nie może być powszechnie używanym hasłem</span>
                </div>
                <div class="requirement-item" data-rule="numeric">
                    <i class="fas fa-times text-danger requirement-icon"></i>
                    <span class="requirement-text">Twoje hasło nie może składać się tylko z cyfr</span>
                </div>
            </div>
        </div>
    `;
    
    // Add styles for requirement items
    const style = document.createElement('style');
    style.textContent = `
        .requirement-item {
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
            padding: 0.25rem 0;
            transition: all 0.3s ease;
        }
        
        .requirement-item:last-child {
            margin-bottom: 0;
        }
        
        .requirement-icon {
            width: 16px;
            height: 16px;
            margin-right: 0.5rem;
            transition: all 0.3s ease;
            flex-shrink: 0;
        }
        
        .requirement-text {
            font-size: 0.85rem;
            line-height: 1.4;
            transition: color 0.3s ease;
        }
        
        .requirement-item.valid .requirement-icon {
            color: #28a745 !important;
        }
        
        .requirement-item.valid .requirement-text {
            color: #28a745;
            text-decoration: line-through;
            opacity: 0.8;
        }
        
        .requirement-item.invalid .requirement-icon {
            color: #dc3545 !important;
        }
        
        .requirement-item.invalid .requirement-text {
            color: #6c757d;
        }
        
        .password-validation-container {
            animation: fadeIn 0.3s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Mobile responsiveness */
        @media (max-width: 576px) {
            .password-validation-container {
                margin-top: 0.5rem !important;
                margin-bottom: 0.5rem !important;
                padding: 0.5rem;
            }
            
            .requirement-text {
                font-size: 0.8rem;
            }
            
            .requirement-icon {
                width: 14px;
                height: 14px;
            }
        }
    `;
    
    if (!document.querySelector('#password-validation-styles')) {
        style.id = 'password-validation-styles';
        document.head.appendChild(style);
    }
    
    return container;
}

function validatePassword(password, container, userData = {}) {
    const requirements = container.querySelectorAll('.requirement-item');
    
    requirements.forEach(function(requirement) {
        const rule = requirement.getAttribute('data-rule');
        const icon = requirement.querySelector('.requirement-icon');
        const isValid = checkPasswordRule(password, rule, userData);
        
        requirement.classList.remove('valid', 'invalid');
        requirement.classList.add(isValid ? 'valid' : 'invalid');
        
        icon.className = isValid 
            ? 'fas fa-check text-success requirement-icon'
            : 'fas fa-times text-danger requirement-icon';
    });
}

function checkPasswordRule(password, rule, userData = {}) {
    switch (rule) {
        case 'length':
            return password.length >= 8;
            
        case 'similarity':
            if (!password) return false;
            
            const userFields = [
                userData.username || '',
                userData.email || '',
                userData.first_name || '',
                userData.last_name || ''
            ];
            
            const passwordLowerSim = password.toLowerCase();
            
            return !userFields.some(function(field) {
                if (!field || field.length < 3) return false;
                const fieldLower = field.toLowerCase();
                
                // Check if password contains significant parts of user data
                if (passwordLowerSim.includes(fieldLower) || fieldLower.includes(passwordLowerSim)) {
                    return true;
                }
                
                // Check similarity ratio (simple implementation)
                const similarity = calculateSimilarity(passwordLowerSim, fieldLower);
                return similarity > 0.6;
            });
            
        case 'common':
            // Check against common passwords list
            const commonPasswords = [
                'password', 'hasło', '12345678', '123456789', 'qwerty', 'abc123',
                'password123', 'admin', 'letmein', 'welcome', 'monkey', 'dragon',
                '123123', 'password1', 'admin123', 'root', 'toor', 'pass',
                'test', 'guest', 'info', 'adm', 'admin1', 'password12',
                'pass123', '12345', '1234', '123456', '654321', 'superman',
                'qwerty123', 'football', 'baseball', 'welcome123'
            ];
            
            const passwordLowerCommon = password.toLowerCase();
            return !commonPasswords.some(function(common) {
                return passwordLowerCommon === common || passwordLowerCommon.includes(common);
            });
            
        case 'numeric':
            return !/^\d+$/.test(password);
            
        default:
            return false;
    }
}

function calculateSimilarity(str1, str2) {
    if (str1.length === 0 || str2.length === 0) return 0;
    
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) return 1.0;
    
    const editDistance = levenshteinDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
}

function levenshteinDistance(str1, str2) {
    const matrix = [];
    
    for (let i = 0; i <= str2.length; i++) {
        matrix[i] = [i];
    }
    
    for (let j = 0; j <= str1.length; j++) {
        matrix[0][j] = j;
    }
    
    for (let i = 1; i <= str2.length; i++) {
        for (let j = 1; j <= str1.length; j++) {
            if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                matrix[i][j] = matrix[i - 1][j - 1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1,
                    matrix[i][j - 1] + 1,
                    matrix[i - 1][j] + 1
                );
            }
        }
    }
    
    return matrix[str2.length][str1.length];
}
