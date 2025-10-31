/**
 * Phone number masking for Polish phone numbers
 * Supports formats: xx xxx xx xx and +48 xx xxx xx xx
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all phone input fields
    const phoneInputs = document.querySelectorAll('input[name="phone"], input.phone-mask');
    
    phoneInputs.forEach(function(phoneInput) {
        // Set placeholder
        phoneInput.setAttribute('placeholder', '12 345 67 89 lub +48 12 345 67 89');
        
        // Apply mask on input
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value;
            let cursorPosition = e.target.selectionStart;
            
            // Count spaces before cursor for position adjustment
            let spacesBefore = (value.substring(0, cursorPosition).match(/ /g) || []).length;
            
            // Remove all non-digits except + at the beginning
            let digitsOnly = value.replace(/[^\d+]/g, '');
            
            // Ensure + is only at the beginning
            if (digitsOnly.indexOf('+') > 0) {
                digitsOnly = digitsOnly.replace(/\+/g, '');
            }
            
            let formatted = '';
            
            // Check if it's international format starting with +48
            if (digitsOnly.startsWith('+48')) {
                // Remove the +48 prefix for processing
                let numbers = digitsOnly.substring(3);
                formatted = '+48';
                
                // Format: +48 xx xxx xx xx
                if (numbers.length > 0) formatted += ' ' + numbers.substring(0, 2);
                if (numbers.length > 2) formatted += ' ' + numbers.substring(2, 5);
                if (numbers.length > 5) formatted += ' ' + numbers.substring(5, 7);
                if (numbers.length > 7) formatted += ' ' + numbers.substring(7, 9);
            } 
            // Check if user is typing + (international format)
            else if (digitsOnly.startsWith('+')) {
                formatted = digitsOnly; // Keep the + while user is typing
            }
            // Check if it starts with 48 (without +)
            else if (digitsOnly.startsWith('48') && digitsOnly.length > 2) {
                // Auto-add + for convenience
                let numbers = digitsOnly.substring(2);
                formatted = '+48';
                
                // Format: +48 xx xxx xx xx
                if (numbers.length > 0) formatted += ' ' + numbers.substring(0, 2);
                if (numbers.length > 2) formatted += ' ' + numbers.substring(2, 5);
                if (numbers.length > 5) formatted += ' ' + numbers.substring(5, 7);
                if (numbers.length > 7) formatted += ' ' + numbers.substring(7, 9);
            }
            // Local format: xx xxx xx xx
            else if (digitsOnly.length > 0) {
                if (digitsOnly.length > 0) formatted += digitsOnly.substring(0, 2);
                if (digitsOnly.length > 2) formatted += ' ' + digitsOnly.substring(2, 5);
                if (digitsOnly.length > 5) formatted += ' ' + digitsOnly.substring(5, 7);
                if (digitsOnly.length > 7) formatted += ' ' + digitsOnly.substring(7, 9);
            }
            
            // Update value
            e.target.value = formatted;
            
            // Restore cursor position
            let spacesAfter = (formatted.substring(0, cursorPosition).match(/ /g) || []).length;
            let newPosition = cursorPosition + (spacesAfter - spacesBefore);
            
            // Make sure cursor is in valid position
            if (newPosition > formatted.length) {
                newPosition = formatted.length;
            }
            
            e.target.setSelectionRange(newPosition, newPosition);
        });
        
        // Handle paste event
        phoneInput.addEventListener('paste', function(e) {
            setTimeout(function() {
                phoneInput.dispatchEvent(new Event('input'));
            }, 10);
        });
    });
});
