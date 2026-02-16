# Remove flex-1 spacer and use moderate fixed margin instead
import re

with open('projects/Cauchemar/cauchemar.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the flex-1 spacer div we added
content = re.sub(r'\s*<div class="flex-1"></div>\s*', '\n', content)

# Add moderate margin (ml-16) to Member section - not too much, not too little
content = content.replace(
    '<div class="hidden sm:flex items-center gap-3 border-r border-white/10 pr-6">',
    '<div class="hidden sm:flex items-center gap-3 border-r border-white/10 pr-6 ml-16">'
)

with open('projects/Cauchemar/cauchemar.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed spacing in cauchemar.html (moderate margin)")

# Do the same for crew.html
with open('projects/Cauchemar/crew.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'\s*<div class="flex-1"></div>\s*', '\n', content)

content = content.replace(
    '<div class="flex items-center gap-3 border-r border-white/10 pr-6">',
    '<div class="flex items-center gap-3 border-r border-white/10 pr-6 ml-16">'
)

with open('projects/Cauchemar/crew.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed spacing in crew.html (moderate margin)")
print("\n✅ Balanced navigation spacing achieved!")
