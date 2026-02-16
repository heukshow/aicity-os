# Add login buttons to navigation bars
import re

files_to_update = [
    'projects/Cauchemar/services.html',
    'projects/Cauchemar/portfolio.html',
    'projects/Cauchemar/inquiry.html'
]

login_buttons_html = '''
                    <!-- Member Login -->
                    <div class="hidden sm:flex items-center gap-2 border-l border-white/10 pl-4">
                        <span class="text-xs text-purple-400 font-bold">MEMBER</span>
                        <a href="/login_user.html" class="text-xs text-gray-400 hover:text-white transition">LOGIN</a>
                    </div>
                    
                    <!-- Crew Login -->
                    <div class="hidden sm:flex items-center gap-2 border-l border-white/10 pl-4">
                        <span class="text-xs text-purple-400 font-bold">CREW</span>
                        <a href="/login.html" class="text-xs text-gray-400 hover:text-white transition">LOGIN</a>
                    </div>
                    '''

for filepath in files_to_update:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the inquiry button and insert login buttons before it
        pattern = r'(\s+<a href="/inquiry\.html"[^>]*>)'
        
        if re.search(pattern, content):
            content = re.sub(pattern, login_buttons_html + r'\1', content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated {filepath}")
        else:
            print(f"⚠️  Pattern not found in {filepath}")
            
    except FileNotFoundError:
        print(f"⚠️  File not found: {filepath}")
    except Exception as e:
        print(f"❌ Error with {filepath}: {e}")

print("\n✅ Navigation update complete!")
