// Global variables
let familyMemberCount = 0;
let statesData = [];
let designationsData = [];

// DOM Content Loaded Event
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...'); // Debug log
    initializeApp();
    
    // Alternative event listener for add family member button
    const addFamilyBtn = document.querySelector('.add-btn');
    if (addFamilyBtn) {
        addFamilyBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Add family member button clicked'); // Debug log
            addFamilyMember();
        });
    } else {
        console.error('Add family member button not found'); // Debug log
    }
});

// Initialize Application
function initializeApp() {
    loadMasterData();
    setupEventListeners();
    setupFormValidation();
}

// Load Master Data from API
async function loadMasterData() {
    try {
        // Load States
        const statesResponse = await fetch('/api/states');
        statesData = await statesResponse.json();
        populateStatesDropdowns();

        // Load Designations
        const designationsResponse = await fetch('/api/designations');
        designationsData = await designationsResponse.json();
        populateDesignationsDropdown();

    } catch (error) {
        console.error('Error loading master data:', error);
        showNotification('Error loading form data. Please refresh the page.', 'error');
    }
}

// Populate States Dropdowns
function populateStatesDropdowns() {
    const stateDropdowns = ['dob_state', 'present_state', 'permanent_state'];
    
    stateDropdowns.forEach(dropdownId => {
        const dropdown = document.getElementById(dropdownId);
        if (dropdown) {
            // Clear existing options except the first one
            dropdown.innerHTML = '<option value="">Select State</option>';
            
            // Add states
            statesData.forEach(state => {
                const option = document.createElement('option');
                option.value = state.id;
                option.textContent = state.name;
                dropdown.appendChild(option);
            });
        }
    });
}

