# Fix crew.html navigation - make login buttons visible and add Member section
with open('projects/Cauchemar/crew.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the visibility:hidden and hidden class from crew portal
content = content.replace(
    '<div id="crew-portal" class="hidden sm:flex items-center gap-4" style="visibility: hidden;">',
    '<div id="crew-portal" class="flex items-center gap-4">'
)

# Add Member login section before Crew portal
member_section = '''            <!-- Member Portal -->
            <div class="flex items-center gap-4 border-r border-white/10 pr-6 mr-2">
                <p class="text-sm uppercase tracking-[0.2em] text-purple-500 font-black">Member</p>
                <div class="flex gap-5 text-sm font-bold">
                    <a href="login_user.html" class="text-gray-400 hover:text-white transition">LOGIN</a>
                    <a href="register_user.html" class="text-gray-400 hover:text-white transition">JOIN</a>
                </div>
            </div>
            '''

# Insert Member section before Crew portal
content = content.replace(
    '<div id="crew-portal" class="flex items-center gap-4">',
    member_section + '<div id="crew-portal" class="flex items-center gap-4 mr-2">'
)

with open('projects/Cauchemar/crew.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed crew.html navigation - login buttons now visible!")
