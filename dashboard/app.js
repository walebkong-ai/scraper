// KW AI News Dashboard - Main Application Logic
// Follows B.L.A.S.T. protocol and gemini.md schemas

// State Management
const state = {
    articles: [],
    savedArticles: JSON.parse(localStorage.getItem('savedArticles') || '[]'),
    currentFilter: 'all',
    searchQuery: '',
    sortOrder: 'desc' // desc = newest first
};

// DOM Elements
const elements = {
    articlesGrid: document.getElementById('articlesGrid'),
    loadingState: document.getElementById('loadingState'),
    emptyState: document.getElementById('emptyState'),
    searchInput: document.getElementById('searchInput'),
    refreshBtn: document.getElementById('refreshBtn'),
    sortBtn: document.getElementById('sortBtn'),
    clearFiltersBtn: document.getElementById('clearFiltersBtn'),
    filterPills: document.querySelectorAll('.filter-pill'),
    sectionTitle: document.getElementById('sectionTitle'),
    totalArticles: document.getElementById('totalArticles'),
    savedCount: document.getElementById('savedCount'),
    sourcesCount: document.getElementById('sourcesCount'), // Added sourcesCount
    lastUpdate: document.getElementById('lastUpdate')
};

// Initialize App
async function init() {
    console.log('🚀 Initializing KW AI News Dashboard...');

    // Load saved articles from localStorage
    updateSavedCount();

    // Attach event listeners
    attachEventListeners();

    // Load articles
    await loadArticles();
}

// Event Listeners
function attachEventListeners() {
    // Search
    elements.searchInput.addEventListener('input', debounce(handleSearch, 300));

    // Refresh
    elements.refreshBtn.addEventListener('click', handleRefresh);

    // Sort
    elements.sortBtn.addEventListener('click', handleSort);

    // Clear filters
    elements.clearFiltersBtn.addEventListener('click', handleClearFilters);

    // Filter pills
    elements.filterPills.forEach(pill => {
        pill.addEventListener('click', () => handleFilterChange(pill.dataset.filter));
    });
}

// Load Articles from Scrapers
async function loadArticles() {
    showLoading();

    try {
        // In production, this would call the scrapers
        // For now, we'll simulate with mock data
        const articles = await fetchArticles();

        state.articles = articles;
        updateStats();
        renderArticles();
    } catch (error) {
        console.error('Error loading articles:', error);
        showEmpty();
    }
}

// Fetch Articles (calls Python scrapers)
async function fetchArticles() {
    // TODO: In production, this would call the Python scrapers
    // For now, return mock data for demonstration

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock data for demonstration
    const mockArticles = [
        {
            id: '1',
            source: 'bens_bites',
            title: 'Something big is happening',
            summary: 'Not just $60m seed rounds... The latest from Ben\'s Bites on the shifting AI landscape.',
            url: 'https://bensbites.substack.com/p/something-big-is-happening',
            published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            author: 'Ben Tossell',
            is_saved: false
        },
        {
            id: '2',
            source: 'ai_rundown',
            title: 'The Rundown: Google\'s upgrade breaks reasoning barriers',
            summary: 'Google\'s upgraded Deep Think AI shatters reasoning benchmarks, demonstrating unprecedented problem-solving capabilities.',
            url: 'https://www.therundown.ai/p/googles-upgrade-breaks-reasoning-barriers',
            published_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
            author: 'Rowan Cheung',
            is_saved: false
        },
        {
            id: '3',
            source: 'cointelegraph',
            title: 'Strategy Plans to Equitize Convertible Debt Over Next 3-6 Years: Saylor',
            summary: 'MicroStrategy continues its Bitcoin accumulation strategy while managing debt obligations...',
            url: 'https://cointelegraph.com/news/strategy-plans-equitize-convertible-debt-over-next-3-6-years-saylor',
            published_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
            author: 'CoinTelegraph',
            is_saved: false
        },
        {
            id: '4',
            source: 'decrypt',
            title: 'Bitcoin Leverage Heats Up as Traders Bet on Price Rebound',
            summary: 'Bitcoin\'s futures basis has widened amid retail dip buying surges, but experts warn of potential shakeout...',
            url: 'https://decrypt.co/358134/bitcoin-leverage-heats-up-as-traders-bet-on-price-rebound',
            published_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
            author: 'Decrypt',
            is_saved: false
        },
        {
            id: '5',
            source: 'mckinsey',
            title: 'Building Leaders in the Age of AI',
            summary: 'New research explores why digital fluency alone isn\'t enough—leaders must combine human strengths with AI capabilities.',
            url: 'https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/building-leaders-in-the-age-of-ai',
            published_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
            author: 'McKinsey & Company',
            is_saved: false
        },
        {
            id: '6',
            source: 'hbr',
            title: 'Match Your AI Strategy to Your Organization\'s Reality',
            summary: 'Don\'t just copy the tech giants. Tailor your AI adoption to your company\'s specific strengths and constraints.',
            url: 'https://hbr.org/2026/01/match-your-ai-strategy-to-your-organizations-reality',
            published_at: new Date(Date.now() - 18 * 60 * 60 * 1000).toISOString(),
            author: 'Harvard Business Review',
            is_saved: false
        },
        {
            id: '7',
            source: 'bens_bites',
            title: 'Anthropic Releases Claude 4: Enhanced Safety and Reasoning',
            summary: 'Anthropic\'s latest model Claude 4 sets new benchmarks in AI safety while maintaining strong performance...',
            url: 'https://bensbites.substack.com/archive',
            published_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
            author: 'Ben Tossell',
            is_saved: false
        },
        {
            id: '8',
            source: 'decrypt',
            title: 'Hollywood\'s AI Crackdown Opens Door for Copyright Detection Startups',
            summary: 'Studios are escalating pressure on AI developers, as new tools aim to document whether generative models are trained on copyrighted material.',
            url: 'https://decrypt.co/358131/hollywoods-ai-crackdown-copyright-detection-startups',
            published_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
            author: 'Decrypt',
            is_saved: false
        }
    ];
    return mockArticles;
}

