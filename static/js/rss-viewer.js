// ===== HIRMAGNET RSS VIEWER OSZTÁLY - FIXED ERROR VERSION =====

class RSSViewer {
    constructor() {
        this.rssUrl = null;
        this.sourceName = null;
        this.sourceCategory = null;
        this.feedData = null;
        
        // Debug mode using utils
        this.debugMode = window.HirMagnetUtils.isDebugMode();
        
        this.init();
    }

    init() {
        console.log('🧲 RSS Viewer inicializálása - FIXED Enhanced Version...');
        
        if (this.debugMode) {
            window.HirMagnetUtils.showDebugPanel();
            window.HirMagnetUtils.debugLog('RSS Viewer initialized with debug mode');
        }
        
        // Get RSS parameters from URL
        this.parseUrlParameters();
        
        if (!this.rssUrl) {
            this.showError('Nincs megadva RSS URL');
            window.HirMagnetUtils.debugLog('ERROR: No RSS URL found in parameters');
            return;
        }

        window.HirMagnetUtils.debugLog(`RSS URL: ${this.rssUrl}`);
        window.HirMagnetUtils.debugLog(`Source: ${this.sourceName}`);
        window.HirMagnetUtils.debugLog(`Category: ${this.sourceCategory}`);
        
        // Setup basic UI
        this.setupBasicUI();
        
        // Load RSS feed
        this.loadRSSFeed();
        
        // Load sidebar data - ENHANCED
        this.loadSidebarData();
    }

    parseUrlParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        this.rssUrl = urlParams.get('url');
        this.sourceName = urlParams.get('name') || 'Ismeretlen forrás';
        this.sourceCategory = urlParams.get('category') || 'general';
        
