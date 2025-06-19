// ===== HIRMAGNET KÖZÖS UTILITY FÜGGVÉNYEK =====

// Közös utility függvények és konstansok
window.HirMagnetUtils = {
    // Kategóriák mapping
    categories: {
        'general': 'Közélet',
        'foreign': 'Külföld',
        'politics': 'Politika', 
        'economy': 'Gazdaság',
        'tech': 'Tech',
        'entertainment': 'Bulvár',
        'sport': 'Sport',
        'cars': 'Autók',
        'lifestyle': 'Életmód'
    },

    // Debug mode check
    isDebugMode() {
        return window.location.hash.includes('debug') || 
               window.location.search.includes('debug') ||
               new URLSearchParams(window.location.search).get('debug') === 'true';
    },

    // Debug logging
    debugLog(message, data = null) {
        if (!this.isDebugMode()) return;
        
        console.log(`🧲 DEBUG: ${message}`, data);
        
        const debugContent = document.getElementById('debugContent');
        if (debugContent) {
            const timestamp = new Date().toLocaleTimeString();
            const newLine = `${timestamp}: ${message}<br>`;
            debugContent.innerHTML = newLine + debugContent.innerHTML;
            
            // Keep only last 15 messages
            const lines = debugContent.innerHTML.split('<br>');
            if (lines.length > 15) {
                debugContent.innerHTML = lines.slice(0, 15).join('<br>');
            }
        }
    },

    // Time formatting
    formatTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 60) {
            return diffMins <= 1 ? '1 perce' : `${diffMins} perce`;
        } else if (diffHours < 24) {
            return `${diffHours} órája`;
        } else {
            return `${diffDays} napja`;
        }
    },

    // Short time format for cards
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
    },

    // Number formatting
    formatNumber(num) {
        if (num >= 1000000) {
            return Math.floor(num / 100000) / 10 + 'M';
        } else if (num >= 1000) {
            return Math.floor(num / 100) / 10 + 'k';
        }
        return num.toString();
    },

    // HTML escaping
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // Text truncation
    truncateText(text, maxLength) {
        if (!text || text.length <= maxLength) return text || '';
        return text.substring(0, maxLength) + '...';
    },

    // Category name getter
    getCategoryName(categoryCode) {
        return this.categories[categoryCode] || categoryCode;
    },

    // Duration formatting for audio
    formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    // Domain extraction from URL
    extractDomain(url) {
        try {
            const domain = new URL(url).hostname;
            return domain.replace('www.', '');
        } catch {
            return url;
        }
    },

    // Get main site URL from RSS URL
    getMainSiteUrl(rssUrl) {
        try {
            const url = new URL(rssUrl);
            return `${url.protocol}//${url.hostname}`;
        } catch {
            return rssUrl;
        }
    },

    // Strip HTML tags
    stripHtml(text) {
        const div = document.createElement('div');
        div.innerHTML = text;
        return div.textContent || div.innerText || '';
    },

    // Capitalize first letter
    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },

    // Reading time estimation
    estimateReadingTime(text) {
        const wordsPerMinute = 200;
        const wordCount = text ? text.split(' ').length : 0;
        return Math.max(1, Math.ceil(wordCount / wordsPerMinute));
    },

    // Show debug info panel
    showDebugPanel() {
        const debugEl = document.getElementById('debugInfo');
        if (debugEl && this.isDebugMode()) {
            debugEl.style.display = 'block';
            this.debugLog('Debug panel activated');
        }
    },

    // Date formatting
    formatDate(date) {
        return date.toLocaleDateString('hu-HU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Get element text safely
    getElementText(parent, tagName) {
        const element = parent.querySelector(tagName);
        return element ? element.textContent.trim() : '';
    }
};

console.log('🧲 Utils.js betöltve');