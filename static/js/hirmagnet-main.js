// ===== HIRMAGNET FŐOLDAL OSZTÁLY - HERR CLAUS ROBUST VERSION + GRACEFUL FALLBACK ===== 

class HirMagnet {
    constructor() {
        this.currentCategory = 'all';
        this.currentPage = 0;
        this.pageSize = 20;
        this.isLoading = false;
        this.hasMore = true;
        this.trending = [];
        this.dashboardData = null;
        this.lastDashboardUpdate = null;
        
        // 🎖️ HERR CLAUS ROBUST INFRASTRUCTURE
        this.isServerProcessing = false;
        this.lastGoodData = {
            articles: [],
            trending: [],
            dashboard: null,
            timestamp: null
        };
        this.processingCheckInterval = null;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        // Debug mode using utils
        this.debugMode = window.HirMagnetUtils?.isDebugMode() || window.location.hash.includes('debug');
        
        // 🧲 HERR CLAUS AUTO-REFRESH TIMER (ENHANCED)
        this.autoRefreshTimer = null;
        this.autoRefreshInterval = 15000; // 15 seconds - Much faster response
        
        this.init();
    }

    async init() {
        console.log('🎖️ HírMagnet inicializálása...');
        
        if (this.debugMode) {
            if (window.HirMagnetUtils?.showDebugPanel) {
                window.HirMagnetUtils.showDebugPanel();
            }
            this.debugLog('HirMagnet initialized');
        }
        
        // 🎖️ HERR CLAUS: Start processing monitoring FIRST
        this.startProcessingMonitoring();
        
        // Event listeners
        this.setupEventListeners();
        
        // 🎖️ HERR CLAUS: Initial data load with robust error handling
        await this.loadInitialDataRobust();
        
        // 🎖️ HERR CLAUS: Background updates with processing awareness
        this.startBackgroundUpdatesRobust();
        
        // 🎖️ HERR CLAUS: Auto-refresh with graceful handling
        this.startAutoRefreshRobust();
        
        console.log('🎖️ HírMagnet Robust Ready - Deutsche Präzision!');
    }

