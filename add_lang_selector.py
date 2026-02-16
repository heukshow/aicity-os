# Add language selector and scripts to cau chemar.html

with open('projects/Cauchemar/cauchemar.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add language selector before INQUIRY button in nav
language_selector = '''            <!-- Language Selector -->
            <div class="relative group mr-4">
                <button id="lang-btn" class="flex items-center gap-2 text-gray-400 hover:text-white transition text-sm font-bold">
                    <span id="current-lang">🇰🇷 KO</span>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                </button>
                <div id="lang-menu" class="hidden absolute right-0 mt-2 w-40 bg-black/95 border border-white/10 rounded-lg shadow-xl z-50">
                    <button data-lang="ko" class="lang-btn w-full px-4 py-2 text-left hover:bg-purple-500/20 transition flex items-center gap-2">
                        <span>🇰🇷</span> 한국어
                    </button>
                    <button data-lang="en" class="lang-btn w-full px-4 py-2 text-left hover:bg-purple-500/20 transition flex items-center gap-2">
                        <span>🇺🇸</span> English
                    </button>
                    <button data-lang="ja" class="lang-btn w-full px-4 py-2 text-left hover:bg-purple-500/20 transition flex items-center gap-2">
                        <span>🇯🇵</span> 日本語
                    </button>
                    <button data-lang="zh" class="lang-btn w-full px-4 py-2 text-left hover:bg-purple-500/20 transition flex items-center gap-2">
                        <span>🇨🇳</span> 中文
                    </button>
                    <button data-lang="es" class="lang-btn w-full px-4 py-2 text-left hover:bg-purple-500/20 transition flex items-center gap-2">
                        <span>🇪🇸</span> Español
                    </button>
                    <button data-lang="fr" class="lang-btn w-full px-4 py-2 text-left hover:bg-purple-500/20 transition flex items-center gap-2">
                        <span>🇫🇷</span> Français
                    </button>
                </div>
            </div>
            '''

# Find and insert before INQUIRY button
import re
pattern = r'(\s+<a href="inquiry\.html")'
replacement = language_selector + r'\1'
content = re.sub(pattern, replacement, content)

# Add scripts before </body>
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
        document.getElementById('lang-btn').addEventListener('click', () => {
            document.getElementById('lang-menu').classList.toggle('hidden');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.group')) {
                document.getElementById('lang-menu').classList.add('hidden');
            }
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

with open('projects/Cauchemar/cauchemar.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added language selector and scripts to cauchemar.html")
