// ===== HIRMAGNET CIKK OLDAL OSZTÁLY =====

class ArticleViewer {
    constructor() {
        this.articleId = null;
        this.article = null;
        
        // Debug mode using utils
        this.debugMode = window.HirMagnetUtils.isDebugMode();
        
        this.init();
    }

    init() {
        console.log('🧲 ArticleViewer inicializálása...');
        
        if (this.debugMode) {
            window.HirMagnetUtils.showDebugPanel();
            window.HirMagnetUtils.debugLog('ArticleViewer initialized with debug mode');
        }
        
        // Get article ID from URL
        this.articleId = this.getArticleIdFromUrl();
        window.HirMagnetUtils.debugLog(`Article ID from URL: ${this.articleId}`);
        
        if (!this.articleId) {
            this.showError('Nincs megadva cikk azonosító');
            window.HirMagnetUtils.debugLog('ERROR: No article ID found in URL');
            return;
        }

        // Load article data
        this.loadArticle();
        
        // Load dashboard data for sidebar
        this.loadDashboardData();
        
        // Setup event listeners
        this.setupEventListeners();
    }

    getArticleIdFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        const id = urlParams.get('id');
        
        window.HirMagnetUtils.debugLog(`FULL URL: ${window.location.href}`);
        window.HirMagnetUtils.debugLog(`Search params: ${window.location.search}`);
        window.HirMagnetUtils.debugLog(`Extracted ID: ${id}`);
        
        // Debug alert
        if (this.debugMode && id) {
            alert(`DEBUG: Article ID extracted from URL\nFull URL: ${window.location.href}\nExtracted ID: ${id}`);
        }
        
        // Check hash for legacy support
        if (!id && window.location.hash) {
            const hash = window.location.hash.substring(1);
            const hashParams = new URLSearchParams(hash);
            const hashId = hashParams.get('id');
            window.HirMagnetUtils.debugLog(`Hash ID found: ${hashId}`);
            return hashId;
        }
        
