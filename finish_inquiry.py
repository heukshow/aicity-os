# Quick script to finish inquiry.html

with open('projects/Cauchemar/inquiry.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add language scripts before </body>
scripts = '''
    <!-- Language System -->
    <script src="js/translations.js"></script>
    <script src="js/languageDetector.js"></script>
    <script src="js/i18n.js"></script>
    <script>
        // Initialize i18n
        const i18n = new I18n(translations);
        i18n.init();
        
        // Language selector toggle
        document.getElementById('lang-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            document.getElementById('lang-menu').classList.toggle('hidden');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', () => {
            document.getElementById('lang-menu').classList.add('hidden');
        });
        
        // Language selection
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const lang = btn.getAttribute('data-lang');
                i18n.setLanguage(lang);
                languageDetector.saveLanguage(lang);
                
                // Update button text
                const flags = { ko: '🇰🇷 KO', en: '🇺🇸 EN', ja: '🇯🇵 JA', zh: '🇨🇳 ZH', es: '🇪🇸 ES', fr: '🇫🇷 FR' };
                document.getElementById('current-lang').textContent = flags[lang];
                document.getElementById('lang-menu').classList.add('hidden');
            });
        });
    </script>
'''

content = content.replace('</body>', scripts + '\n</body>')

with open('projects/Cauchemar/inquiry.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added language system to inquiry.html")
print("🔄 Test: http://localhost:8000/inquiry.html")
