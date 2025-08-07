// Book Recommender System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add loading animation to images
    const images = document.querySelectorAll('.book-image');
    images.forEach(img => {
        img.addEventListener('load', function() {
            this.style.opacity = '1';
        });
        
        img.addEventListener('error', function() {
            this.src = 'https://via.placeholder.com/300x400/6a4c93/ffffff?text=No+Image';
            this.style.opacity = '1';
        });
    });

    // Initialize search functionality if on recommend page
    if (document.getElementById('bookSearch')) {
        initializeSearch();
    }

    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe book cards for animation
    document.querySelectorAll('.book-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('bookSearch');
    const searchBtn = document.getElementById('searchBtn');
    const resultsContainer = document.getElementById('recommendationsResults');
    const suggestionsContainer = document.getElementById('suggestions');
    
    let currentSuggestionIndex = -1;
    let suggestions = [];
    let debounceTimer;

    // Search input event listeners
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const query = this.value.trim();
            if (query.length >= 2) {
                fetchSuggestions(query);
            } else {
                hideSuggestions();
            }
        }, 300);
    });

    // Keyboard navigation for suggestions
    searchInput.addEventListener('keydown', function(e) {
        const suggestionItems = suggestionsContainer.querySelectorAll('.autocomplete-suggestion');
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                currentSuggestionIndex = Math.min(currentSuggestionIndex + 1, suggestionItems.length - 1);
                updateSuggestionHighlight(suggestionItems);
                break;
            case 'ArrowUp':
                e.preventDefault();
                currentSuggestionIndex = Math.max(currentSuggestionIndex - 1, -1);
                updateSuggestionHighlight(suggestionItems);
                break;
            case 'Enter':
                e.preventDefault();
                if (currentSuggestionIndex >= 0 && suggestionItems[currentSuggestionIndex]) {
                    selectSuggestion(suggestionItems[currentSuggestionIndex].textContent);
                } else {
                    searchBooks();
                }
                break;
            case 'Escape':
                hideSuggestions();
                break;
        }
    });

    // Click outside to hide suggestions
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.autocomplete-container')) {
            hideSuggestions();
        }
    });

    // Search button click
    searchBtn.addEventListener('click', searchBooks);

    // Enter key to search
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && currentSuggestionIndex === -1) {
            searchBooks();
        }
    });

    async function fetchSuggestions(query) {
        try {
            const response = await fetch(`/search_books?q=${encodeURIComponent(query)}`);
            suggestions = await response.json();
            displaySuggestions(suggestions);
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }

    function displaySuggestions(suggestions) {
        if (suggestions.length === 0) {
            hideSuggestions();
            return;
        }

        const suggestionsHtml = suggestions.map(suggestion => 
            `<div class="autocomplete-suggestion" onclick="selectSuggestion('${suggestion}')">${suggestion}</div>`
        ).join('');

        suggestionsContainer.innerHTML = suggestionsHtml;
        suggestionsContainer.style.display = 'block';
        currentSuggestionIndex = -1;
    }

    function hideSuggestions() {
        suggestionsContainer.style.display = 'none';
        currentSuggestionIndex = -1;
    }

    function updateSuggestionHighlight(suggestionItems) {
        suggestionItems.forEach((item, index) => {
            item.classList.toggle('active', index === currentSuggestionIndex);
        });

        if (currentSuggestionIndex >= 0 && suggestionItems[currentSuggestionIndex]) {
            searchInput.value = suggestionItems[currentSuggestionIndex].textContent;
        }
    }

    window.selectSuggestion = function(suggestion) {
        searchInput.value = suggestion;
        hideSuggestions();
        searchBooks();
    };

    async function searchBooks() {
        const bookName = searchInput.value.trim();
        
        if (!bookName) {
            showAlert('Please enter a book name', 'error');
            return;
        }

        // Show loading
        showLoading();

        try {
            const response = await fetch('/get_recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ book_name: bookName })
            });

            const data = await response.json();
            hideLoading();

            if (data.error) {
                showAlert(data.error, 'error');
                if (data.suggestions) {
                    showSuggestions(data.suggestions);
                }
            } else {
                displayRecommendations(data.recommendations);
            }
        } catch (error) {
            hideLoading();
            showAlert('An error occurred while fetching recommendations', 'error');
            console.error('Error:', error);
        }
    }

    function showLoading() {
        resultsContainer.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Finding perfect book recommendations for you...</p>
            </div>
        `;
    }

    function hideLoading() {
        // Loading will be replaced by results or error message
    }

    function displayRecommendations(recommendations) {
        if (recommendations.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-custom alert-info">
                    <h4>No recommendations found</h4>
                    <p>Sorry, we couldn't find any recommendations for this book.</p>
                </div>
            `;
            return;
        }

        const recommendationsHtml = `
            <div class="row">
                <div class="col-12">
                    <h3 class="text-center mb-4" style="color: var(--light-purple);">
                        📚 Recommended Books for You
                    </h3>
                </div>
                ${recommendations.map(book => `
                    <div class="col-lg-4 col-md-6 col-sm-6 mb-4">
                        <div class="book-card h-100">
                            <img src="${book.image}" alt="${book.title}" class="book-image" loading="lazy">
                            <div class="book-details">
                                <h5 class="book-title">${book.title}</h5>
                                <p class="book-author">👤 ${book.author}</p>
                                <p class="book-year">📅 ${book.year}</p>
                                <div class="book-stats">
                                    <span class="rating">🔥 ${book.similarity}% Match</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        resultsContainer.innerHTML = recommendationsHtml;

        // Animate new cards
        const newCards = resultsContainer.querySelectorAll('.book-card');
        newCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            setTimeout(() => {
                card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function showAlert(message, type) {
        const alertClass = type === 'error' ? 'alert-error' : 'alert-info';
        const alertHtml = `
            <div class="alert alert-custom ${alertClass}" role="alert">
                <strong>${type === 'error' ? '❌ Error:' : 'ℹ️ Info:'}</strong> ${message}
            </div>
        `;
        
        resultsContainer.innerHTML = alertHtml;
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function showSuggestions(suggestionsList) {
        const suggestionsHtml = `
            <div class="alert alert-custom alert-info mt-3">
                <h5>💡 Try these books instead:</h5>
                <div class="row">
                    ${suggestionsList.slice(0, 6).map(book => `
                        <div class="col-md-4 col-sm-6 mb-2">
                            <button class="btn btn-outline-light btn-sm w-100" 
                                    onclick="selectSuggestion('${book}')" 
                                    style="border-color: var(--primary-purple); color: var(--light-purple);">
                                ${book}
                            </button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        resultsContainer.innerHTML += suggestionsHtml;
    }
}

// Utility functions
function animateOnScroll() {
    const elements = document.querySelectorAll('.book-card');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < window.innerHeight - elementVisible) {
            element.classList.add('animate');
        }
    });
}

// Smooth page transitions
function fadeInPage() {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease-in-out';
    
    window.addEventListener('load', function() {
        document.body.style.opacity = '1';
    });
}

// Initialize page fade
fadeInPage();

// Add scroll event listener
window.addEventListener('scroll', animateOnScroll);

// Preload critical images
function preloadImages() {
    const images = document.querySelectorAll('.book-image');
    images.forEach(img => {
        const imageUrl = img.getAttribute('src');
        if (imageUrl && imageUrl !== '#') {
            const preloadImg = new Image();
            preloadImg.src = imageUrl;
        }
    });
}

// Initialize preloading
setTimeout(preloadImages, 1000);