        return id;
    }

    async loadArticle() {
        try {
            window.HirMagnetUtils.debugLog(`LOADING ARTICLE ID: ${this.articleId}`);
            console.log(`🧲 Cikk betöltése: ${this.articleId}`);
            
            const url = `/api/articles/${this.articleId}`;
            window.HirMagnetUtils.debugLog(`API URL: ${url}`);
            
            // Debug alert before fetch
            if (this.debugMode) {
                alert(`DEBUG: About to fetch article\nID: ${this.articleId}\nURL: ${url}`);
            }
            
            const response = await fetch(url);
            
            window.HirMagnetUtils.debugLog(`Response: ${response.status} ${response.statusText}`);
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('A keresett cikk nem található');
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.article = await response.json();
            
            // Debug logging
            window.HirMagnetUtils.debugLog(`ARTICLE LOADED: ID=${this.article.id}, Title="${this.article.title}"`);
            console.log('🧲 Betöltött cikk:', this.article);
            
            // Debug verification
            if (this.debugMode) {
                const confirmation = confirm(`DEBUG: Article loaded successfully!\n\nRequested ID: ${this.articleId}\nReceived ID: ${this.article.id}\nTitle: ${this.article.title}\n\nIs this the CORRECT article?\nClick OK if correct, Cancel if wrong.`);
                if (!confirmation) {
                    window.HirMagnetUtils.debugLog(`USER REPORTED: Wrong article loaded!`);
                    console.error('🚨 USER REPORTED WRONG ARTICLE:', {
                        requestedId: this.articleId,
                        receivedId: this.article.id,
                        receivedTitle: this.article.title,
                        fullArticle: this.article
                    });
                }
            }
            
            // Render article
            this.renderArticle();
            
            // Load related content
            this.loadRelatedContent();
            
        } catch (error) {
            console.error('Cikk betöltési hiba:', error);
            window.HirMagnetUtils.debugLog(`LOAD ERROR: ${error.message}`);
            this.showError(error.message);
        }
    }

    renderArticle() {
        window.HirMagnetUtils.debugLog('Rendering article content');
        
        // Hide loading, show content
        const loadingContainer = document.getElementById('loadingContainer');
        const articleContainer = document.getElementById('articleContainer');
        
        if (loadingContainer) loadingContainer.style.display = 'none';
        if (articleContainer) articleContainer.style.display = 'block';

        // Update page title
        document.title = `${this.article.title} - HírMagnet`;

        // Breadcrumbs
        const breadcrumbCategory = document.getElementById('breadcrumbCategory');
        const breadcrumbTitle = document.getElementById('breadcrumbTitle');
        if (breadcrumbCategory) breadcrumbCategory.textContent = window.HirMagnetUtils.getCategoryName(this.article.category);
        if (breadcrumbTitle) breadcrumbTitle.textContent = window.HirMagnetUtils.truncateText(this.article.title, 50);

        // Article title
        const articleTitle = document.getElementById('articleTitle');
        if (articleTitle) articleTitle.textContent = this.article.title;

        // Meta bar
        this.renderMetaBar();

        // Article content
        this.renderContent();

        // Audio player
        if (this.article.has_audio && this.article.audio_filename) {
            this.setupAudioPlayer();
            window.HirMagnetUtils.debugLog(`Audio player setup: ${this.article.audio_filename}`);
        }

        // AI Analytics
        if (this.article.seo_keywords || this.article.sentiment) {
            this.renderAIAnalytics();
            window.HirMagnetUtils.debugLog('AI Analytics rendered');
        }

        // Original article link
        const originalLink = document.getElementById('originalArticleLink');
        if (originalLink) {
            originalLink.href = this.article.url;
            originalLink.innerHTML = `🔗 Az Eredeti Cikk Teljes Terjedelmében (${this.article.source})`;
        }

        // Set active category in nav
        this.setActiveCategory();
        
        window.HirMagnetUtils.debugLog('Article rendering complete');
    }

    renderMetaBar() {
        const metaBar = document.getElementById('articleMeta');
        if (!metaBar) return;
        
        const publishedDate = this.article.published_at ? new Date(this.article.published_at) : new Date(this.article.created_at);
        const createdDate = new Date(this.article.created_at);

        metaBar.innerHTML = `
            <span class="meta-item"><strong>Forrás:</strong> <a href="${this.article.url}" target="_blank" rel="noopener noreferrer">${window.HirMagnetUtils.escapeHtml(this.article.source)}</a></span>
            <span class="meta-item"><strong>Kategória:</strong> ${window.HirMagnetUtils.getCategoryName(this.article.category)}</span>
            <span class="meta-item"><strong>Publikálva:</strong> ${window.HirMagnetUtils.formatDate(publishedDate)}</span>
            <span class="meta-item"><strong>AI összegzés:</strong> ${window.HirMagnetUtils.formatDate(createdDate)}</span>
            <span class="meta-item">Kb. ${window.HirMagnetUtils.estimateReadingTime(this.article.summary)} perc olvasás</span>
            <div class="article-share-buttons">
                <button title="Megosztás Facebookon" onclick="window.articleViewer.shareOnFacebook()">FB</button>
                <button title="Megosztás Twitteren" onclick="window.articleViewer.shareOnTwitter()">TW</button>
                <button title="Link másolása" onclick="window.articleViewer.copyLink()">🔗</button>
            </div>
        `;
    }

    renderContent() {
        const contentDiv = document.getElementById('articleContent');
        if (!contentDiv) return;
        
        // Create structured content from summary
        const content = this.article.summary || this.article.original_content || '';
        window.HirMagnetUtils.debugLog(`Content length: ${content.length} chars`);
        
        const paragraphs = content.split('\n').filter(p => p.trim().length > 0);

        let html = '';
        paragraphs.forEach((paragraph, index) => {
            if (index === 0) {
                html += `<p><strong>${window.HirMagnetUtils.escapeHtml(paragraph)}</strong></p>`;
            } else {
                html += `<p>${window.HirMagnetUtils.escapeHtml(paragraph)}</p>`;
            }
        });

        contentDiv.innerHTML = html;
    }

    setupAudioPlayer() {
        const audioPlayerDiv = document.getElementById('embeddedAudioPlayer');
        const audioElement = document.getElementById('articleAudio');
        const speedControl = document.getElementById('articleAudioSpeed');

        if (!audioPlayerDiv || !audioElement) return;

        const audioSource = audioElement.querySelector('source');

        // Set audio source
        const audioPath = `/static/audio/${this.article.audio_filename}`;
        audioSource.src = audioPath;
        audioElement.load();
        
        window.HirMagnetUtils.debugLog(`Audio source set: ${audioPath}`);

        // Show audio player
        audioPlayerDiv.style.display = 'block';

        // Speed control
        if (speedControl) {
            speedControl.addEventListener('change', (e) => {
                audioElement.playbackRate = parseFloat(e.target.value);
                window.HirMagnetUtils.debugLog(`Audio speed changed: ${e.target.value}x`);
            });
        }

        // Track play events
        audioElement.addEventListener('play', () => {
            this.trackAudioPlay();
        });

        // Set duration when loaded
        audioElement.addEventListener('loadedmetadata', () => {
            window.HirMagnetUtils.debugLog(`Audio duration: ${audioElement.duration}s`);
            console.log(`Audio duration: ${audioElement.duration}s`);
        });

        // Error handling
        audioElement.addEventListener('error', (e) => {
            window.HirMagnetUtils.debugLog(`Audio error: ${e.target.error?.message || 'Unknown audio error'}`);
            console.error('Audio error:', e);
        });
    }

    renderAIAnalytics() {
        const analyticsSection = document.getElementById('aiAnalytics');
        const analyticsContent = document.getElementById('analyticsContent');

        if (!analyticsSection || !analyticsContent) return;

        let html = '';

        // Keywords
        if (this.article.seo_keywords) {
            const keywords = this.article.seo_keywords.split(',').map(k => k.trim());
            const keywordSpans = keywords.map(k => `<span>${window.HirMagnetUtils.escapeHtml(k)}</span>`).join('');
            html += `<li><strong>Kulcsszavak:</strong> <span class="keywords-list">${keywordSpans}</span></li>`;
        }

        // Sentiment
        if (this.article.sentiment) {
            const sentimentText = this.getSentimentText(this.article.sentiment);
            html += `<li><strong>Hangulatelemzés:</strong> ${sentimentText}</li>`;
        }

        // View stats
        html += `<li><strong>Megtekintések:</strong> ${window.HirMagnetUtils.formatNumber(this.article.view_count)}</li>`;
        
        if (this.article.has_audio) {
            html += `<li><strong>Audio lejátszások:</strong> ${window.HirMagnetUtils.formatNumber(this.article.audio_play_count)}</li>`;
        }

        analyticsContent.innerHTML = html;
        analyticsSection.style.display = 'block';
    }

    async loadRelatedContent() {
        try {
            window.HirMagnetUtils.debugLog('Loading related content');
            
            // Load trending for sidebar
            const trendingResponse = await fetch('/api/trending?limit=5');
            if (trendingResponse.ok) {
                const trendingData = await trendingResponse.json();
                this.renderTrending(trendingData.trending);
                window.HirMagnetUtils.debugLog(`Loaded ${trendingData.trending.length} trending items`);
            }

            // Load related articles
            const relatedResponse = await fetch(`/api/articles?category=${this.article.category}&limit=3`);
            if (relatedResponse.ok) {
                const relatedData = await relatedResponse.json();
                const relatedArticles = relatedData.articles.filter(a => a.id !== this.article.id).slice(0, 3);
                if (relatedArticles.length > 0) {
                    this.renderRelatedArticles(relatedArticles);
                    window.HirMagnetUtils.debugLog(`Loaded ${relatedArticles.length} related articles`);
                }
            }

        } catch (error) {
            console.error('Related content betöltési hiba:', error);
            window.HirMagnetUtils.debugLog(`Related content error: ${error.message}`);
        }
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/dashboard-data');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.updateSidebarData(data);
            window.HirMagnetUtils.debugLog('Dashboard data loaded for article page');

        } catch (error) {
            console.error('Dashboard adatok betöltési hiba article page-en:', error);
            window.HirMagnetUtils.debugLog(`Dashboard load error: ${error.message}`);
        }
    }

    updateSidebarData(dashboardData) {
        if (!dashboardData) return;
        
        // Update financial rates
        this.updateFinancialRates(dashboardData.financial_rates);
        
        // Update weather  
        this.updateWeather(dashboardData.weather);
    }

    updateFinancialRates(financialData) {
        const container = document.querySelector('.financial-rates-content');
        
        if (!container || !financialData) return;

        let html = '';

        // Currencies
        if (financialData.currencies && financialData.currencies.length > 0) {
            html += '<div class="rate-category"><h4>Deviza (HUF)</h4><ul class="rate-list">';
            
            financialData.currencies.forEach(rate => {
                const trendClass = rate.trend === 'up' ? 'up' : 'down';
                const changeSign = rate.change.startsWith('+') || rate.change.startsWith('-') ? '' : (rate.trend === 'up' ? '+' : '-');
                html += `<li><span class="rate-pair">${rate.pair.replace('/HUF', '')}:</span><span class="rate-value">${rate.value}</span><span class="rate-change ${trendClass}">${changeSign}${rate.change}</span></li>`;
            });
            
            html += '</ul></div>';
        }

        // Crypto & Commodities
        if (financialData.crypto && financialData.crypto.length > 0) {
            html += '<div class="rate-category"><h4>Kripto / Nemesfém</h4><ul class="rate-list">';
            
            financialData.crypto.forEach(rate => {
                const trendClass = rate.trend === 'up' ? 'up' : 'down';
                const changeSign = rate.change.startsWith('+') || rate.change.startsWith('-') ? '' : (rate.trend === 'up' ? '+' : '-');
                html += `<li><span class="rate-pair">${rate.pair}:</span><span class="rate-value">${rate.value}</span><span class="rate-change ${trendClass}">${changeSign}${rate.change}</span></li>`;
            });
            
            html += '</ul></div>';
        }

        // Hungarian Stocks
        if (financialData.hungarian_stocks && financialData.hungarian_stocks.length > 0) {
            html += '<div class="rate-category"><h4>Magyar Részvények</h4><ul class="rate-list">';
            
            financialData.hungarian_stocks.forEach(rate => {
                const trendClass = rate.trend === 'up' ? 'up' : 'down';
                const changeSign = rate.change.startsWith('+') || rate.change.startsWith('-') ? '' : (rate.trend === 'up' ? '+' : '-');
                html += `<li><span class="rate-pair">${rate.pair}:</span><span class="rate-value">${rate.value}</span><span class="rate-change ${trendClass}">${changeSign}${rate.change}</span></li>`;
            });
            
            html += '</ul></div>';
        }

        html += '<p class="data-source-notice">Frissítve: ' + new Date().toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit'}) + '</p>';
        container.innerHTML = html;
    }

    updateWeather(weatherData) {
        const container = document.querySelector('.weather-widget-content');
        
        if (!container || !weatherData) return;

        container.innerHTML = `
            <div class="weather-main">
                <span class="weather-icon-placeholder">${weatherData.icon || '🌦️'}</span>
                <span class="weather-temp-placeholder">${weatherData.temperature}°C</span>
            </div>
            <p class="weather-location">${weatherData.city || 'Budapest'}</p>
            <span class="weather-details-link">Részletek &raquo;</span>
        `;
    }

    renderTrending(trending) {
        const container = document.getElementById('trendingItems');
        if (!container) return;
        
        container.innerHTML = '';

        trending.forEach(item => {
            const trendingItem = document.createElement('div');
            trendingItem.className = 'trending-item';
            trendingItem.onclick = () => this.navigateToArticle(item.id);
            
            const engagementScore = window.HirMagnetUtils.formatNumber(item.engagement_score);
            
            trendingItem.innerHTML = `
                <span>${window.HirMagnetUtils.escapeHtml(window.HirMagnetUtils.truncateText(item.title, 60))}</span>
                <span>${engagementScore}</span>
            `;
            
            container.appendChild(trendingItem);
        });
    }

    renderRelatedArticles(articles) {
        const section = document.getElementById('relatedArticles');
        const grid = document.getElementById('relatedArticlesGrid');
        
        if (!section || !grid) return;
        
        grid.innerHTML = '';

        articles.forEach(article => {
            const card = document.createElement('div');
            card.className = 'related-article-card';
            card.onclick = () => this.navigateToArticle(article.id);

            const timeAgo = window.HirMagnetUtils.formatTimeAgo(new Date(article.created_at));

            card.innerHTML = `
                <h4 class="related-title">${window.HirMagnetUtils.escapeHtml(article.title)}</h4>
                <p class="related-meta">${window.HirMagnetUtils.escapeHtml(article.source)} | ${window.HirMagnetUtils.getCategoryName(article.category)} | ${timeAgo}</p>
            `;

            grid.appendChild(card);
        });

        section.style.display = 'block';
    }

    setupEventListeners() {
        // Navigation category tabs
        document.querySelectorAll('.nav-tab[data-category]').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const category = tab.dataset.category;
                window.location.href = `index.html#category=${category}`;
            });
        });
    }

    setActiveCategory() {
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.category === this.article.category) {
                tab.classList.add('active');
            }
        });
    }

    async trackAudioPlay() {
        try {
            window.HirMagnetUtils.debugLog(`Tracking audio play for article ${this.articleId}`);
            const response = await fetch(`/api/articles/${this.articleId}/play`, { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                window.HirMagnetUtils.debugLog(`Audio play tracked, new count: ${data.play_count}`);
                console.log('Audio play tracked');
            }
        } catch (error) {
            console.error('Audio play tracking failed:', error);
            window.HirMagnetUtils.debugLog(`Audio play tracking failed: ${error.message}`);
        }
    }

    navigateToArticle(articleId) {
        window.HirMagnetUtils.debugLog(`Navigating to article: ${articleId}`);
        window.location.href = `article-view.html?id=${articleId}`;
    }

    shareOnFacebook() {
        const url = encodeURIComponent(window.location.href);
        const title = encodeURIComponent(this.article.title);
        window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}&t=${title}`, '_blank');
    }

    shareOnTwitter() {
        const url = encodeURIComponent(window.location.href);
        const title = encodeURIComponent(this.article.title);
        window.open(`https://twitter.com/intent/tweet?url=${url}&text=${title}`, '_blank');
    }

    copyLink() {
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert('Link vágólapra másolva!');
        }).catch(() => {
            alert('Link másolása sikertelen');
        });
    }

    showError(message) {
        window.HirMagnetUtils.debugLog(`Showing error: ${message}`);
        
        const loadingContainer = document.getElementById('loadingContainer');
        const articleContainer = document.getElementById('articleContainer');
        const errorContainer = document.getElementById('errorContainer');
        const errorMessage = document.getElementById('errorMessage');
        
        if (loadingContainer) loadingContainer.style.display = 'none';
        if (articleContainer) articleContainer.style.display = 'none';
        if (errorContainer) errorContainer.style.display = 'block';
        if (errorMessage) errorMessage.textContent = message;
    }

    getSentimentText(sentiment) {
        const sentiments = {
            'positive': 'Pozitív',
            'negative': 'Negatív',
            'neutral': 'Semleges'
        };
        return sentiments[sentiment] || 'Ismeretlen';
    }
}

// Export to global
window.ArticleViewer = ArticleViewer;

console.log('🧲 ArticleViewer Class betöltve');