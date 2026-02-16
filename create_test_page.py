# Create simple debug test page

html_debug = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Language System Test</title>
    <script src="js/translations.js"></script>
    <script src="js/languageDetector.js"></script>
    <script src="js/i18n.js"></script>
</head>
<body style="font-family: sans-serif; padding: 40px; background: #111; color: white;">
    <h1>Language System Debug</h1>
    
    <div style="margin: 20px 0;">
        <h2>Language Selector:</h2>
        <button onclick="changeLanguage('ko')">한국어</button>
        <button onclick="changeLanguage('en')">English</button>
        <button onclick="changeLanguage('ja')">日本語</button>
    </div>
    
    <div style="margin: 20px 0; padding: 20px; background: #222; border-radius: 10px;">
        <h2>Test Content:</h2>
        <p data-i18n="nav.crew">Navigation Text</p>
        <p data-i18n="hero.subtitle">Hero Subtitle</p>
        <p data-i18n="hero.cta_inquiry">CTA Button</p>
    </div>
    
    <div style="margin: 20px 0;">
        <h2>Debug Info:</h2>
        <pre id="debug"></pre>
    </div>
    
    <script>
        // Initialize
        const i18n = new I18n(translations);
        const detector = new LanguageDetector();
        
        async function init() {
            const lang = await detector.detectLanguage();
            console.log('Detected language:', lang);
            i18n.setLanguage(lang);
            updateDebug();
        }
        
        function changeLanguage(lang) {
            console.log('Changing to:', lang);
            i18n.setLanguage(lang);
            detector.saveLanguage(lang);
            updateDebug();
        }
        
        function updateDebug() {
            const debug = document.getElementById('debug');
            debug.textContent = `Current Language: ${i18n.currentLang}\\n`;
            debug.textContent += `Saved Language: ${localStorage.getItem('preferred_language')}\\n`;
            debug.textContent += `Translation loaded: ${typeof translations !== 'undefined'}\\n`;
            debug.textContent += `Available langs: ${Object.keys(translations).join(', ')}`;
        }
        
        init();
    </script>
</body>
</html>
'''

with open('projects/Cauchemar/test_lang.html', 'w', encoding='utf-8') as f:
    f.write(html_debug)

print("✅ Created test_lang.html")
print("📍 Open: http://localhost:8000/test_lang.html")
print("   테스트 페이지로 언어 시스템 동작 확인 가능!")
