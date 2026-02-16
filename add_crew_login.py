# Add login buttons to crew.html navigation
with open('projects/Cauchemar/crew.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the navigation section and add login buttons before the INQUIRY button
import re

# Pattern to find right before the INQUIRY button in crew.html
pattern = r'(<!-- Crew Portal Visibility -->)'

login_section = '''<!-- Member & Crew Login -->
            <div class="hidden sm:flex items-center gap-4 border-r border-white/10 pr-6 mr-2">
                <p class="text-sm uppercase tracking-[0.2em] text-purple-500 font-black">Member</p>
                <div class="flex gap-5 text-sm font-bold">
                    <a href="login_user.html" class="text-gray-400 hover:text-white transition">LOGIN</a>
                </div>
            </div>
            <div class="hidden sm:flex items-center gap-4 mr-2">
                <p class="text-sm uppercase tracking-[0.2em] text-purple-400 font-black">Crew</p>
                <div class="flex gap-5 text-sm font-bold">
                    <a href="login.html" class="text-gray-400 hover:text-white transition">LOGIN</a>
                </div>
            </div>
            
            <!-- Crew Portal Visibility -->'''

if pattern in content:
    content = re.sub(pattern, login_section, content)
    
    with open('projects/Cauchemar/crew.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added login buttons to crew.html navigation!")
else:
    print("❌ Pattern not found in crew.html")
    print("Looking for alternative pattern...")
    
    # Try alternative pattern - look for the nav section
    alt_pattern = r'(<div class="flex items-center gap-6">.*?)(<!-- Crew Portal Visibility -->)'
    
    if re.search(alt_pattern, content, re.DOTALL):
        content = re.sub(alt_pattern, r'\1' + login_section, content, flags=re.DOTALL)
        
        with open('projects/Cauchemar/crew.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Added login buttons to crew.html navigation (alternative method)!")
    else:
        print("❌ Alternative pattern also not found")