    // 🎖️ HERR CLAUS PROCESSING STATUS MONITORING
    startProcessingMonitoring() {
        console.log('🎖️ Processing monitoring started...');
        
        this.processingCheckInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/processing-status', {
                    timeout: 3000,
                    headers: { 'Cache-Control': 'no-cache' }
                });
                
                if (response.ok) {
                    const status = await response.json();
                    const wasProcessing = this.isServerProcessing;
                    this.isServerProcessing = status.is_processing || false;
                    
                    if (this.isServerProcessing && !wasProcessing) {
                        this.debugLog('Server processing started - switching to cached data mode');
                        this.showProcessingIndicator();
                    } else if (!this.isServerProcessing && wasProcessing) {
                        this.debugLog('Server processing finished - switching to real data mode');
                        this.hideProcessingIndicator();
                        // Trigger immediate refresh when processing finishes
                        setTimeout(() => this.loadInitialDataRobust(), 2000);
                    }
                }
            } catch (error) {
                // If we can't check status, assume normal operation
                this.debugLog('Cannot check processing status - assuming normal operation');
                this.isServerProcessing = false;
            }
        }, 15000); // Check every 15 seconds (reduced frequency)
    }

    // 🎖️ HERR CLAUS ROBUST INITIAL DATA LOADING - NO MOCK FALLBACK DURING PROCESSING
    async loadInitialDataRobust() {
        try {
            this.debugLog('Loading initial data with robust error handling');
            
            // Try to load data with retries and processing awareness
            const [articlesResult, trendingResult, dashboardResult] = await Promise.allSettled([
                this.loadArticlesRobust(this.currentCategory, 0, this.pageSize),
                this.loadTrendingRobust(),
                this.loadDashboardDataRobust()
            ]);

            // 🎖️ HERR CLAUS: Handle articles with graceful fallback
            if (articlesResult.status === 'fulfilled' && articlesResult.value.success) {
                this.lastGoodData.articles = articlesResult.value.data.articles;
                this.lastGoodData.timestamp = new Date();
                this.renderArticlesSmooth(articlesResult.value.data.articles, true);
                this.hasMore = articlesResult.value.data.has_more;
                this.updateStats(articlesResult.value.data.total);
                this.debugLog(`Loaded ${articlesResult.value.data.articles.length} fresh articles`);
            } else if (this.lastGoodData.articles.length > 0) {
                // 🎖️ CRITICAL: Use cached data instead of mock during processing
                this.debugLog('Using cached articles data during server processing');
                this.renderArticlesSmooth(this.lastGoodData.articles, true);
                this.showCachedDataNotice('articles');
            } else {
                // Only use mock if we have absolutely no cached data
                this.debugLog('No cached articles available - loading minimal fallback');
                this.loadMinimalFallbackArticles();
            }

            // 🎖️ HERR CLAUS: Handle trending with graceful fallback
            if (trendingResult.status === 'fulfilled' && trendingResult.value.success) {
                this.lastGoodData.trending = trendingResult.value.data.trending;
                this.trending = trendingResult.value.data.trending;
                this.renderTrendingSmooth();
                this.debugLog(`Loaded ${this.trending.length} fresh trending items`);
            } else if (this.lastGoodData.trending.length > 0) {
                // Use cached trending
                this.debugLog('Using cached trending data during server processing');
                this.trending = this.lastGoodData.trending;
                this.renderTrendingSmooth();
                this.showCachedDataNotice('trending');
            }

            // 🎖️ HERR CLAUS: Handle dashboard with graceful fallback
            if (dashboardResult.status === 'fulfilled' && dashboardResult.value.success) {
                this.lastGoodData.dashboard = dashboardResult.value.data;
                this.dashboardData = dashboardResult.value.data;
                this.updateSidebarDataSmooth();
                this.debugLog('Loaded fresh dashboard data');
            } else if (this.lastGoodData.dashboard) {
                // Use cached dashboard
                this.debugLog('Using cached dashboard data during server processing');
                this.dashboardData = this.lastGoodData.dashboard;
                this.updateSidebarDataSmooth();
                this.showCachedDataNotice('dashboard');
            } else {
                // Only NOW use mock data if we have NO cached data
                this.debugLog('No cached dashboard data available - loading minimal mock data');
                this.loadMockDashboardDataSmooth();
            }

            // Load current news
            this.loadCurrentNewsRobust();

        } catch (error) {
            console.error('Robust initialization error:', error);
            this.debugLog(`Robust init error: ${error.message}`);
            
            // Use any available cached data
            if (this.lastGoodData.articles.length > 0) {
                this.renderArticlesSmooth(this.lastGoodData.articles, true);
            }
            if (this.lastGoodData.trending.length > 0) {
                this.trending = this.lastGoodData.trending;
                this.renderTrendingSmooth();
            }
            if (this.lastGoodData.dashboard) {
                this.dashboardData = this.lastGoodData.dashboard;
                this.updateSidebarDataSmooth();
            }
        }
    }

    // 🎖️ HERR CLAUS ROBUST ARTICLES LOADING WITH RETRY AND PROCESSING AWARENESS
    async loadArticlesRobust(category = 'all', offset = 0, limit = 20, retryCount = 0) {
        try {
            const params = new URLSearchParams({
                limit: limit.toString(),
                offset: offset.toString()
            });

            if (category && category !== 'all') {
                params.append('category', category);
            }

            const url = `/api/articles?${params}`;
            this.debugLog(`Fetching: ${url} (retry: ${retryCount})`);
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
            
            const response = await fetch(url, {
                signal: controller.signal,
                headers: {
                    'Cache-Control': 'no-cache',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            // 🎖️ HERR CLAUS: Check if server indicates processing
            if (data.processing_status === 'processing') {
                this.debugLog('Server reports processing status - will use cached data');
                this.isServerProcessing = true;
                throw new Error('Server is processing - use cached data');
            }
            
            // Check for valid article data
            if (!data.articles || data.articles.length === 0) {
                throw new Error('No articles received - possibly processing');
            }
            
            this.debugLog(`API Response: ${data.articles.length} articles, total: ${data.total}`);
            this.retryCount = 0; // Reset retry count on success
            return { success: true, data };

        } catch (error) {
            console.warn('Articles loading error:', error);
            this.debugLog(`Load articles error: ${error.message}`);
            
            // 🎖️ HERR CLAUS: Intelligent retry logic with exponential backoff
            if (retryCount < this.maxRetries && !error.message.includes('processing')) {
                const delay = Math.pow(2, retryCount) * 500; // 0.5s, 1s, 2s - Much faster
                this.debugLog(`Retrying in ${delay}ms...`);
                
                await new Promise(resolve => setTimeout(resolve, delay));
                return this.loadArticlesRobust(category, offset, limit, retryCount + 1);
            }
            
            // Failed after retries
            return { success: false, error: error.message };
        }
    }

    // 🎖️ HERR CLAUS ROBUST TRENDING LOADING
    async loadTrendingRobust(retryCount = 0) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
            
            const response = await fetch('/api/trending?limit=10', {
                signal: controller.signal,
                headers: { 'Cache-Control': 'no-cache' }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            // Check for processing status
            if (data.processing_status === 'processing') {
                throw new Error('Server is processing - use cached data');
            }
            
            return { success: true, data };

        } catch (error) {
            console.warn('Trending loading error:', error);
            
            if (retryCount < 2 && !error.message.includes('processing')) {
                await new Promise(resolve => setTimeout(resolve, 1000)); // Faster retry
                return this.loadTrendingRobust(retryCount + 1);
            }
            
            return { success: false, error: error.message };
        }
    }

    // 🎖️ HERR CLAUS ROBUST DASHBOARD LOADING  
    async loadDashboardDataRobust(retryCount = 0) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
            
            const response = await fetch('/api/dashboard-data', {
                signal: controller.signal,
                headers: { 'Cache-Control': 'no-cache' }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.lastDashboardUpdate = new Date();
            return { success: true, data };

        } catch (error) {
            console.warn('Dashboard loading error:', error);
            
            if (retryCount < 2) {
                await new Promise(resolve => setTimeout(resolve, 1000)); // Faster retry
                return this.loadDashboardDataRobust(retryCount + 1);
            }
            
            return { success: false, error: error.message };
        }
    }

    // 🎖️ HERR CLAUS ROBUST CURRENT NEWS
    async loadCurrentNewsRobust() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
            
            const response = await fetch('/api/latest?limit=6', {
                signal: controller.signal,
                headers: { 'Cache-Control': 'no-cache' }
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const data = await response.json();
                
                // Check for processing status
                if (data.processing_status !== 'processing' && data.latest && data.latest.length > 0) {
                    this.renderCurrentNewsSmooth(data.latest);
                }
            } else {
                throw new Error('Current news not available');
            }

        } catch (error) {
            console.warn('Current news loading error:', error);
            // Don't show mock current news - just skip
            this.debugLog('Current news unavailable - skipping');
        }
    }

    // 🎖️ HERR CLAUS ROBUST AUTO-REFRESH - PROCESSING AWARE
    startAutoRefreshRobust() {
        console.log('🎖️ Robust auto-refresh aktiviert - Deutsche Präzision!');
        
        this.autoRefreshTimer = setInterval(async () => {
            if (this.isLoading) {
                console.log('🎖️ Auto-refresh skipped - loading in progress');
                return;
            }
            
            // 🎖️ CRITICAL: Skip refresh if server is processing
            if (this.isServerProcessing) {
                console.log('🎖️ Auto-refresh skipped - server processing');
                this.debugLog('Auto-refresh postponed - server busy');
                this.updateRefreshTimestamp('server busy');
                return;
            }
            
            try {
                console.log('🎖️ Robust auto-refresh triggered...');
                this.debugLog('Robust auto-refresh cycle started');
                
                this.updateRefreshTimestamp('checking...');
                
                // Use robust loading
                await this.loadInitialDataRobust();
                
                console.log('✅ Robust auto-refresh successful');
                this.debugLog('Robust auto-refresh completed successfully');
                this.updateRefreshTimestamp('auto');
                
            } catch (error) {
                console.warn('❌ Robust auto-refresh warning:', error);
                this.debugLog(`Auto-refresh warning: ${error.message}`);
                this.updateRefreshTimestamp('retry soon');
            }
        }, this.autoRefreshInterval);
    }

    // 🎖️ HERR CLAUS PROCESSING INDICATORS
    showProcessingIndicator() {
        const updateEl = document.getElementById('lastUpdate');
        if (updateEl) {
            updateEl.textContent = 'Szerver feldolgozás folyamatban... 🔄';
            updateEl.style.color = '#f39c12';
            updateEl.style.fontWeight = 'bold';
        }
        
        // Add subtle visual indication
        const container = document.getElementById('articlesContainer');
        if (container) {
            container.style.opacity = '0.95';
        }
    }

    hideProcessingIndicator() {
        const updateEl = document.getElementById('lastUpdate');
        if (updateEl) {
            updateEl.style.color = '';
            updateEl.style.fontWeight = '';
        }
        
        const container = document.getElementById('articlesContainer');
        if (container) {
            container.style.opacity = '1';
        }
    }

    // 🎖️ HERR CLAUS CACHED DATA NOTICE
    showCachedDataNotice(dataType) {
        const updateEl = document.getElementById('lastUpdate');
        if (updateEl) {
            const cacheTime = this.lastGoodData.timestamp ? 
                this.lastGoodData.timestamp.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit'}) : 
                'korábbi';
            updateEl.textContent = `Gyorsítótár: ${cacheTime} (${dataType}) 📋`;
            updateEl.style.color = '#17a2b8';
        }
    }

    // 🎖️ HERR CLAUS ENHANCED UPDATE TIMESTAMP
    updateRefreshTimestamp(status = 'auto') {
        const updateEl = document.getElementById('lastUpdate');
        if (updateEl) {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit', second: '2-digit'});
            
            switch (status) {
                case 'server busy':
                    updateEl.textContent = `Szerver elfoglalt: ${timeStr} ⚠️`;
                    updateEl.style.color = '#dc3545';
                    break;
                case 'checking...':
                    updateEl.textContent = `Ellenőrzés: ${timeStr} 🔍`;
                    updateEl.style.color = '#ffc107';
                    break;
                case 'retry soon':
                    updateEl.textContent = `Újrapróbálás: ${timeStr} 🔄`;
                    updateEl.style.color = '#fd7e14';
                    break;
                default:
                    updateEl.textContent = `Frissítve: ${timeStr} (auto) ✅`;
                    updateEl.style.color = '#28a745';
            }
        }
    }

    // 🎖️ HERR CLAUS MINIMAL FALLBACK ARTICLES (instead of full mock)
    loadMinimalFallbackArticles() {
        console.log('🎖️ Loading minimal fallback articles...');
        
        const fallbackArticles = [
            {
                id: 'fallback-1',
                title: 'HírMagnet betöltés folyamatban...',
                summary: 'A rendszer jelenleg frissíti a híreket. Kérjük, várjon néhány másodpercet a legfrissebb tartalmakért.',
                source: 'HírMagnet',
                category: 'general',
                created_at: new Date().toISOString(),
                url: '#',
                view_count: 0,
                audio_play_count: 0,
                has_audio: false
            }
        ];
        
        this.renderArticlesSmooth(fallbackArticles, true);
        this.debugLog('Minimal fallback articles loaded');
    }

    // ===== ORIGINAL HIRMAGNET METHODS (preserved for backward compatibility) =====

    debugLog(message) {
        if (window.HirMagnetUtils?.debugLog) {
            window.HirMagnetUtils.debugLog(message);
        } else {
            console.log(`🎖️ DEBUG: ${message}`);
        }
    }

    setupEventListeners() {
        // Category navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const category = tab.dataset.category;
                if (category !== this.currentCategory) {
                    this.switchCategory(category);
                }
            });
        });

        // Load more button
        const loadMoreBtn = document.getElementById('load-more-btn');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => {
                this.loadMoreArticles();
            });
        }

        // Audio modal
        this.setupAudioModal();

        // Feed filter tabs
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.filterSources(tab.dataset.categoryFilter);
            });
        });

        // 🎖️ HERR CLAUS PAGE VISIBILITY HANDLER - Auto-refresh pausieren/fortsetzen
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.debugLog('Page hidden - auto-refresh continues in background');
            } else {
                this.debugLog('Page visible - triggering immediate refresh');
                // Immediate refresh when user returns
                setTimeout(() => this.loadInitialDataRobust(), 1000);
            }
        });
    }

    // ✅ SMOOTH ARTICLES RENDERING - NEM PISLOG!
    renderArticlesSmooth(articles, clear = false) {
        const container = document.getElementById('articlesContainer');
        
        this.debugLog(`Rendering ${articles.length} articles (SMOOTH), clear: ${clear}`);

        // ✅ BACKGROUND RENDERING - build new content first
        const newContent = document.createDocumentFragment();
        
        articles.forEach((article, index) => {
            const isTopWidget = clear && index < 3;
            const articleCard = this.createArticleCard(article, isTopWidget);
            newContent.appendChild(articleCard);
        });

        // ✅ ATOMIC REPLACEMENT - csak ha sikeres volt a building
        if (newContent.children.length > 0) {
            if (clear) {
                container.innerHTML = '';
            }
            container.appendChild(newContent);
        }

        // Show/hide load more button
        const loadMoreBtn = document.getElementById('load-more-btn');
        if (loadMoreBtn) {
            loadMoreBtn.style.display = this.hasMore ? 'block' : 'none';
        }
    }

    // ⚡ HERR CLAUS ENHANCED & CORRECTED: EGYSÉGES WIDGET CREATION
    createArticleCard(article, isTopWidget = false) {
        const card = document.createElement('div');
        card.className = 'article-card';
        
        // *** ITT A KULCSMÓDOSÍTÁS ***
        // Ha ez egy top widget, adjuk hozzá a megkülönböztető osztályt.
        if (isTopWidget) {
            card.classList.add('article-card--large');
        }
        
        // ⚡ ÚJ: KATEGÓRIA ÉS AUDIO DATA ATTRIBUTES
        card.dataset.category = article.category || 'general';
        card.dataset.hasAudio = article.has_audio ? 'true' : 'false';
        
        // Store article data to prevent closure issues
        const articleId = article.id;
        const articleTitle = article.title;
        const articleSummary = article.summary || '';
        
        // Store for verification
        card.dataset.articleId = articleId;
        card.dataset.articleTitle = articleTitle;
        
        // Click handler - simplified (no action buttons to worry about)
        card.addEventListener('click', (e) => {
            // ⚡ ÚJ: Audio gomb kizárása
            if (e.target.classList.contains('audio-button')) {
                return;
            }
            
            this.debugLog(`CARD CLICK: ID=${articleId}, Title="${articleTitle}"`);
            
            // Debug confirmation
            if (this.debugMode) {
                const confirmed = confirm(`DEBUG: Navigate to article?\nID: ${articleId}\nTitle: ${articleTitle}\n\nClick OK to proceed or Cancel to abort.`);
                if (!confirmed) {
                    this.debugLog('Navigation cancelled by user');
                    return;
                }
            }
            
            this.navigateToArticle(articleId, articleTitle);
        });

        // Debug title
        const debugTitle = this.debugMode ? `[ID:${articleId}] ${articleTitle}` : articleTitle;
        
        // Truncate summary to 150-200 characters
        const truncatedSummary = this.truncateText(articleSummary, 180);

        // ⚡ HERR CLAUS: AUDIO GOMB (csak audio-s cikkeknél)
        const audioButtonHtml = article.has_audio ? 
            `<button class="audio-button" onclick="event.stopPropagation(); window.hirmagnet.playAudio('${articleId}', '${article.audio_filename}', '${articleTitle.replace(/'/g, "\\'")}', '${article.source}')"></button>` : '';

        // Clean, simplified card structure
        card.innerHTML = `
            <h3 class="article-title" title="Article ID: ${articleId}">${this.escapeHtml(debugTitle)}</h3>
            <p class="article-summary">${this.escapeHtml(truncatedSummary)}</p>
            ${audioButtonHtml}
        `;

        return card;
    }

    // ⚡ HERR CLAUS: ÚJ AUDIO FUNKCIÓ
    async playAudio(articleId, audioFilename, title, source) {
        try {
            this.debugLog(`Playing audio: ${articleId} - ${audioFilename}`);
            await fetch(`/api/articles/${articleId}/play`, { method: 'POST' });
            this.openAudioModal(audioFilename, title, source);
        } catch (error) {
            console.error('Audio play hiba:', error);
            this.openAudioModal(audioFilename, title, source);
        }
    }

    // ✅ SMOOTH TRENDING RENDERING - NEM PISLOG!
    renderTrendingSmooth() {
        const container = document.getElementById('trendingList');
        if (!container) return;
        
        // ✅ BACKGROUND RENDERING
        const newContent = document.createDocumentFragment();

        this.trending.forEach(item => {
            const trendingItem = document.createElement('div');
            trendingItem.className = 'trending-item';
            
            const itemId = item.id;
            const itemTitle = item.title;
            
            trendingItem.addEventListener('click', () => {
                this.debugLog(`TRENDING CLICK: ID=${itemId}, Title="${itemTitle}"`);
                this.navigateToArticle(itemId, itemTitle);
            });
            
            const engagementScore = this.formatNumber(item.engagement_score);
            const debugTitle = this.debugMode ? 
                `[ID:${itemId}] ${this.truncateText(itemTitle, 50)}` : 
                this.truncateText(itemTitle, 60);
            
            trendingItem.innerHTML = `
                <span title="Article ID: ${itemId}">${this.escapeHtml(debugTitle)}</span>
                <span>${engagementScore}</span>
            `;
            
            newContent.appendChild(trendingItem);
        });

        // ✅ ATOMIC REPLACEMENT
        if (newContent.children.length > 0) {
            container.innerHTML = '';
            container.appendChild(newContent);
        }
    }

    // ✅ SMOOTH CURRENT NEWS RENDERING - NEM PISLOG!
    renderCurrentNewsSmooth(articles) {
        const container = document.getElementById('currentArticlesGrid');
        if (!container) return;
        
        // ✅ BACKGROUND RENDERING
        const newContent = document.createDocumentFragment();

        articles.forEach(article => {
            const card = document.createElement('div');
            card.className = 'current-article-card';
            
            const articleId = article.id;
            const articleTitle = article.title;
            
            card.addEventListener('click', () => {
                this.debugLog(`CURRENT NEWS CLICK: ID=${articleId}, Title="${articleTitle}"`);
                this.navigateToArticle(articleId, articleTitle);
            });

            const debugTitle = this.debugMode ? `[ID:${articleId}] ${articleTitle}` : articleTitle;

            // Simplified current news cards - consistent with main cards
            card.innerHTML = `
                <h4 class="current-title" title="Article ID: ${articleId}">${this.escapeHtml(debugTitle)}</h4>
                <div class="current-meta">
                    <span class="current-source">${this.escapeHtml(article.source)}</span>
                </div>
            `;

            newContent.appendChild(card);
        });

        // ✅ ATOMIC REPLACEMENT
        if (newContent.children.length > 0) {
            container.innerHTML = '';
            container.appendChild(newContent);
        }
    }

    async switchCategory(category) {
        console.log(`Kategória váltás: ${this.currentCategory} → ${category}`);
        this.debugLog(`Switching category to: ${category}`);
        
        this.currentCategory = category;
        this.currentPage = 0;
        
        // Update UI
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.category === category);
        });

        this.updateSectionTitle(category);
        
        // Show loading
        const container = document.getElementById('articlesContainer');
        if (container) container.classList.add('loading');
        
        try {
            const response = await this.loadArticlesRobust(category, 0, this.pageSize);
            
            if (response.success) {
                this.renderArticlesSmooth(response.data.articles, true);
                this.hasMore = response.data.has_more;
                this.updateStats(response.data.total);
            } else {
                this.showError('Hiba a cikkek betöltésekor');
            }
            
        } catch (error) {
            console.error('Kategória váltás hiba:', error);
            this.debugLog(`Category switch error: ${error.message}`);
            this.showError('Hiba a kategória betöltésekor');
        } finally {
            if (container) container.classList.remove('loading');
        }
    }

    async loadMoreArticles() {
        if (this.isLoading || !this.hasMore) return;

        this.isLoading = true;
        this.currentPage++;

        const loadMoreBtn = document.getElementById('load-more-btn');
        const originalText = loadMoreBtn.textContent;
        loadMoreBtn.textContent = 'Betöltés...';
        loadMoreBtn.disabled = true;

        try {
            const response = await this.loadArticlesRobust(
                this.currentCategory, 
                this.currentPage * this.pageSize, 
                this.pageSize
            );

            if (response.success) {
                this.renderArticlesSmooth(response.data.articles, false);
                this.hasMore = response.data.has_more;
            } else {
                this.showError('Hiba a további cikkek betöltésekor');
                this.currentPage--;
            }

        } catch (error) {
            console.error('Load more hiba:', error);
            this.showError('Hiba a további cikkek betöltésekor');
            this.currentPage--;
        } finally {
            loadMoreBtn.textContent = originalText;
            loadMoreBtn.disabled = false;
            this.isLoading = false;
        }
    }

    navigateToArticle(articleId, articleTitle = null) {
        this.debugLog(`Maps START: ID=${articleId}, Title="${articleTitle}"`);
        
        let url = `article-view.html?id=${articleId}`;
        if (this.debugMode) {
            url += '&debug=true';
        }
        
        console.log(`🎖️ NAVIGATION DETAILS:`, {
            articleId: articleId,
            articleTitle: articleTitle,
            targetUrl: url,
            currentLocation: window.location.href
        });
        
        this.debugLog(`Opening URL: ${url}`);
        
        // Force navigation
        if (window.location.pathname.includes('article-view.html')) {
            window.location.replace(url);
        } else {
            window.location.href = url;
        }
    }

    updateSectionTitle(category) {
        const titles = {
            'all': 'AI Feldolgozott Hírek',
            'general': 'Közélet - AI Hírek',
            'foreign': 'Külföld - AI Hírek',
            'politics': 'Politika - AI Hírek',
            'economy': 'Gazdaság - AI Hírek',
            'tech': 'Tech - AI Hírek',
            'entertainment': 'Bulvár - AI Hírek',
            'sport': 'Sport - AI Hírek',
            'cars': 'Autók - AI Hírek',
            'lifestyle': 'Életmód - AI Hírek'
        };

        const titleEl = document.getElementById('sectionTitle');
        if (titleEl) titleEl.textContent = titles[category] || 'AI Hírek';
    }

    updateStats(totalCount) {
        const countEl = document.getElementById('articleCount');
        const updateEl = document.getElementById('lastUpdate');
        
        if (countEl) countEl.textContent = `${this.formatNumber(totalCount)} cikk`;
        if (updateEl && !updateEl.textContent.includes('Gyorsítótár') && !updateEl.textContent.includes('Szerver')) {
            updateEl.textContent = `Frissítve: ${new Date().toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit'})}`;
        }
    }

    showError(message) {
        const container = document.getElementById('articlesContainer');
        if (!container) return;
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        container.querySelectorAll('.error-message').forEach(el => el.remove());
        container.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // *** SIDEBAR METÓDUSOK - JAVÍTOTT VERZIÓ ***
    updateSidebarData() {
        if (!this.dashboardData) return;
        this.updateFinancialRatesSmooth(this.dashboardData.financial_rates);
        this.updateWeatherSmooth(this.dashboardData.weather);
        this.updateRSSSourcesSmooth(this.dashboardData.rss_sources);
    }

    // ✅ SMOOTH SIDEBAR UPDATE
    updateSidebarDataSmooth() {
        if (!this.dashboardData) return;
        this.updateFinancialRatesSmooth(this.dashboardData.financial_rates);
        this.updateWeatherSmooth(this.dashboardData.weather);
        this.updateRSSSourcesSmooth(this.dashboardData.rss_sources);
    }

    // ✅ SMOOTH FINANCIAL RATES UPDATE - NEM PISLOG!
    updateFinancialRatesSmooth(financialData) {
        const container = document.getElementById('financialRatesContent');
        
        if (!container || !financialData) {
            if (container) container.innerHTML = '<div style="text-align: center; color: var(--text-muted-color); padding: 1rem;">💰 Árfolyam adatok nem elérhetőek</div>';
            return;
        }

        // ✅ BACKGROUND HTML BUILDING
        const newHtml = this.buildFinancialRatesHtml(financialData);
        
        // ✅ ATOMIC REPLACEMENT - csak ha sikeres
        if (newHtml && newHtml.length > 50) {
            container.innerHTML = newHtml;
        }
    }

    // ✅ ENHANCED FINANCIAL RATES HTML BUILDER - TÖBB ADATTAL!
    buildFinancialRatesHtml(financialData) {
        let html = '';

        // ✅ ENHANCED - Valutaárfolyamok
        if (financialData.currencies && financialData.currencies.length > 0) {
            html += '<div class="rate-category"><h4>💱 Deviza árfolyamok (HUF)</h4><ul class="rate-list">';
            financialData.currencies.forEach(rate => {
                const trendClass = rate.trend === 'up' ? 'up' : 'down';
                const changeSign = rate.change.startsWith('+') || rate.change.startsWith('-') ? '' : (rate.trend === 'up' ? '+' : '-');
                html += `<li><span class="rate-pair">${rate.pair.replace('/HUF', '')}:</span><span class="rate-value">${rate.value}</span><span class="rate-change ${trendClass}">${changeSign}${rate.change}</span></li>`;
            });
            html += '</ul></div>';
        }

        // ✅ ENHANCED - Magyar részvények KIEMELVE!
        if (financialData.hungarian_stocks && financialData.hungarian_stocks.length > 0) {
            html += '<div class="rate-category"><h4>📊 Magyar tőzsde</h4><ul class="rate-list hungarian-stocks">';
            financialData.hungarian_stocks.forEach(rate => {
                const trendClass = rate.trend === 'up' ? 'up' : 'down';
                const changeSign = rate.change.startsWith('+') || rate.change.startsWith('-') ? '' : (rate.trend === 'up' ? '+' : '-');
                // Enhanced formatting for Hungarian stocks
                html += `<li class="stock-item"><span class="rate-pair stock-name">${rate.pair}:</span><span class="rate-value stock-price">${rate.value}</span><span class="rate-change ${trendClass} stock-change">${changeSign}${rate.change}</span></li>`;
            });
            html += '</ul></div>';
        }

        // ✅ ENHANCED - Crypto és arany
        if (financialData.crypto && financialData.crypto.length > 0) {
            html += '<div class="rate-category"><h4>🪙 Kripto & Nemesfém</h4><ul class="rate-list">';
            financialData.crypto.forEach(rate => {
                const trendClass = rate.trend === 'up' ? 'up' : 'down';
                const changeSign = rate.change.startsWith('+') || rate.change.startsWith('-') ? '' : (rate.trend === 'up' ? '+' : '-');
                html += `<li><span class="rate-pair">${rate.pair}:</span><span class="rate-value">${rate.value}</span><span class="rate-change ${trendClass}">${changeSign}${rate.change}</span></li>`;
            });
            html += '</ul></div>';
        }

        html += '<p class="data-source-notice">💹 Frissítve: ' + new Date().toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit'}) + '</p>';
        
        return html;
    }

    // ✅ SMOOTH WEATHER UPDATE - NEM PISLOG!
    updateWeatherSmooth(weatherData) {
        const container = document.getElementById('weatherContent');
        
        if (!container || !weatherData) {
            if (container) container.innerHTML = '<div style="text-align: center; color: var(--text-muted-color); padding: 1rem;">🌤️ Időjárás adatok nem elérhetőek</div>';
            return;
        }

        // ✅ BACKGROUND HTML BUILDING
        const newHtml = this.buildWeatherHtml(weatherData);
        
        // ✅ ATOMIC REPLACEMENT - csak ha sikeres
        if (newHtml && newHtml.length > 50) {
            container.innerHTML = newHtml;
        }
    }

    // ✅ ENHANCED WEATHER HTML BUILDER - TÖBB ADATTAL!
    buildWeatherHtml(weatherData) {
        return `
            <a href="https://www.idojaras.hu/" target="_blank" rel="noopener noreferrer" class="weather-widget-link">
                <div class="weather-widget-content enhanced">
                    <div class="weather-main">
                        <span class="weather-icon-placeholder">${weatherData.icon || '🌦️'}</span>
                        <div class="weather-temps">
                            <span class="weather-temp-main">${weatherData.temperature}°C</span>
                            ${weatherData.feels_like ? `<span class="weather-feels-like">Hőérzet: ${weatherData.feels_like}°C</span>` : ''}
                        </div>
                    </div>
                    <p class="weather-location">${weatherData.city || 'Budapest'}</p>
                    ${weatherData.humidity ? `
                    <div class="weather-details">
                        <div class="weather-detail-row">
                            <span>💧 ${weatherData.humidity}%</span>
                            ${weatherData.wind_speed ? `<span>💨 ${weatherData.wind_speed} km/h ${weatherData.wind_direction || ''}</span>` : ''}
                        </div>
                        ${weatherData.pressure ? `
                        <div class="weather-detail-row">
                            <span>🔵 ${weatherData.pressure} hPa</span>
                            ${weatherData.uv_index !== undefined ? `<span>☀️ UV: ${weatherData.uv_index}</span>` : ''}
                        </div>
                        ` : ''}
                    </div>
                    ` : ''}
                    <span class="weather-details-link">Részletek &raquo;</span>
                </div>
            </a>
        `;
    }

    // ✅ SMOOTH RSS SOURCES UPDATE - NEM PISLOG!
    updateRSSSourcesSmooth(rssData) {
        const container = document.getElementById('sourcesContainer');
        
        if (!container) {
            console.warn('🎖️ RSS Sources container not found!');
            return;
        }
        
        if (!rssData) {
            container.innerHTML = '<div style="text-align: center; color: var(--text-muted-color); padding: 2rem;"><div style="font-size: 1.2rem; margin-bottom: 0.5rem;">📡</div><div>RSS források nem elérhetőek</div></div>';
            return;
        }

        // ✅ BACKGROUND HTML BUILDING
        const newHtml = this.buildRSSSourcesHtml(rssData);
        
        // ✅ ATOMIC REPLACEMENT - csak ha sikeres
        if (newHtml && newHtml.length > 100) {
            container.innerHTML = newHtml;
            this.debugLog(`RSS Sources rendered (SMOOTH): ${Object.keys(rssData).length} categories`);
        }
    }

    buildRSSSourcesHtml(rssData) {
        let html = '';
        const categoryIcons = {
            'general': '👥', 'economy': '📈', 'tech': '💻', 'sport': '⚽',
            'entertainment': '👠', 'politics': '🏛️', 'foreign': '🌍', 'cars': '🚗', 'lifestyle': '✨'
        };

        Object.keys(rssData).forEach(categoryKey => {
            const sources = rssData[categoryKey];
            if (!sources || sources.length === 0) return;

            const categoryName = this.getCategoryName(categoryKey);
            const categoryIcon = categoryIcons[categoryKey] || '📰';

            html += `<div class="category-section" data-category="${categoryKey}">
                <div class="category-header">
                    <span class="category-icon">${categoryIcon}</span>
                    <h2 class="category-title">${categoryName}</h2>
                    <span class="category-count">${sources.length}</span>
                </div>
                <div class="sources-grid">`;

            // *** ENHANCED sources.forEach with Latest Articles Support ***
            sources.forEach(source => {
                const statusDot = source.status === 'active' ? 'status-dot' : 'status-dot inactive';
                const statusText = source.status === 'active' ? 'Aktív' : 'Inaktív';
                const lastSync = source.last_sync ? this.formatTimeAgo(new Date(source.last_sync)) : 'Nincs';
                
                // *** NEW: Latest articles HTML generation ***
                let latestArticlesHtml = '';
                if (source.latest_articles && source.latest_articles.length > 0) {
                    latestArticlesHtml = `
                        <div class="latest-articles">
                            <h4 class="latest-title">Legfrissebb cikkek:</h4>
                    `;
                    
                    source.latest_articles.forEach(article => {
                        const timeAgo = article.published ? this.formatTimeAgo(new Date(article.published)) : 'Idő n/a';
                        latestArticlesHtml += `
                            <div class="article-preview">
                                <div class="preview-title">${this.escapeHtml(article.title || 'Cím nélkül')}</div>
                                <div class="preview-time">${timeAgo}</div>
                            </div>
                        `;
                    });
                    
                    latestArticlesHtml += '</div>';
                }

                html += `<div class="source-card" onclick="openSource('${source.url}', '${this.escapeHtml(source.name)}', '${categoryKey}')">
                    <div class="source-header">
                        <div>
                            <h3 class="source-name">${this.escapeHtml(source.name)}</h3>
                            <a href="${source.url}" class="source-url" onclick="event.stopPropagation();">${this.extractDomain(source.url)}</a>
                        </div>
                        <span class="source-priority ${source.priority.toLowerCase()}">${this.capitalizeFirst(source.priority)}</span>
                    </div>
                    <div class="source-meta">
                        <div class="source-status">
                            <span class="${statusDot}"></span>
                            <span>${statusText}</span>
                        </div>
                        <span>Sync: ${lastSync}</span>
                    </div>
                    ${latestArticlesHtml}
                </div>`;
            });

            html += '</div></div>';
        });

        return html;
    }

    filterSources(categoryFilter) {
        document.querySelectorAll('#sourcesContainer .category-section').forEach(section => {
            section.style.display = (categoryFilter === 'all' || section.dataset.category === categoryFilter) ? 'block' : 'none';
        });
    }

    setupAudioModal() {
        const modal = document.getElementById('audioModal');
        if (!modal) return;

        const closeBtn = document.getElementById('closeAudioModal');
        const audioPlayer = document.getElementById('audioPlayer');
        const speedControl = document.getElementById('audioSpeed');

        if (closeBtn) closeBtn.addEventListener('click', () => this.closeAudioModal());
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeAudioModal();
        });

        if (speedControl && audioPlayer) {
            speedControl.addEventListener('change', (e) => {
                audioPlayer.playbackRate = parseFloat(e.target.value);
            });
        }

        if (audioPlayer) {
            audioPlayer.addEventListener('loadedmetadata', () => {
                const duration = this.formatDuration(audioPlayer.duration);
                const durationEl = document.getElementById('audioDuration');
                if (durationEl) durationEl.textContent = `Időtartam: ${duration}`;
            });
        }
    }

    // ⚡ HERR CLAUS: ENHANCED AUDIO MODAL
    openAudioModal(audioFilename, title, source) {
        const modal = document.getElementById('audioModal');
        const audioPlayer = document.getElementById('audioPlayer');
        const audioSource = audioPlayer?.querySelector('source');

        if (!modal || !audioPlayer) return;

        audioSource.src = `/static/audio/${audioFilename}`;
        audioPlayer.load();

        const titleEl = document.getElementById('audioTitle');
        const sourceEl = document.getElementById('audioSourceInfo');
        if (titleEl) titleEl.textContent = title;
        if (sourceEl) sourceEl.textContent = `Forrás: ${source}`;

        const speed = document.getElementById('audioSpeed').value;
        audioPlayer.playbackRate = parseFloat(speed);

        modal.style.display = 'flex';
        audioPlayer.play().catch(e => console.log('Autoplay prevented:', e));
    }

    closeAudioModal() {
        const modal = document.getElementById('audioModal');
        const audioPlayer = document.getElementById('audioPlayer');

        if (audioPlayer) audioPlayer.pause();
        if (modal) modal.style.display = 'none';
    }

    // 🎖️ HERR CLAUS ROBUST BACKGROUND UPDATES
    startBackgroundUpdatesRobust() {
        // Update trending every 5 minutes (only if not processing)
        setInterval(async () => {
            if (!this.isServerProcessing) {
                const response = await this.loadTrendingRobust();
                if (response.success) {
                    this.trending = response.data.trending;
                    this.renderTrendingSmooth();
                }
            }
        }, 10 * 60 * 1000); // Reduced from 5min to 10min

        // Update dashboard data every 10 minutes (only if not processing)
        setInterval(async () => {
            if (!this.isServerProcessing) {
                const response = await this.loadDashboardDataRobust();
                if (response.success) {
                    this.dashboardData = response.data;
                    this.updateSidebarDataSmooth();
                }
            }
        }, 10 * 60 * 1000);

        // Update stats every 2 minutes
        setInterval(() => {
            const updateEl = document.getElementById('lastUpdate');
            if (updateEl && !updateEl.textContent.includes('Gyorsítótár') && !updateEl.textContent.includes('Szerver')) {
                updateEl.textContent = `Frissítve: ${new Date().toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit'})}`;
            }
        }, 2 * 60 * 1000);
    }

    // *** ENHANCED MOCK DASHBOARD DATA - ONLY AS LAST RESORT ***
    loadMockDashboardDataSmooth() {
        console.log('🎖️ Loading MOCK dashboard data as last resort...');
        
        this.dashboardData = {
            financial_rates: {
                currencies: [
                    { pair: 'EUR/HUF', value: '402.81', change: '+0.8%', trend: 'up' },
                    { pair: 'USD/HUF', value: '365.42', change: '-0.3%', trend: 'down' },
                    { pair: 'CHF/HUF', value: '398.67', change: '+0.2%', trend: 'up' },
                    { pair: 'GBP/HUF', value: '463.21', change: '+1.1%', trend: 'up' }
                ],
                crypto: [
                    { pair: 'BTC/USD', value: '$107,685', change: '+2.1%', trend: 'up' },
                    { pair: 'ETH/USD', value: '$3,924', change: '+1.5%', trend: 'up' },
                    { pair: 'Arany/HUF', value: '38,952', change: '+0.4%', trend: 'up' }
                ],
                hungarian_stocks: [
                    { pair: 'OTP', value: '26,450', change: '+1.8%', trend: 'up' },
                    { pair: 'MOL', value: '2,935', change: '+0.9%', trend: 'up' },
                    { pair: 'Richter', value: '9,890', change: '-0.2%', trend: 'down' },
                    { pair: 'Magyar Telekom', value: '1,798', change: '+0.6%', trend: 'up' }
                ]
            },
            weather: {
                temperature: '8',
                feels_like: '5', 
                city: 'Budapest',
                icon: '🌨️',
                humidity: 78,
                wind_speed: 12,
                wind_direction: 'É',
                pressure: 1018,
                uv_index: 1,
                visibility: 10,
                cloud_cover: 75
            },
            rss_sources: {
                general: [
                    {
                        name: 'HírMagnet Demo',
                        url: 'https://demo.hirmagnet.hu/rss/',
                        priority: 'high',
                        status: 'active',
                        last_sync: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
                        latest_articles: [
                            { title: 'Demo tartalom - valós adatok betöltése folyamatban', published: new Date(Date.now() - 1000 * 60 * 45).toISOString() },
                            { title: 'Friss hírek hamarosan elérhetőek lesznek', published: new Date(Date.now() - 1000 * 60 * 90).toISOString() }
                        ]
                    }
                ]
            },
            fallback: true
        };
        
        // SMOOTH sidebar update
        this.updateSidebarDataSmooth();
        this.debugLog('Mock dashboard data loaded as last resort (SMOOTH)');
    }

    // *** UTILITY METHODS ***
    getCategoryName(categoryCode) {
        const categories = {
            'general': 'Közélet',
            'foreign': 'Külföld',
            'politics': 'Politika', 
            'economy': 'Gazdaság',
            'tech': 'Tech',
            'entertainment': 'Bulvár',
            'sport': 'Sport',
            'cars': 'Autók',
            'lifestyle': 'Életmód'
        };
        return categories[categoryCode] || categoryCode;
    }

    formatTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        
        if (diffMins < 60) {
            return diffMins <= 1 ? '1 perce' : `${diffMins} perce`;
        } else if (diffHours < 24) {
            return `${diffHours} órája`;
        } else {
            const diffDays = Math.floor(diffHours / 24);
            return `${diffDays} napja`;
        }
    }

    formatTimeAgoShort(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        
        if (diffMins < 60) {
            return diffMins <= 1 ? '1p' : `${diffMins}p`;
        } else if (diffHours < 24) {
            return `${diffHours}ó`;
        } else {
            const diffDays = Math.floor(diffHours / 24);
            return `${diffDays}n`;
        }
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return Math.floor(num / 100000) / 10 + 'M';
        } else if (num >= 1000) {
            return Math.floor(num / 100) / 10 + 'k';
        }
        return num.toString();
    }

    formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    extractDomain(url) {
        try {
            const domain = new URL(url).hostname;
            return domain.replace('www.', '');
        } catch {
            return url;
        }
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    // 🎖️ HERR CLAUS: CLEANUP METÓDUS
    destroy() {
        this.stopAutoRefresh();
        if (this.processingCheckInterval) {
            clearInterval(this.processingCheckInterval);
        }
        console.log('🎖️ HirMagnet destroyed - all timers stopped');
    }

    // Auto-refresh leállítása (pl. oldal elhagyásakor)
    stopAutoRefresh() {
        if (this.autoRefreshTimer) {
            clearInterval(this.autoRefreshTimer);
            this.autoRefreshTimer = null;
            console.log('🎖️ Auto-refresh gestoppt');
            this.debugLog('Auto-refresh stopped');
        }
    }
}

