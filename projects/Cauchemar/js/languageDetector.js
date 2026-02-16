// Language Detection and Auto-switch System
class LanguageDetector {
    constructor() {
        this.defaultLang = 'ko';
        this.supportedLangs = ['ko', 'en', 'ja', 'zh', 'es', 'fr'];
        this.countryLangMap = {
            'KR': 'ko', 'US': 'en', 'GB': 'en', 'CA': 'en', 'AU': 'en',
            'JP': 'ja', 'CN': 'zh', 'TW': 'zh', 'HK': 'zh',
            'ES': 'es', 'MX': 'es', 'AR': 'es', 'CO': 'es',
            'FR': 'fr', 'BE': 'fr', 'CH': 'fr'
        };
    }

    // Get saved language preference
    getSavedLanguage() {
        return localStorage.getItem('preferred_language');
    }

    // Save language preference
    saveLanguage(lang) {
        localStorage.setItem('preferred_language', lang);
    }

    // Get browser language
    getBrowserLanguage() {
        const browserLang = navigator.language || navigator.userLanguage;
        const langCode = browserLang.split('-')[0]; // 'en-US' -> 'en'
        return this.supportedLangs.includes(langCode) ? langCode : null;
    }

    // Fetch IP-based location
    async getIPLocation() {
        try {
            const response = await fetch('https://ipapi.co/json/');
            const data = await response.json();
            return data.country_code;
        } catch (error) {
            console.warn('IP geolocation failed:', error);
            return null;
        }
    }

    // Map country to language
    getLanguageFromCountry(countryCode) {
        return this.countryLangMap[countryCode] || this.defaultLang;
    }

    // Detect language with priority
    async detectLanguage() {
        // 1. Check saved preference
        const saved = this.getSavedLanguage();
        if (saved && this.supportedLangs.includes(saved)) {
            console.log('Using saved language:', saved);
            return saved;
        }

        // 2. Check browser language
        const browserLang = this.getBrowserLanguage();
        if (browserLang) {
            console.log('Using browser language:', browserLang);
            this.saveLanguage(browserLang);
            return browserLang;
        }

        // 3. IP-based detection
        const countryCode = await this.getIPLocation();
        if (countryCode) {
            const lang = this.getLanguageFromCountry(countryCode);
            console.log('Using IP-based language:', lang, 'from country:', countryCode);
            this.saveLanguage(lang);
            return lang;
        }

        // 4. Fallback to default
        console.log('Using default language:', this.defaultLang);
        return this.defaultLang;
    }
}

// Initialize on page load
const languageDetector = new LanguageDetector();
