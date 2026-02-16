# Apply language system to ALL remaining pages at once

import shutil

# List of pages to update
pages = ['services.html', 'portfolio.html', 'crew.html']

for page in pages:
    filepath = f'projects/Cauchemar/{page}'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already has language scripts
        if 'js/translations.js' in content:
            print(f"⏭️  {page} already has language system")
            continue
        
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
        const langBtn = document.getElementById('lang-btn');
        const langMenu = document.getElementById('lang-menu');
        
        if (langBtn && langMenu) {
            langBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                langMenu.classList.toggle('hidden');
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', () => {
                langMenu.classList.add('hidden');
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
                    langMenu.classList.add('hidden');
                });
            });
        }
    </script>
'''
        
        content = content.replace('</body>', scripts + '\n</body>')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Added language system to {page}")
        
    except FileNotFoundError:
        print(f"⚠️  {page} not found, skipping")

print("\n✅ Language system applied to all pages!")