// Populate Designations Dropdown
function populateDesignationsDropdown() {
    const dropdown = document.getElementById('designation');
    if (dropdown) {
        dropdown.innerHTML = '<option value="">Select Designation</option>';
        
        designationsData.forEach(designation => {
            const option = document.createElement('option');
            option.value = designation.id;
            option.textContent = `${designation.name} (${designation.department})`;
            dropdown.appendChild(option);
        });
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // State change listeners for district population
    document.getElementById('dob_state')?.addEventListener('change', function() {
        loadDistricts(this.value, 'dob_district');
    });

    document.getElementById('present_state')?.addEventListener('change', function() {
        loadDistricts(this.value, 'present_district');
    });

    document.getElementById('permanent_state')?.addEventListener('change', function() {
        loadDistricts(this.value, 'permanent_district');
    });

    // Form submission
    document.getElementById('employeeForm')?.addEventListener('submit', handleFormSubmission);

    // File input change listeners
    setupFileInputListeners();

    // Form reset
    document.querySelector('.reset-btn')?.addEventListener('click', function(e) {
        if (confirm('Are you sure you want to reset the form? All data will be lost.')) {
            resetForm();
        } else {
            e.preventDefault();
        }
    });
}

// Load Districts based on State
async function loadDistricts(stateId, districtDropdownId) {
    const districtDropdown = document.getElementById(districtDropdownId);
    
    if (!districtDropdown || !stateId) {
        if (districtDropdown) {
            districtDropdown.innerHTML = '<option value="">Select District</option>';
        }
        return;
    }

    try {
        const response = await fetch(`/api/districts/${stateId}`);
        const districts = await response.json();
        
        districtDropdown.innerHTML = '<option value="">Select District</option>';
        
        districts.forEach(district => {
            const option = document.createElement('option');
            option.value = district.id;
            option.textContent = district.name;
            districtDropdown.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error loading districts:', error);
        showNotification('Error loading districts', 'error');
    }
}

// Add Family Member
function addFamilyMember() {
    familyMemberCount++;
    const container = document.getElementById('family-members-container');
    
    const familyMemberHtml = `
        <div class="family-member-card" id="family-member-${familyMemberCount}">
            <div class="family-member-header">
                <div class="family-member-title">
                    <i class="fas fa-user"></i>
                    Family Member ${familyMemberCount}
                </div>
                <button type="button" class="remove-family-btn" onclick="removeFamilyMember(${familyMemberCount})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="form-grid">
                <div class="form-group">
                    <label for="family_name_${familyMemberCount}">Name</label>
                    <input type="text" id="family_name_${familyMemberCount}" name="family_name_${familyMemberCount}" class="form-control family-name">
                </div>
                <div class="form-group">
                    <label for="family_relationship_${familyMemberCount}">Relationship</label>
                    <select id="family_relationship_${familyMemberCount}" name="family_relationship_${familyMemberCount}" class="form-control family-relationship">
                        <option value="">Select Relationship</option>
                        <option value="Father">Father</option>
                        <option value="Mother">Mother</option>
                        <option value="Spouse">Spouse</option>
                        <option value="Son">Son</option>
                        <option value="Daughter">Daughter</option>
                        <option value="Brother">Brother</option>
                        <option value="Sister">Sister</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="family_aadhar_${familyMemberCount}">Aadhar Number</label>
                    <input type="text" id="family_aadhar_${familyMemberCount}" name="family_aadhar_${familyMemberCount}" class="form-control family-aadhar" pattern="[0-9]{12}" maxlength="12">
                </div>
                <div class="form-group">
                    <label for="family_mobile_${familyMemberCount}">Mobile Number</label>
                    <input type="tel" id="family_mobile_${familyMemberCount}" name="family_mobile_${familyMemberCount}" class="form-control family-mobile" pattern="[0-9]{10}" maxlength="10">
                </div>
                <div class="form-group">
                    <label for="family_dob_${familyMemberCount}">Date of Birth</label>
                    <input type="date" id="family_dob_${familyMemberCount}" name="family_dob_${familyMemberCount}" class="form-control family-dob">
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', familyMemberHtml);
    
    // Add animation
    const newCard = document.getElementById(`family-member-${familyMemberCount}`);
    if (newCard) {
        newCard.style.opacity = '0';
        newCard.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            newCard.style.transition = 'all 0.3s ease';
            newCard.style.opacity = '1';
            newCard.style.transform = 'translateY(0)';
        }, 10);
    }
    
    console.log(`Added family member ${familyMemberCount}`); // Debug log
}

// Make functions globally available
window.addFamilyMember = addFamilyMember;
window.removeFamilyMember = removeFamilyMember;
window.copyPresentToPermanent = copyPresentToPermanent;

// Remove Family Member
function removeFamilyMember(id) {
    const card = document.getElementById(`family-member-${id}`);
    if (card) {
        card.style.transition = 'all 0.3s ease';
        card.style.opacity = '0';
        card.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            card.remove();
        }, 300);
    }
}

// Copy Present Address to Permanent Address
function copyPresentToPermanent() {
    const presentFields = {
        'present_address': 'permanent_address',
        'present_state': 'permanent_state',
        'present_district': 'permanent_district',
        'present_pincode': 'permanent_pincode'
    };
    
    Object.keys(presentFields).forEach(presentField => {
        const presentElement = document.getElementById(presentField);
        const permanentElement = document.getElementById(presentFields[presentField]);
        
        if (presentElement && permanentElement && presentElement.value) {
            permanentElement.value = presentElement.value;
            
            // Trigger change event for dropdowns
            if (presentElement.tagName === 'SELECT') {
                permanentElement.dispatchEvent(new Event('change'));
            }
        }
    });
    
    showNotification('Address copied successfully!', 'success');
}

// Setup File Input Listeners
function setupFileInputListeners() {
    const fileInputs = document.querySelectorAll('.file-input');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateFileUpload(this);
        });
    });
}

// Validate File Upload
function validateFileUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    const maxSizes = {
        'photo': 2 * 1024 * 1024, // 2MB
        'signature': 1 * 1024 * 1024, // 1MB
        'certificate': 5 * 1024 * 1024, // 5MB
        'default': 2 * 1024 * 1024 // 2MB
    };
    
    const maxSize = maxSizes[input.name] || maxSizes.default;
    
    if (file.size > maxSize) {
        showNotification(`File size too large. Maximum allowed: ${Math.round(maxSize / (1024 * 1024))}MB`, 'error');
        input.value = '';
        return false;
    }
    
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Invalid file type. Allowed: JPG, PNG, GIF, PDF', 'error');
        input.value = '';
        return false;
    }
    
    return true;
}

// Setup Form Validation
function setupFormValidation() {
    const form = document.getElementById('employeeForm');
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
}

// Validate Individual Field
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    
    // Pattern validation
    if (value && field.hasAttribute('pattern')) {
        const pattern = new RegExp(field.getAttribute('pattern'));
        if (!pattern.test(value)) {
            isValid = false;
            errorMessage = getPatternErrorMessage(field);
        }
    }
    
    // Specific field validations
    switch (field.type) {
        case 'email':
            if (value && !isValidEmail(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid email address';
            }
            break;
        case 'tel':
            if (value && !isValidPhone(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid phone number';
            }
            break;
        case 'date':
            if (value && !isValidDate(field, value)) {
                isValid = false;
                errorMessage = 'Please enter a valid date';
            }
            break;
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

// Get Pattern Error Message
function getPatternErrorMessage(field) {
    const fieldName = field.name;
    
    const patterns = {
        'mobile_no': 'Mobile number should be 10 digits',
        'home_mobile_no': 'Mobile number should be 10 digits',
        'permanent_mobile_no': 'Mobile number should be 10 digits',
        'pan_no': 'PAN should be in format: ABCDE1234F',
        'ifsc_code': 'IFSC code should be in format: ABCD0123456',
        'present_pincode': 'Pincode should be 6 digits',
        'permanent_pincode': 'Pincode should be 6 digits'
    };
    
    return patterns[fieldName] || 'Please enter a valid format';
}

// Show Field Error
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('error');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

// Clear Field Error
function clearFieldError(field) {
    field.classList.remove('error');
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

// Validation Helper Functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[0-9]{10}$/;
    return phoneRegex.test(phone);
}

function isValidDate(field, value) {
    const date = new Date(value);
    const today = new Date();
    
    if (isNaN(date.getTime())) {
        return false;
    }
    
    // DOB should not be in future
    if (field.name === 'dob' && date > today) {
        return false;
    }
    
    // DOB should not be more than 100 years ago
    if (field.name === 'dob') {
        const hundredYearsAgo = new Date();
        hundredYearsAgo.setFullYear(hundredYearsAgo.getFullYear() - 100);
        if (date < hundredYearsAgo) {
            return false;
        }
    }
    
    return true;
}

// Handle Form Submission
function handleFormSubmission(e) {
    e.preventDefault();
    
    if (!validateForm()) {
        showNotification('Please correct the errors before submitting', 'error');
        return;
    }
    
    // Collect family data
    const familyData = collectFamilyData();
    
    // Add family data to form
    const familyInput = document.createElement('input');
    familyInput.type = 'hidden';
    familyInput.name = 'family_details';
    familyInput.value = JSON.stringify(familyData);
    e.target.appendChild(familyInput);
    
    // Show loading overlay
    showLoadingOverlay();
    
    // Submit form
    e.target.submit();
}

// Validate Entire Form
function validateForm() {
    const form = document.getElementById('employeeForm');
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

// Collect Family Data
function collectFamilyData() {
    const familyData = [];
    const familyCards = document.querySelectorAll('.family-member-card');
    
    familyCards.forEach(card => {
        const cardId = card.id.split('-')[2];
        const familyMember = {
            name: document.getElementById(`family_name_${cardId}`)?.value || '',
            relationship: document.getElementById(`family_relationship_${cardId}`)?.value || '',
            aadhar_no: document.getElementById(`family_aadhar_${cardId}`)?.value || '',
            mobile_no: document.getElementById(`family_mobile_${cardId}`)?.value || '',
            dob: document.getElementById(`family_dob_${cardId}`)?.value || ''
        };
        
        if (familyMember.name.trim()) {
            familyData.push(familyMember);
        }
    });
    
    return familyData;
}

// Show Loading Overlay
function showLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('show');
    }
}

// Hide Loading Overlay
function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('show');
    }
}

// Show Notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
        ${message}
        <span class="close-btn" onclick="this.parentElement.remove()">&times;</span>
    `;
    
    const container = document.querySelector('.container');
    const firstSection = container.querySelector('.form-section');
    
    if (firstSection) {
        container.insertBefore(notification, firstSection);
    } else {
        container.appendChild(notification);
    }
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Reset Form
function resetForm() {
    const form = document.getElementById('employeeForm');
    form.reset();
    
    // Clear family members
    const familyContainer = document.getElementById('family-members-container');
    familyContainer.innerHTML = '';
    familyMemberCount = 0;
    
    // Clear all errors
    document.querySelectorAll('.field-error').forEach(error => error.remove());
    document.querySelectorAll('.error').forEach(field => field.classList.remove('error'));
    
    // Reset dropdowns
    populateStatesDropdowns();
    
    showNotification('Form has been reset', 'success');
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Auto-save functionality (optional)
function setupAutoSave() {
    const form = document.getElementById('employeeForm');
    const inputs = form.querySelectorAll('input, select, textarea');
    
    const saveData = debounce(() => {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        localStorage.setItem('employeeFormData', JSON.stringify(data));
    }, 2000);
    
    inputs.forEach(input => {
        input.addEventListener('input', saveData);
    });
}

// Load saved data (optional)
function loadSavedData() {
    const savedData = localStorage.getItem('employeeFormData');
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const field = document.getElementById(key);
                if (field) {
                    field.value = data[key];
                }
            });
        } catch (error) {
            console.error('Error loading saved data:', error);
        }
    }
}

// Clear saved data
function clearSavedData() {
    localStorage.removeItem('employeeFormData');
}

// Add CSS for field errors
const style = document.createElement('style');
style.textContent = `
    .form-control.error {
        border-color: #ef4444 !important;
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
    }
    
    .field-error {
        color: #ef4444;
        font-size: 0.875rem;
        margin-top: 5px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .field-error::before {
        content: "⚠";
        font-size: 0.8rem;
    }
`;
document.head.appendChild(style);