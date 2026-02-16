# Add more spacing between navigation links and Member section
with open('projects/Cauchemar/cauchemar.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add left margin to Member section for better spacing
content = content.replace(
    '<div class="hidden sm:flex items-center gap-3 border-r border-white/10 pr-6">',
    '<div class="hidden sm:flex items-center gap-3 border-r border-white/10 pr-6 ml-8">'
)

with open('projects/Cauchemar/cauchemar.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added spacing between PARTNERSHIP and MEMBER in cauchemar.html")

# Do the same for crew.html
with open('projects/Cauchemar/crew.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<div class="flex items-center gap-4 border-r border-white/10 pr-6">',
    '<div class="flex items-center gap-3 border-r border-white/10 pr-6 ml-8">'
)

with open('projects/Cauchemar/crew.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added spacing in crew.html")
print("\n✅ Navigation spacing improved!")
