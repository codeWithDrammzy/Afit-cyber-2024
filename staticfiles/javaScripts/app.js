// ================== UTILITY FUNCTIONS ==================

// CSRF Token Helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Share functionality
function shareItem(title, url) {
    if (navigator.share) {
        navigator.share({
            title: `Lost & Found: ${title}`,
            text: `Check if this found item belongs to you: ${title}`,
            url: url
        })
        .then(() => console.log('Successful share'))
        .catch((error) => console.log('Error sharing:', error));
    } else {
        // Fallback for browsers that don't support Web Share API
        navigator.clipboard.writeText(url).then(() => {
            alert('Link copied to clipboard!');
        });
    }
}

// ================== DASHBOARD FILTERING ==================

function initializeDashboardFilters() {
    const reportsContainer = document.getElementById('reportsContainer');
    const reportCards = document.querySelectorAll('.report-card');
    const searchInput = document.getElementById('searchInput');
    const clearSearch = document.getElementById('clearSearch');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const categoryChips = document.querySelectorAll('.category-chip');
    const noResults = document.getElementById('noResults');
    const clearFilters = document.getElementById('clearFilters');

    // If no reports container, this isn't a dashboard page
    if (!reportsContainer) return;

    let activeFilter = 'all';
    let activeCategory = 'all';
    let searchTerm = '';

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            searchTerm = this.value.toLowerCase().trim();
            if (clearSearch) {
                clearSearch.style.display = searchTerm ? 'block' : 'none';
            }
            filterReports();
        });
    }

    if (clearSearch) {
        clearSearch.addEventListener('click', function() {
            if (searchInput) {
                searchInput.value = '';
                searchTerm = '';
                this.style.display = 'none';
                filterReports();
            }
        });
    }

    // Filter button functionality
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active filter
            activeFilter = this.dataset.filter;
            
            // Update button styles
            filterButtons.forEach(btn => {
                btn.classList.remove('bg-blue-100', 'text-blue-700');
                btn.classList.add('bg-gray-100', 'text-gray-700');
            });
            this.classList.remove('bg-gray-100', 'text-gray-700');
            this.classList.add('bg-blue-100', 'text-blue-700');
            
            filterReports();
        });
    });

    // Category chip functionality
    categoryChips.forEach(chip => {
        chip.addEventListener('click', function() {
            activeCategory = this.dataset.category;
            
            // Update chip styles
            categoryChips.forEach(c => {
                c.classList.remove('bg-blue-100', 'text-blue-700');
                c.classList.add('bg-gray-100', 'text-gray-700');
            });
            this.classList.remove('bg-gray-100', 'text-gray-700');
            this.classList.add('bg-blue-100', 'text-blue-700');
            
            filterReports();
        });
    });

    // Clear all filters
    if (clearFilters) {
        clearFilters.addEventListener('click', function() {
            if (searchInput) {
                searchInput.value = '';
                searchTerm = '';
            }
            if (clearSearch) {
                clearSearch.style.display = 'none';
            }
            activeFilter = 'all';
            activeCategory = 'all';
            
            // Reset button styles
            filterButtons.forEach(btn => {
                btn.classList.remove('bg-blue-100', 'text-blue-700');
                btn.classList.add('bg-gray-100', 'text-gray-700');
            });
            const allFilterBtn = document.querySelector('.filter-btn[data-filter="all"]');
            if (allFilterBtn) {
                allFilterBtn.classList.add('bg-blue-100', 'text-blue-700');
            }
            
            categoryChips.forEach(c => {
                c.classList.remove('bg-blue-100', 'text-blue-700');
                c.classList.add('bg-gray-100', 'text-gray-700');
            });
            
            filterReports();
        });
    }

    // Filter reports function
    function filterReports() {
        let visibleCount = 0;
        
        reportCards.forEach(card => {
            const type = card.dataset.type;
            const category = card.dataset.category;
            const searchData = card.dataset.search || '';
            
            // Check filters
            const typeMatch = activeFilter === 'all' || type === activeFilter;
            const categoryMatch = activeCategory === 'all' || category === activeCategory;
            const searchMatch = searchTerm === '' || searchData.includes(searchTerm);
            
            // Show/hide based on all conditions
            if (typeMatch && categoryMatch && searchMatch) {
                card.style.display = 'block';
                visibleCount++;
                
                // Add animation
                card.style.opacity = '0';
                card.style.transform = 'translateY(10px)';
                setTimeout(() => {
                    card.style.transition = 'opacity 0.3s, transform 0.3s';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 50);
            } else {
                card.style.display = 'none';
            }
        });
        
        // Show/hide no results message
        if (visibleCount === 0 && reportsContainer) {
            reportsContainer.style.display = 'none';
            if (noResults) {
                noResults.style.display = 'block';
            }
        } else {
            reportsContainer.style.display = 'grid';
            if (noResults) {
                noResults.style.display = 'none';
            }
        }
    }

    // Hover effect for cards
    reportCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', function() {
            if (!this.style.display || this.style.display === 'none') return;
            this.style.transform = 'translateY(0)';
        });
    });

    // Initialize with all visible
    filterReports();
}

