// ===== HIRMAGNET ALKALMAZÁS INICIALIZÁLÁS - JAVÍTOTT VERZIÓ + CACHE BUSTER =====

// 🧲 HERR CLAUS CACHE BUSTER KONSTANS
const CACHE_VERSION = '202506161200';
const CACHE_TIMESTAMP = Date.now();

// 🧲 CACHE BUSTER UTILITY FÜGGVÉNYEK
function addCacheBuster(url) {
    // Deutsche Präzision Cache Buster - minden URL-hez
    const separator = url.includes('?') ? '&' : '?';
    return `${url}${separator}v=${CACHE_VERSION}&t=${CACHE_TIMESTAMP}`;
}

function addDynamicCacheBuster(url) {
    // Dinamikus cache buster real-time timestamp-tel
    const separator = url.includes('?') ? '&' : '?';
    return `${url}${separator}v=${CACHE_VERSION}&cb=${Date.now()}`;
}

// Globális függvények (backward compatibility)
function scrollToFeeds() {
    const feedsSection = document.getElementById('feedsSection');
    if (feedsSection) {
        feedsSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

function showPremium() {
    alert('🚀 Premium funkció hamarosan elérhető!');
}

// *** KRITIKUS JAVÍTÁS: openSource függvény RSS-feed.html-re navigál + CACHE BUSTER ***
function openSource(url, sourceName, sourceCategory) {
    console.log('🧲 RSS Feed megnyitása (CACHE BUSTER):', { url, sourceName, sourceCategory });
    
    // URL paraméterek összeállítása
    const params = new URLSearchParams({
        url: url,
        name: sourceName || 'RSS Feed',
        category: sourceCategory || 'general'
    });
    
    // Debug mode támogatás
    const isDebugMode = window.location.hash.includes('debug') || 
                        window.location.search.includes('debug=true') ||
                        (window.hirmagnet && window.hirmagnet.debugMode);
    
    if (isDebugMode) {
        params.append('debug', 'true');
    }
    
    // 🧲 HERR CLAUS CACHE BUSTER hozzáadása
    params.append('v', CACHE_VERSION);
    params.append('cb', Date.now().toString());
    
    // RSS Feed oldal URL összeállítása CACHE BUSTER-rel
    const rssPageUrl = `rss-feed.html?${params.toString()}`;
    
    console.log('🧲 Navigáció új ablakban (CACHE BUSTER):', rssPageUrl);
    
    // Cache buster megerősítés debug módban
    if (isDebugMode) {
        const confirmed = confirm(`🧲 CACHE BUSTER NAVIGATION\n\nURL: ${rssPageUrl}\nCache Version: ${CACHE_VERSION}\nTimestamp: ${Date.now()}\n\nFolytassuk?`);
        if (!confirmed) {
            console.log('🧲 Navigation cancelled by user (debug mode)');
            return;
        }
    }
    
    // Új ablakban megnyitás
    const newWindow = window.open(rssPageUrl, '_blank', 'noopener,noreferrer');
    
    // Ellenőrzés, hogy sikerült-e megnyitni
    if (!newWindow) {
        console.warn('🧲 Popup blokkolva! Fallback ugyanabban az ablakban...');
        // Fallback is cache buster-rel
        window.location.href = rssPageUrl;
    }
}

// 🧲 ENHANCED NAVIGATION FÜGGVÉNYEK - CACHE BUSTER-rel
function navigateWithCacheBuster(path, params = {}) {
    // Általános navigáció cache buster-rel
    
    // Alapértelmezett cache buster paraméterek hozzáadása
    params.v = CACHE_VERSION;
    params.cb = Date.now();
    
    const urlParams = new URLSearchParams(params);
    const finalUrl = `${path}?${urlParams.toString()}`;
    
    console.log(`🧲 Cache buster navigation: ${finalUrl}`);
    
    // Navigate
    window.location.href = finalUrl;
}

function navigateToArticle(articleId, debugMode = false) {
    // Cikk navigáció cache buster-rel
    const params = { id: articleId };
    
    if (debugMode) {
        params.debug = 'true';
    }
    
    navigateWithCacheBuster('article-view.html', params);
}

function navigateToHome(category = null) {
    // Főoldal navigáció cache buster-rel
    const params = {};
    
    if (category && category !== 'all') {
        params.category = category;
    }
    
    navigateWithCacheBuster('index.html', params);
}

// Háttér animáció
function startBackgroundAnimation() {
    let currentBg = 1;
    setInterval(() => {
        document.body.className = currentBg === 1 ? 'bg-alternate' : '';
        currentBg = currentBg === 1 ? 2 : 1;
    }, 15000);
}

// Oldal típus felismerés
function detectPageType() {
    const currentPath = window.location.pathname;
    
    if (currentPath.includes('rss-feed.html')) {
        return 'rss';
    } else if (currentPath.includes('article-view.html')) {
        return 'article';
    } else {
        return 'index';
    }
}

// 🧲 CACHE BUSTER VERIFICATION
function verifyCacheBuster() {
    // Cache buster működés ellenőrzése
    const urlParams = new URLSearchParams(window.location.search);
    const versionParam = urlParams.get('v');
    const timestampParam = urlParams.get('cb') || urlParams.get('t');
    
    const cacheStatus = {
        hasVersion: !!versionParam,
        hasTimestamp: !!timestampParam,
        version: versionParam,
        timestamp: timestampParam,
        currentVersion: CACHE_VERSION,
        isLatestVersion: versionParam === CACHE_VERSION
    };
    
    console.log('🧲 Cache Buster Status:', cacheStatus);
    
    return cacheStatus;
}

// Alkalmazás inicializálás
function initializeApp() {
    const pageType = detectPageType();
    const isDebug = window.HirMagnetUtils?.isDebugMode() || false;
    
    // 🧲 Cache buster verification
    const cacheStatus = verifyCacheBuster();
    
    console.log(`🧲 Oldal típus: ${pageType}`);
    console.log(`🧲 Cache Version: ${CACHE_VERSION}`);
    console.log(`🧲 Cache Status:`, cacheStatus);
    
    if (isDebug) {
        window.HirMagnetUtils.debugLog(`Page type detected: ${pageType}`);
        window.HirMagnetUtils.debugLog(`Cache version: ${CACHE_VERSION}`);
        window.HirMagnetUtils.debugLog(`Cache status: ${JSON.stringify(cacheStatus)}`);
    }
    
    switch (pageType) {
        case 'rss':
            // RSS Feed oldal
            window.rssViewer = new RSSViewer();
            
            if (isDebug) {
                console.log(`
🧲 RSS Viewer DEBUG MODE ACTIVATED + CACHE BUSTER! 🧲

Debug features enabled:
✅ URL parameter extraction verification
✅ RSS feed loading confirmation 
✅ Enhanced API response logging  
✅ Debug info panel (top-right corner)
✅ Mock data fallback for CORS issues
✅ Sidebar widgets support
✅ CACHE BUSTER: Version ${CACHE_VERSION}

Debug info:
• Current URL: ${window.location.href}
• RSS URL: ${window.rssViewer?.rssUrl || 'Not detected'}
• Source Name: ${window.rssViewer?.sourceName || 'Not detected'}
• Category: ${window.rssViewer?.sourceCategory || 'general'}
• Cache Version: ${cacheStatus.version || 'NONE'}
• Is Latest: ${cacheStatus.isLatestVersion ? 'YES' : 'NO'}
• Debug panel visible in top-right corner

To disable debug mode, remove 'debug' from URL
                `);
            } else {
                console.log(`
🧲 RSS Viewer Loaded Successfully + CACHE BUSTER! 🧲

Current RSS Source: ${window.rssViewer?.sourceName || 'Not detected'}
RSS URL: ${window.rssViewer?.rssUrl || 'Not detected'}
Category: ${window.rssViewer?.sourceCategory || 'general'}
Cache Version: ${CACHE_VERSION}
Cache Status: ${cacheStatus.isLatestVersion ? 'LATEST' : 'OUTDATED'}
To enable debug mode, add '&debug=true' to the URL
                `);
            }
            break;
            
        case 'article':
            // Cikk oldal
            window.articleViewer = new ArticleViewer();
            
            if (isDebug) {
                console.log(`
🧲 ArticleViewer DEBUG MODE ACTIVATED + CACHE BUSTER! 🧲

Debug features enabled:
✅ URL parameter extraction verification
✅ Article loading confirmation dialogs
✅ Enhanced API response logging  
✅ Debug info panel (top-right corner)
✅ Wrong article detection alerts
✅ CACHE BUSTER: Version ${CACHE_VERSION}

Debug info:
• Current URL: ${window.location.href}
• Article ID: ${window.articleViewer?.articleId || 'Not detected'}
• Cache Version: ${cacheStatus.version || 'NONE'}
• Is Latest: ${cacheStatus.isLatestVersion ? 'YES' : 'NO'}
• Debug panel visible in top-right corner

To disable debug mode, remove 'debug' from URL
                `);
            } else {
                console.log(`
🧲 ArticleViewer Loaded Successfully + CACHE BUSTER! 🧲

Current Article ID: ${window.articleViewer?.articleId || 'Not detected'}
Cache Version: ${CACHE_VERSION}
Cache Status: ${cacheStatus.isLatestVersion ? 'LATEST' : 'OUTDATED'}
To enable debug mode, add '&debug=true' to the URL
                `);
            }
            break;
            
        case 'index':
        default:
            // Főoldal
            window.hirmagnet = new HirMagnet();
            
            if (isDebug) {
                console.log(`
🧲 HírMagnet DEBUG MODE ACTIVATED + CACHE BUSTER! 🧲

Debug features enabled:
✅ Article ID verification alerts
✅ Navigation confirmation dialogs  
✅ Enhanced console logging
✅ Debug info panel (top-right corner)
✅ Article IDs shown in titles
✅ RSS Widget mock data support
✅ Auto-refresh Panzer (30s interval)
✅ CACHE BUSTER: Version ${CACHE_VERSION}

How to use:
- Click any article to see debug navigation dialog
- Check console for detailed logs
- Debug info panel shows real-time events
- Article titles show [ID:xxx] prefix
- RSS sources load with mock data if server unavailable
- Auto-refresh triggers every 30 seconds
- Cache version: ${CACHE_VERSION}
- Cache status: ${cacheStatus.isLatestVersion ? 'LATEST' : 'OUTDATED'}

To disable debug mode, remove 'debug' from URL
                `);
            } else {
                console.log(`
🧲 HírMagnet Loaded Successfully + CACHE BUSTER! 🧲

Features:
✅ RSS Sources widget support
✅ Mock data fallback for development
✅ Enhanced navigation system
✅ Auto-refresh Panzer (30 seconds)
✅ Cache Buster Version: ${CACHE_VERSION}

Cache Status: ${cacheStatus.isLatestVersion ? 'LATEST' : 'OUTDATED'}
To enable debug mode, add '#debug' to the URL
Example: ${window.location.href}#debug
                `);
            }
            break;
    }
    
    // Indítsd a háttér animációt
    startBackgroundAnimation();
    
    // Debug info
    if (isDebug) {
        window.HirMagnetUtils?.debugLog(`App initialized for ${pageType} page with cache version ${CACHE_VERSION}`);
    }
    
    // 🧲 CACHE BUSTER WARNING ha elavult
    if (!cacheStatus.isLatestVersion && cacheStatus.hasVersion) {
        console.warn(`🧲 CACHE VERSION MISMATCH! Current: ${cacheStatus.version}, Expected: ${CACHE_VERSION}`);
        
        if (isDebug) {
            alert(`🧲 CACHE VERSION WARNING!\n\nFound: ${cacheStatus.version}\nExpected: ${CACHE_VERSION}\n\nPage may have cached content!`);
        }
    }
}

// Fájlok betöltődésének ellenőrzése
function checkDependencies() {
    const required = ['HirMagnetUtils'];
    const missing = [];
    
    required.forEach(dep => {
        if (!window[dep]) {
            missing.push(dep);
        }
    });
    
    if (missing.length > 0) {
        console.error('🚨 Hiányzó függőségek:', missing);
        alert(`Hiba: Hiányzó JavaScript fájlok!\n\nHiányzó: ${missing.join(', ')}\n\nEllenőrizd, hogy minden JS fájl be van-e töltve!`);
        return false;
    }
    
    return true;
}

// 🧲 GLOBAL CACHE BUSTER FUNCTIONS - Export
window.addCacheBuster = addCacheBuster;
window.addDynamicCacheBuster = addDynamicCacheBuster;
window.navigateWithCacheBuster = navigateWithCacheBuster;
window.navigateToArticle = navigateToArticle;
window.navigateToHome = navigateToHome;
window.verifyCacheBuster = verifyCacheBuster;
window.CACHE_VERSION = CACHE_VERSION;

// DOM betöltődés után inicializálás
document.addEventListener('DOMContentLoaded', () => {
    console.log('🧲 DOM betöltődött, alkalmazás inicializálása CACHE BUSTER-rel...');
    console.log(`🧲 Cache Version: ${CACHE_VERSION}`);
    
    // Ellenőrizd a függőségeket
    if (!checkDependencies()) {
        return;
    }
    
    // Kis késleltetés, hogy minden biztosan betöltődjön
    setTimeout(() => {
        try {
            initializeApp();
            console.log('🧲 HírMagnet Moduláris Rendszer Ready! - Enhanced RSS Support + Cache Buster');
            console.log(`🎯 Cache Buster Version: ${CACHE_VERSION} - Deutsche Präzision!`);
        } catch (error) {
            console.error('🚨 Inicializálási hiba:', error);
            alert(`Inicializálási hiba: ${error.message}`);
        }
    }, 100);
});

// Hiba kezelés
window.addEventListener('error', (event) => {
    console.error('🚨 JavaScript hiba:', event.error);
    
    if (window.HirMagnetUtils && window.HirMagnetUtils.isDebugMode()) {
        window.HirMagnetUtils.debugLog(`Global error: ${event.error?.message || 'Unknown error'}`);
    }
});

// Unhandled promise rejection kezelés
window.addEventListener('unhandledrejection', (event) => {
    console.error('🚨 Unhandled promise rejection:', event.reason);
    
    if (window.HirMagnetUtils && window.HirMagnetUtils.isDebugMode()) {
        window.HirMagnetUtils.debugLog(`Unhandled promise rejection: ${event.reason}`);
    }
});

// 🧲 PAGE VISIBILITY CACHE REFRESH
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // User visszatért az oldalra - ellenőrizzük a cache statuszt
        const cacheStatus = verifyCacheBuster();
        
        if (!cacheStatus.isLatestVersion) {
            console.log('🧲 Page returned with outdated cache - considering refresh...');
            
            // Csak debug módban auto-refresh
            if (window.HirMagnetUtils?.isDebugMode()) {
                const shouldRefresh = confirm('🧲 CACHE VERSION OUTDATED!\n\nCurrent page may have cached content.\nRefresh page with latest cache buster?\n\nOK = Refresh, Cancel = Continue');
                
                if (shouldRefresh) {
                    const currentUrl = new URL(window.location);
                    currentUrl.searchParams.set('v', CACHE_VERSION);
                    currentUrl.searchParams.set('cb', Date.now());
                    window.location.href = currentUrl.toString();
                }
            }
        }
    }
});

console.log('🧲 App.js betöltve - Ready for initialization! - Enhanced RSS & openSource support + Deutsche Präzision Cache Buster!');
console.log(`🎖️ Cache Buster Version: ${CACHE_VERSION}`);
console.log(`🚀 Timestamp: ${CACHE_TIMESTAMP}`);