        if (this.debugMode) {
            alert(`DEBUG: RSS Parameters\nURL: ${this.rssUrl}\nName: ${this.sourceName}\nCategory: ${this.sourceCategory}`);
        }
    }

    setupBasicUI() {
        // Update breadcrumb
        const breadcrumbSource = document.getElementById('breadcrumbSource');
        if (breadcrumbSource) {
            breadcrumbSource.textContent = this.sourceName;
        }

        // Update page title
        document.title = `${this.sourceName} - RSS Feed - HírMagnet`;
        
        // Set RSS title
        const rssTitle = document.getElementById('rssTitle');
        if (rssTitle) {
            rssTitle.textContent = this.sourceName;
        }

        // Set RSS URL display
        const rssUrl = document.getElementById('rssUrl');
        if (rssUrl) {
            const domain = window.HirMagnetUtils.extractDomain(this.rssUrl);
            rssUrl.textContent = domain;
        }

        // Set category
        const rssCategory = document.getElementById('rssCategory');
        if (rssCategory) {
            rssCategory.textContent = window.HirMagnetUtils.getCategoryName(this.sourceCategory);
        }

        // Set original link
        const originalLink = document.getElementById('rssOriginalLink');
        if (originalLink) {
            const mainUrl = window.HirMagnetUtils.getMainSiteUrl(this.rssUrl);
            originalLink.href = mainUrl;
        }

        // Set active category in navigation
        this.setActiveCategory();
    }

    setActiveCategory() {
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.category === this.sourceCategory) {
                tab.classList.add('active');
            }
        });
    }

    async loadRSSFeed() {
        try {
            window.HirMagnetUtils.debugLog(`Loading RSS feed: ${this.rssUrl}`);
            
            // Using a CORS proxy or server-side endpoint to fetch RSS
            const response = await this.fetchRSSFeed(this.rssUrl);
            
            if (!response.success) {
                throw new Error(response.error || 'RSS feed betöltési hiba');
            }

            this.feedData = response.data;
            
            // *** CRITICAL FIX: Check if feedData and items exist ***
            if (!this.feedData) {
                throw new Error('RSS feed data is null or undefined');
            }
            
            if (!this.feedData.items) {
                this.feedData.items = [];
                window.HirMagnetUtils.debugLog('WARNING: No items in RSS feed, using empty array');
            }
            
            window.HirMagnetUtils.debugLog(`RSS feed loaded: ${this.feedData.items.length} items`);
            
            // Render the feed
            this.renderRSSFeed();
            
        } catch (error) {
            console.error('RSS feed betöltési hiba:', error);
            window.HirMagnetUtils.debugLog(`RSS load error: ${error.message}`);
            this.showError(`RSS feed betöltési hiba: ${error.message}`);
        }
    }

    async fetchRSSFeed(url) {
        try {
            // Method 1: Try server-side RSS proxy (if available)
            const serverResponse = await fetch(`/api/rss-proxy?url=${encodeURIComponent(url)}`);
            
            if (serverResponse.ok) {
                const data = await serverResponse.json();
                return { success: true, data };
            }
            
            // Method 2: Try direct fetch (likely to fail due to CORS)
            window.HirMagnetUtils.debugLog('Server RSS proxy not available, trying direct fetch...');
            const directResponse = await fetch(url, { mode: 'cors' });
            
            if (!directResponse.ok) {
                throw new Error(`HTTP ${directResponse.status}: ${directResponse.statusText}`);
            }
            
            const text = await directResponse.text();
            const parsedData = this.parseRSSXML(text);
            return { success: true, data: parsedData };
            
        } catch (error) {
            // Method 3: Mock data for demo purposes
            window.HirMagnetUtils.debugLog('Direct fetch failed, using mock data for demo');
            return this.getMockRSSData();
        }
    }

    parseRSSXML(xmlText) {
        try {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(xmlText, 'text/xml');
            
            // Check for RSS 2.0
            let channel = xmlDoc.querySelector('rss channel');
            if (!channel) {
                // Check for Atom feed
                channel = xmlDoc.querySelector('feed');
            }
            
            if (!channel) {
                throw new Error('Invalid RSS/Atom format');
            }
            
            const title = window.HirMagnetUtils.getElementText(channel, 'title') || this.sourceName;
            const description = window.HirMagnetUtils.getElementText(channel, 'description') || '';
            const link = window.HirMagnetUtils.getElementText(channel, 'link') || '';
            
            // Parse items
            const items = [];
            const itemElements = xmlDoc.querySelectorAll('item, entry');
            
            itemElements.forEach((item, index) => {
                if (index < 50) { // Limit to 50 items
                    const itemData = {
                        title: window.HirMagnetUtils.getElementText(item, 'title') || `Cím nélkül ${index + 1}`,
                        link: window.HirMagnetUtils.getElementText(item, 'link') || '#',
                        description: window.HirMagnetUtils.getElementText(item, 'description') || window.HirMagnetUtils.getElementText(item, 'summary') || '',
                        pubDate: window.HirMagnetUtils.getElementText(item, 'pubDate') || window.HirMagnetUtils.getElementText(item, 'published') || '',
                        guid: window.HirMagnetUtils.getElementText(item, 'guid') || `item-${index}`
                    };
                    
                    // Clean up description (remove HTML tags)
                    itemData.description = window.HirMagnetUtils.stripHtml(itemData.description);
                    
                    items.push(itemData);
                }
            });
            
            return {
                title,
                description,
                link,
                items,
                lastUpdated: new Date().toISOString()
            };
            
        } catch (error) {
            throw new Error(`RSS parsing error: ${error.message}`);
        }
    }

    // *** CRITICAL FIX: Enhanced Mock Data Generator ***
    getMockRSSData() {
        console.log('🧲 Generating enhanced mock RSS data...');
        
        // Mock data for demo purposes when RSS can't be fetched
        return {
            success: true,
            data: {
                title: this.sourceName,
                description: `${this.sourceName} hírek - Demo verzió (CORS korlátok miatt élő RSS nem elérhető)`,
                link: window.HirMagnetUtils.getMainSiteUrl(this.rssUrl),
                lastUpdated: new Date().toISOString(),
                items: [
                    {
                        title: `Friss hír: ${this.sourceName} jelentése a gazdasági helyzetről`,
                        link: window.HirMagnetUtils.getMainSiteUrl(this.rssUrl) + '/hirek/gazdasag-1',
                        description: 'A legfrissebb gazdasági elemzés szerint jelentős változások várhatóak a következő negyedévben. A szakértők optimisták a jövőt illetően, különös tekintettel az inflációs mutatókra.',
                        pubDate: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 minutes ago
                        guid: 'demo-1'
                    },
                    {
                        title: `Technológiai áttörés: ${this.sourceName} exkluzív interjúja`,
                        link: window.HirMagnetUtils.getMainSiteUrl(this.rssUrl) + '/hirek/tech-2',
                        description: 'Egy úttörő technológiai fejlesztésről számolnak be a kutatók, amely forradalmasíthatja az iparágat. Az innováció különösen az energiahatékonyság terén jelenthet előrelépést.',
                        pubDate: new Date(Date.now() - 1000 * 60 * 45).toISOString(), // 45 minutes ago
                        guid: 'demo-2'
                    },
                    {
                        title: `Politikai elemzés: Mi várható a következő hónapban?`,
                        link: window.HirMagnetUtils.getMainSiteUrl(this.rssUrl) + '/hirek/politika-3',
                        description: 'A politikai szakértők szerint jelentős döntések várhatóak a közeljövőben. Az elemzők különböző forgatókönyveket vázolnak fel a lehetséges kimenetelekkel kapcsolatban.',
                        pubDate: new Date(Date.now() - 1000 * 60 * 60).toISOString(), // 1 hour ago
                        guid: 'demo-3'
                    },
                    {
                        title: `Sport hírek: Fantasztikus eredmények a hétvégén`,
                        link: window.HirMagnetUtils.getMainSiteUrl(this.rssUrl) + '/hirek/sport-4',
                        description: 'A hétvégi sportesemények rendkívül izgalmasnak bizonyultak. Számos meglepetés eredmény született, amely felkavarta a bajnokság állását.',
                        pubDate: new Date(Date.now() - 1000 * 60 * 90).toISOString(), // 1.5 hours ago
                        guid: 'demo-4'
                    },
                    {
                        title: `Kultúra: Új kiállítás nyílt a fővárosban`,
                        link: window.HirMagnetUtils.getMainSiteUrl(this.rssUrl) + '/hirek/kultura-5',
                        description: 'Egy lenyűgöző új kiállítás várja a látogatókat a főváros egyik legjelentősebb múzeumában. A tárlat egyedülálló műalkotásokat mutat be a nagyközönségnek.',
                        pubDate: new Date(Date.now() - 1000 * 60 * 120).toISOString(), // 2 hours ago
                        guid: 'demo-5'
                    },
                    {
                        title: `Időjárás: Változékony idő várható a héten`,
                        link: window.HirMagnetUtils.getMainSiteUrl(this.rssUrl) + '/hirek/idojaras-6',
                        description: 'A meteorológusok változatos időjárási feltételekre figyelmeztetnek a következő napokra vonatkozóan. Érdemes figyelemmel kísérni az előrejelzéseket.',
                        pubDate: new Date(Date.now() - 1000 * 60 * 180).toISOString(), // 3 hours ago
                        guid: 'demo-6'
                    }
                ].map(item => {
                    // Add [DEMO] prefix to titles in debug mode
                    if (this.debugMode) {
                        item.title = `[DEMO] ${item.title}`;
                    }
                    return item;
                })
            }
        };
    }

    renderRSSFeed() {
        window.HirMagnetUtils.debugLog('Rendering RSS feed');
        
        // Hide loading, show content
        const loadingContainer = document.getElementById('loadingContainer');
        const rssContainer = document.getElementById('rssContainer');
        
        if (loadingContainer) loadingContainer.style.display = 'none';
        if (rssContainer) rssContainer.style.display = 'block';

        // Set feed title if different from source name
        if (this.feedData && this.feedData.title && this.feedData.title !== this.sourceName) {
            const rssTitle = document.getElementById('rssTitle');
            if (rssTitle) {
                rssTitle.textContent = this.feedData.title;
            }
        }

        // Set description
        if (this.feedData && this.feedData.description) {
            const rssDescription = document.getElementById('rssDescription');
            const rssDescriptionText = document.getElementById('rssDescriptionText');
            if (rssDescription && rssDescriptionText) {
                rssDescriptionText.textContent = this.feedData.description;
                rssDescription.style.display = 'block';
            }
        }

        // Update stats in meta bar
        this.updateStats();

        // Render items
        this.renderRSSItems();
        
        window.HirMagnetUtils.debugLog('RSS feed rendering complete');
    }

    updateStats() {
        const itemCount = document.getElementById('rssItemCount');
        const updateTime = document.getElementById('rssUpdateTime');
        
        if (itemCount) {
            // *** CRITICAL FIX: Safe access to items length ***
            const count = (this.feedData && this.feedData.items) ? this.feedData.items.length : 0;
            itemCount.textContent = count;
        }
        
        if (updateTime) {
            updateTime.textContent = new Date().toLocaleTimeString('hu-HU', { hour: '2-digit', minute: '2-digit'});
        }
    }

    renderRSSItems() {
        const itemsList = document.getElementById('rssItemsList');
        if (!itemsList) return;
        
        itemsList.innerHTML = '';

        // *** CRITICAL FIX: Safe check for items ***
        if (!this.feedData || !this.feedData.items || this.feedData.items.length === 0) {
            itemsList.innerHTML = '<div class="no-items">📰 Nincsenek elérhető hírek ebben az RSS feedben.</div>';
            return;
        }

        this.feedData.items.forEach((item, index) => {
            const itemElement = document.createElement('div');
            itemElement.className = 'rss-item';
            
            const pubDate = item.pubDate ? new Date(item.pubDate) : null;
            const timeAgo = pubDate ? window.HirMagnetUtils.formatTimeAgo(pubDate) : 'Ismeretlen idő';
            
            // Use proper URL for external links
            const itemLink = item.link || '#';
            
            itemElement.innerHTML = `
                <div class="rss-item-header">
                    <h3 class="rss-item-title">
                        <a href="${itemLink}" target="_blank" rel="noopener noreferrer" class="rss-item-link">
                            ${window.HirMagnetUtils.escapeHtml(item.title)}
                        </a>
                    </h3>
                    <div class="rss-item-meta">
                        <span class="rss-item-time">${timeAgo}</span>
                        <span class="rss-item-source">${this.sourceName}</span>
                        <span class="rss-item-category">${window.HirMagnetUtils.getCategoryName(this.sourceCategory)}</span>
                    </div>
                </div>
                ${item.description ? `<p class="rss-item-description">${window.HirMagnetUtils.escapeHtml(window.HirMagnetUtils.truncateText(item.description, 300))}</p>` : ''}
                <div class="rss-item-actions">
                    <a href="${itemLink}" target="_blank" rel="noopener noreferrer" class="read-more-btn">
                        📖 Teljes cikk elolvasása
                    </a>
                </div>
            `;
            
            itemsList.appendChild(itemElement);
        });
    }

    // *** ENHANCED SIDEBAR SUPPORT ***
    async loadSidebarData() {
        try {
            window.HirMagnetUtils.debugLog('Loading sidebar data for RSS viewer');
            
            // Try to load real dashboard data
            const response = await fetch('/api/dashboard-data');
            
            if (response.ok) {
                const data = await response.json();
                this.updateSidebarData(data);
                window.HirMagnetUtils.debugLog('Real dashboard data loaded');
            } else {
                throw new Error('Dashboard API not available');
            }
            
            // Load trending
            const trendingResponse = await fetch('/api/trending?limit=5');
            if (trendingResponse.ok) {
                const trendingData = await trendingResponse.json();
                this.renderTrending(trendingData.trending);
                window.HirMagnetUtils.debugLog('Real trending data loaded');
            } else {
                throw new Error('Trending API not available');
            }
            
        } catch (error) {
            console.error('Sidebar data betöltési hiba:', error);
            window.HirMagnetUtils.debugLog(`Sidebar load error: ${error.message} - Using MOCK data`);
            
            // Use mock data if API is not available
            this.loadMockSidebarData();
        }
    }

    loadMockSidebarData() {
        window.HirMagnetUtils.debugLog('Loading mock sidebar data for RSS viewer');
        
        const mockData = {
            financial_rates: {
                currencies: [
                    { pair: 'EUR/HUF', value: '389.45', change: '+1.2%', trend: 'up' },
                    { pair: 'USD/HUF', value: '356.78', change: '-0.8%', trend: 'down' },
                    { pair: 'CHF/HUF', value: '392.15', change: '+0.5%', trend: 'up' }
                ],
                crypto: [
                    { pair: 'BTC/USD', value: '$43,250', change: '+2.5%', trend: 'up' },
                    { pair: 'ETH/USD', value: '$2,680', change: '+1.8%', trend: 'up' }
                ]
            },
            weather: {
                temperature: '14',
                city: 'Budapest',
                icon: '🌤️'
            }
        };
        
        this.updateSidebarData(mockData);
        
        // Mock trending data
        this.renderTrending([
            { id: 'trend-1', title: 'Trending RSS hír: Gazdasági előrejelzések', engagement_score: 1250 },
            { id: 'trend-2', title: 'Trending RSS hír: Technológiai újítások', engagement_score: 980 },
            { id: 'trend-3', title: 'Trending RSS hír: Politikai fejlemények', engagement_score: 750 }
        ]);
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
        
        if (!container || !financialData) {
            if (container) container.innerHTML = '<div style="text-align: center; color: var(--text-muted-color); padding: 1rem;">💰 Árfolyam adatok nem elérhetőek</div>';
            return;
        }

        let html = '';

        if (financialData.currencies && financialData.currencies.length > 0) {
            html += `<div class="rate-category"><h4>Deviza (HUF)</h4><ul class="rate-list">`;
            financialData.currencies.forEach(rate => {
                const trendClass = rate.trend === 'up' ? 'up' : 'down';
                const changeSign = rate.change.startsWith('+') || rate.change.startsWith('-') ? '' : (rate.trend === 'up' ? '+' : '-');
                html += `<li><span class="rate-pair">${rate.pair.replace('/HUF', '')}:</span><span class="rate-value">${rate.value}</span><span class="rate-change ${trendClass}">${changeSign}${rate.change}</span></li>`;
            });
            html += '</ul></div>';
        }

        if (financialData.crypto && financialData.crypto.length > 0) {
            html += `<div class="rate-category"><h4>Kripto / Nemesfém</h4><ul class="rate-list">`;
            financialData.crypto.forEach(rate => {
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
        
        if (!container || !weatherData) {
            if (container) container.innerHTML = `
                <div class="weather-main">
                    <span class="weather-icon-placeholder">🌦️</span>
                    <span class="weather-temp-placeholder">N/A</span>
                </div>
                <p class="weather-location">Budapest</p>
                <span class="weather-details-link">Részletek &raquo;</span>
            `;
            return;
        }

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
        if (!container || !trending) {
            if (container) container.innerHTML = '<div style="text-align: center; color: var(--text-muted-color); padding: 1rem;">📊 Trending adatok nem elérhetőek</div>';
            return;
        }
        
        container.innerHTML = '';

        trending.forEach(item => {
            const trendingItem = document.createElement('div');
            trendingItem.className = 'trending-item';
            trendingItem.onclick = () => {
                // Navigate to article view
                let url = `article-view.html?id=${item.id}`;
                if (this.debugMode) {
                    url += '&debug=true';
                }
                window.location.href = url;
            };
            
            const engagementScore = window.HirMagnetUtils.formatNumber(item.engagement_score);
            
            trendingItem.innerHTML = `
                <span>${window.HirMagnetUtils.escapeHtml(window.HirMagnetUtils.truncateText(item.title, 60))}</span>
                <span>${engagementScore}</span>
            `;
            
            container.appendChild(trendingItem);
        });
    }

    retry() {
        window.HirMagnetUtils.debugLog('Retrying RSS feed load');
        
        // Show loading, hide error
        const loadingContainer = document.getElementById('loadingContainer');
        const errorContainer = document.getElementById('errorContainer');
        const rssContainer = document.getElementById('rssContainer');
        
        if (loadingContainer) loadingContainer.style.display = 'flex';
        if (errorContainer) errorContainer.style.display = 'none';
        if (rssContainer) rssContainer.style.display = 'none';
        
        // Retry loading
        setTimeout(() => {
            this.loadRSSFeed();
        }, 500);
    }

    showError(message) {
        window.HirMagnetUtils.debugLog(`Showing error: ${message}`);
        
        const loadingContainer = document.getElementById('loadingContainer');
        const rssContainer = document.getElementById('rssContainer');
        const errorContainer = document.getElementById('errorContainer');
        const errorMessage = document.getElementById('errorMessage');
        
        if (loadingContainer) loadingContainer.style.display = 'none';
        if (rssContainer) rssContainer.style.display = 'none';
        if (errorContainer) errorContainer.style.display = 'flex';
        if (errorMessage) errorMessage.textContent = message;
    }
}

// Export to global
window.RSSViewer = RSSViewer;

console.log('🧲 RSSViewer FIXED Class betöltve - Length error resolved!');