// ================== REPORT ITEM FORM ==================

function initializeReportForm() {
    const lostCard = document.getElementById('lost-card');
    const foundCard = document.getElementById('found-card');
    const formContainer = document.getElementById('report-form-container');
    const statusField = document.getElementById('status-field');
    const formTitle = document.getElementById('form-title');
    const formSubtitle = document.getElementById('form-subtitle');
    const statusIndicator = document.getElementById('status-indicator');
    const changeStatusBtn = document.getElementById('change-status-btn');
    const cancelFormBtn = document.getElementById('cancel-form-btn');
    const locationFoundSection = document.getElementById('location-found-section');
    const locationLostSection = document.getElementById('location-lost-section');
    const locationFoundInput = document.getElementById('id_location_found');
    const locationLostInput = document.getElementById('id_location_lost');
    const reportForm = document.getElementById('report-form');
    
    // If no report form container, this isn't the report page
    if (!formContainer) return;
    
    // Check if form has errors (form is already visible)
    const hasFormErrors = document.querySelector('.bg-red-50') !== null;
    
    if (hasFormErrors) {
        // If form has errors, show the form immediately
        formContainer.classList.remove('hidden');
        
        // Set initial state based on form value
        const initialStatus = document.querySelector('input[name="status"]');
        if (initialStatus && initialStatus.value === 'found') {
            setStatus('found');
        } else {
            setStatus('lost');
        }
    } else {
        // Default to showing selection cards
        formContainer.classList.add('hidden');
    }
    
    // Set status function
    function setStatus(status) {
        // Update hidden field
        if (statusField) {
            statusField.value = status;
        }
        
        // Update UI based on status
        if (status === 'lost') {
            // Update cards
            if (lostCard) lostCard.classList.add('border-red-500', 'bg-red-50');
            if (foundCard) foundCard.classList.remove('border-green-500', 'bg-green-50');
            
            // Update form title
            if (formTitle) {
                formTitle.innerHTML = 'Report <span id="selected-status">Lost</span> Item';
            }
            if (formSubtitle) {
                formSubtitle.textContent = 'Please provide details about your missing item';
            }
            
            // Update status indicator
            if (statusIndicator) {
                statusIndicator.innerHTML = '<i class="fas fa-exclamation-triangle mr-2"></i><span class="font-medium">Reporting a Lost Item</span>';
                statusIndicator.className = 'inline-flex items-center px-4 py-2 rounded-full mb-6 bg-red-100 text-red-700';
            }
            
            // Update location fields
            if (locationFoundSection) {
                locationFoundSection.style.display = 'none';
            }
            if (locationLostSection) {
                locationLostSection.style.display = 'block';
            }
            if (locationFoundInput) {
                locationFoundInput.required = false;
            }
            if (locationLostInput) {
                locationLostInput.required = true;
            }
            
        } else if (status === 'found') {
            // Update cards
            if (lostCard) lostCard.classList.remove('border-red-500', 'bg-red-50');
            if (foundCard) foundCard.classList.add('border-green-500', 'bg-green-50');
            
            // Update form title
            if (formTitle) {
                formTitle.innerHTML = 'Report <span id="selected-status">Found</span> Item';
            }
            if (formSubtitle) {
                formSubtitle.textContent = 'Please provide details about the found item';
            }
            
            // Update status indicator
            if (statusIndicator) {
                statusIndicator.innerHTML = '<i class="fas fa-hand-holding-heart mr-2"></i><span class="font-medium">Reporting a Found Item</span>';
                statusIndicator.className = 'inline-flex items-center px-4 py-2 rounded-full mb-6 bg-green-100 text-green-700';
            }
            
            // Update location fields
            if (locationFoundSection) {
                locationFoundSection.style.display = 'block';
            }
            if (locationLostSection) {
                locationLostSection.style.display = 'none';
            }
            if (locationFoundInput) {
                locationFoundInput.required = true;
            }
            if (locationLostInput) {
                locationLostInput.required = false;
            }
        }
    }
    
    // Event Listeners
    if (lostCard) {
        lostCard.addEventListener('click', function() {
            setStatus('lost');
            formContainer.classList.remove('hidden');
            // Scroll to form
            formContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    }
    
    if (foundCard) {
        foundCard.addEventListener('click', function() {
            setStatus('found');
            formContainer.classList.remove('hidden');
            // Scroll to form
            formContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    }
    
    if (changeStatusBtn) {
        changeStatusBtn.addEventListener('click', function() {
            // Hide form and show selection cards
            formContainer.classList.add('hidden');
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
    
    if (cancelFormBtn) {
        cancelFormBtn.addEventListener('click', function() {
            // Hide form and show selection cards
            formContainer.classList.add('hidden');
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
    
    // Initialize category selection
    const categoryRadios = document.querySelectorAll('input[name="category"]');
    categoryRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            // Remove all checked styles first
            document.querySelectorAll('label[for^="id_category_"]').forEach(label => {
                label.classList.remove('border-blue-500', 'bg-blue-50');
            });
            
            // Add style to selected
            if (this.checked) {
                const label = document.querySelector(`label[for="${this.id}"]`);
                if (label) {
                    label.classList.add('border-blue-500', 'bg-blue-50');
                }
            }
        });
        
        // Set initial state for categories
        if (radio.checked) {
            const label = document.querySelector(`label[for="${radio.id}"]`);
            if (label) {
                label.classList.add('border-blue-500', 'bg-blue-50');
            }
        }
    });
    
    // Set default date to now if empty
    const dateInput = document.getElementById('id_date_occurred');
    if (dateInput && !dateInput.value) {
        const now = new Date();
        // Format for datetime-local input
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        
        dateInput.value = `${year}-${month}-${day}T${hours}:${minutes}`;
    }
    
    // Form validation before submit
    if (reportForm) {
        reportForm.addEventListener('submit', function(e) {
            console.log('Form submitted - Status:', statusField ? statusField.value : 'unknown');
        });
    }
}

// Image preview functionality for report form
function previewImage(event) {
    const input = event.target;
    const fileName = input.files[0] ? input.files[0].name : 'No file chosen';
    const fileNameElement = document.getElementById('file-name');
    if (fileNameElement) {
        fileNameElement.textContent = fileName;
    }
    
    const preview = document.getElementById('preview');
    const previewContainer = document.getElementById('image-preview');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            if (preview) {
                preview.src = e.target.result;
            }
            if (previewContainer) {
                previewContainer.classList.remove('hidden');
            }
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

function removeImage() {
    const input = document.getElementById('id_image');
    const previewContainer = document.getElementById('image-preview');
    const fileNameElement = document.getElementById('file-name');
    
    if (input) {
        input.value = '';
    }
    if (previewContainer) {
        previewContainer.classList.add('hidden');
    }
    if (fileNameElement) {
        fileNameElement.textContent = 'No file chosen';
    }
}

// ================== FOUND ITEMS PAGE ==================

function initializeFoundItemsPage() {
    // Search functionality with debounce
    let searchTimer;
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            }, 500);
        });
    }
    
    // Filter chips highlight on click
    const filterChips = document.querySelectorAll('a.bg-gray-100');
    filterChips.forEach(chip => {
        chip.addEventListener('click', function(e) {
            // Remove active state from all chips
            filterChips.forEach(c => {
                c.classList.remove('bg-green-100', 'text-green-700');
                c.classList.add('bg-gray-100', 'text-gray-700');
            });
            
            // Add active state to clicked chip
            this.classList.remove('bg-gray-100', 'text-gray-700');
            this.classList.add('bg-green-100', 'text-green-700');
        });
    });
}

// ================== ITEM DETAIL PAGE ==================

function initializeItemDetailPage() {
    // Form validation
    const claimForm = document.getElementById('claim-form');
    if (claimForm) {
        claimForm.addEventListener('submit', function(e) {
            const description = document.getElementById('id_description');
            const proof = document.getElementById('id_proof');
            
            if (description && proof) {
                const descriptionValue = description.value.trim();
                const proofValue = proof.value.trim();
                
                if (!descriptionValue || !proofValue) {
                    e.preventDefault();
                    alert('Please fill in all required fields.');
                }
            }
        });
    }
}

// ================== MARK AS FOUND FUNCTIONALITY ==================

// Mark as found functionality
function markAsFound(itemId, itemTitle, defaultLocation) {
    // Simple prompt version
    const foundLocation = prompt(`Where did you find "${itemTitle}"?`, defaultLocation);
    
    if (foundLocation === null) {
        // User cancelled
        return;
    }
    
    if (!foundLocation.trim()) {
        alert('Please enter where you found the item.');
        return;
    }
    
    // Ask if user wants to claim it
    const claimIt = confirm('Do you want to claim this item for yourself? (Click OK to claim, Cancel to just mark as found)');
    
    // Find the form
    const foundLocationInput = document.getElementById(`found-location-${itemId}`);
    const claimItemInput = document.getElementById(`claim-item-${itemId}`);
    const form = document.getElementById(`found-form-${itemId}`);
    
    if (foundLocationInput && claimItemInput && form) {
        foundLocationInput.value = foundLocation;
        claimItemInput.value = claimIt ? 'true' : 'false';
        form.submit();
    } else {
        // Fallback AJAX method
        fetch(`/item/${itemId}/mark-found/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `found_location=${encodeURIComponent(foundLocation)}&claim_item=${claimIt}`
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Error marking item as found');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Network error. Please try again.');
        });
    }
}

// ================== MAIN INITIALIZATION ==================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard filters (std-board.html, my-report.html)
    initializeDashboardFilters();
    
    // Initialize report form (report-item.html)
    initializeReportForm();
    
    // Initialize found items page (found-item.html)
    initializeFoundItemsPage();
    
    // Initialize item detail page (item-detail.html)
    initializeItemDetailPage();
    
    // Initialize any other page-specific functionality
    // Add more initialization functions as needed
});

// ================== GLOBAL EXPORTS (Optional) ==================
// If you need to call these functions from HTML onclick attributes

// Make functions available globally
window.previewImage = previewImage;
window.removeImage = removeImage;
window.shareItem = shareItem;
window.markAsFound = markAsFound;