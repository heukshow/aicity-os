// Translation Engine
class I18n {
    constructor(translations) {
        this.translations = translations;
        this.currentLang = 'ko';
    }

    // Set current language
    setLanguage(lang) {
        this.currentLang = lang;
        this.updatePageContent();
        this.updateLanguageSelector();
        document.documentElement.lang = lang;
    }

    // Get translation by key path (e.g., 'nav.crew')
    t(keyPath) {
        const keys = keyPath.split('.');
        let value = this.translations[this.currentLang];

        for (const key of keys) {
            value = value?.[key];
            if (value === undefined) break;
        }

        return value || keyPath;
    }

    // Update all elements with data-i18n attribute
    updatePageContent() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);

            // Check if it's a placeholder
            if (element.hasAttribute('placeholder')) {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        });
    }

    // Update language selector buttons
    updateLanguageSelector() {
        document.querySelectorAll('.lang-btn').forEach(btn => {
            const lang = btn.getAttribute('data-lang');
            if (lang === this.currentLang) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // Initialize with auto-detected language
    async init() {
        const detector = new LanguageDetector();
        const detectedLang = await detector.detectLanguage();
        this.setLanguage(detectedLang);
    }
}