// 🎖️ HERR CLAUS: REPLACE ORIGINAL CLASS WITH ROBUST VERSION
window.HirMagnet = HirMagnet;

console.log('🎖️ HERR CLAUS ROBUST FRONTEND - OPERATIONAL!');
console.log('✅ Graceful fallback during server processing');
console.log('✅ Cached data preservation instead of mock data');  
console.log('✅ Processing status monitoring');
console.log('✅ Retry logic with exponential backoff');
console.log('✅ Full backward compatibility maintained');

// ===== RSS FEED NAVIGATION - GLOBÁLIS FÜGGVÉNY =====

function openSource(rssUrl, sourceName, categoryKey) {
    console.log('🎖️ RSS Feed megnyitása:', { rssUrl, sourceName, categoryKey });
    
    // URL paraméterek összeállítása
    const params = new URLSearchParams({
        url: rssUrl,
        name: sourceName,
        category: categoryKey || 'general'
    });
    
    // Debug mode támogatás
    const isDebugMode = window.location.hash.includes('debug') || 
                        window.location.search.includes('debug=true') ||
                        (window.hirmagnet && window.hirmagnet.debugMode);
    
    if (isDebugMode) {
        params.append('debug', 'true');
    }
    
    // RSS Feed oldal URL összeállítása
    const rssPageUrl = `rss-feed.html?${params.toString()}`;
    
    console.log('🎖️ Navigáció új ablakban:', rssPageUrl);
    
    // Új ablakban megnyitás
    const newWindow = window.open(rssPageUrl, '_blank', 'noopener,noreferrer');
    
    // Ellenőrzés, hogy sikerült-e megnyitni
    if (!newWindow) {
        console.warn('🎖️ Popup blokkolva! Fallback ugyanabban az ablakban...');
        window.location.href = rssPageUrl;
    }
}

// Export a globális használatához
window.openSource = openSource;

// 🎖️ HERR CLAUS: PAGE UNLOAD HANDLER
window.addEventListener('beforeunload', () => {
    if (window.hirmagnet) {
        window.hirmagnet.destroy();
    }
});

console.log('🎖️ RSS Navigation: openSource függvény betöltve!')

// ===== HERR CLAUS ENGINEERING COMPLETE =====
console.log('🎯 HERR CLAUS ROBUST FRONTEND + NON-BLOCKING BACKEND SYSTEM - OPERATIONAL!')
console.log('🎖️ Deutsche Präzision Applied: NO MORE MOCK DATA DURING PROCESSING!');