// Render Articles
function renderArticles() {
    const filteredArticles = filterArticles(); // Changed from getFilteredArticles

    if (filteredArticles.length === 0) {
        showEmpty();
        return;
    }

    hideLoading();
    hideEmpty();

    elements.articlesGrid.innerHTML = filteredArticles.map(article => createArticleCard(article)).join('');

    // Attach save button listeners
    document.querySelectorAll('.save-button').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleSave(btn.dataset.id);
        });
    });

    // Attach card click listeners
    document.querySelectorAll('.article-card').forEach(card => {
        card.addEventListener('click', () => {
            window.open(card.dataset.url, '_blank');
        });
    });
}

// Create Article Card HTML
function createArticleCard(article) {
    const isSaved = state.savedArticles.includes(article.id);
    const timeAgo = getTimeAgo(article.published_at);
    const sourceLabel = getSourceLabel(article.source);

    return `
        <div class="article-card fade-in" data-url="${article.url}">
            <div class="article-header">
                <span class="article-source">${sourceLabel}</span>
                <button class="save-button ${isSaved ? 'saved' : ''}" data-id="${article.id}" title="${isSaved ? 'Unsave' : 'Save'} article">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="${isSaved ? 'currentColor' : 'none'}" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5 3a2 2 0 0 0-2 2v14l7-3.5L17 19V5a2 2 0 0 0-2-2H5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            </div>
            
            <h3 class="article-title">${escapeHtml(article.title)}</h3>
            
            ${article.summary ? `<p class="article-summary">${escapeHtml(article.summary)}</p>` : ''}
            
            <div class="article-footer">
                <div class="article-meta">
                    ${article.author ? `<span class="article-author">${escapeHtml(article.author)}</span>` : ''}
                    <span class="article-time">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M8 4v4l3 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                        ${timeAgo}
                    </span>
                </div>
                <span class="read-more">
                    Read more
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 12l4-4-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </span>
            </div>
        </div>
    `;
}

// Filter articles based on active filter
function filterArticles() { // Renamed from getFilteredArticles
    let filtered = [...state.articles];
    const filterValue = state.currentFilter;

    // Filter by source/saved
    if (filterValue === 'saved') {
        filtered = filtered.filter(a => state.savedArticles.includes(a.id));
    } else if (filterValue.startsWith('category:')) {
        const category = filterValue.split(':')[1];
        filtered = filtered.filter(a => getSourceCategory(a.source) === category);
    } else if (filterValue !== 'all') {
        filtered = filtered.filter(a => a.source === filterValue);
    }

    // Filter by search query
    if (state.searchQuery) {
        const query = state.searchQuery.toLowerCase();
        filtered = filtered.filter(a =>
            a.title.toLowerCase().includes(query) ||
            (a.summary && a.summary.toLowerCase().includes(query))
        );
    }

    // Sort
    filtered.sort((a, b) => {
        const dateA = new Date(a.published_at);
        const dateB = new Date(b.published_at);
        return state.sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
    });

    return filtered;
}

// Event Handlers
function handleSearch(e) {
    state.searchQuery = e.target.value;
    renderArticles();
}

async function handleRefresh() {
    elements.refreshBtn.disabled = true;
    elements.refreshBtn.innerHTML = '<div class="spinner" style="width: 20px; height: 20px; border-width: 2px;"></div> Refreshing...';

    await loadArticles();

    elements.refreshBtn.disabled = false;
    elements.refreshBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 4v6h6M19 16v-6h-6M2.51 9A8 8 0 0 1 17 6.5M17.49 11A8 8 0 0 1 3 13.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Refresh
    `;
}

function handleSort() {
    state.sortOrder = state.sortOrder === 'desc' ? 'asc' : 'desc';
    elements.sortBtn.textContent = state.sortOrder === 'desc' ? 'Sort by Date ↓' : 'Sort by Date ↑';
    renderArticles();
}

function handleFilterChange(filter) {
    state.currentFilter = filter;

    // Update active pill
    elements.filterPills.forEach(pill => {
        pill.classList.toggle('active', pill.dataset.filter === filter);
    });

    // Update section title
    const titles = {
        all: 'Latest Articles',
        bens_bites: "Ben's Bites Articles",
        ai_rundown: 'AI Rundown Articles',
        'category:ai': 'AI Articles',
        'category:crypto': 'Crypto Articles',
        'category:consulting': 'Consulting Articles',
        saved: 'Saved Articles'
    };
    elements.sectionTitle.textContent = titles[filter] || 'Latest Articles';

    renderArticles();
}

function handleClearFilters() {
    state.currentFilter = 'all';
    state.searchQuery = '';
    elements.searchInput.value = '';

    elements.filterPills.forEach(pill => {
        pill.classList.toggle('active', pill.dataset.filter === 'all');
    });

    elements.sectionTitle.textContent = 'Latest Articles';
    renderArticles();
}

function toggleSave(articleId) {
    const index = state.savedArticles.indexOf(articleId);

    if (index > -1) {
        state.savedArticles.splice(index, 1);
    } else {
        state.savedArticles.push(articleId);
    }

    // Persist to localStorage
    localStorage.setItem('savedArticles', JSON.stringify(state.savedArticles));

    updateSavedCount();
    renderArticles();
}

// Update Stats
function updateStats() {
    elements.totalArticles.textContent = state.articles.length;
    elements.savedCount.textContent = state.articles.filter(a => state.savedArticles.includes(a.id)).length; // Updated saved count logic
    elements.sourcesCount.textContent = '8'; // Updated to 8 sources
    elements.lastUpdate.textContent = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function updateSavedCount() {
    elements.savedCount.textContent = state.savedArticles.length;
}

// UI State Helpers
function showLoading() {
    elements.loadingState.style.display = 'flex';
    elements.articlesGrid.style.display = 'none';
    elements.emptyState.style.display = 'none';
}

function hideLoading() {
    elements.loadingState.style.display = 'none';
    elements.articlesGrid.style.display = 'grid';
}

function showEmpty() {
    elements.loadingState.style.display = 'none';
    elements.articlesGrid.style.display = 'none';
    elements.emptyState.style.display = 'block';
}

function hideEmpty() {
    elements.emptyState.style.display = 'none';
}

// Utility Functions
function getSourceLabel(source) {
    const labels = {
        'bens_bites': "Ben's Bites",
        'ai_rundown': 'AI Rundown',
        'cointelegraph': 'CoinTelegraph',
        'decrypt': 'Decrypt',
        'mckinsey': 'McKinsey Insights',
        'hbr': 'Harvard Business Review',
        'bcg': 'Boston Consulting Group',
        'bain': 'Bain & Company'
    };
    return labels[source] || source;
}

// Helper: Get category for source
function getSourceCategory(source) {
    const categories = {
        'bens_bites': 'ai',
        'ai_rundown': 'ai',
        'cointelegraph': 'crypto',
        'decrypt': 'crypto',
        'mckinsey': 'consulting',
        'hbr': 'consulting',
        'bcg': 'consulting',
        'bain': 'consulting'
    };
    return categories[source] || 'other';
}

function getTimeAgo(timestamp) {
    const now = new Date();
    const past = new Date(timestamp);
    const diffMs = now - past;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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

// Initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
