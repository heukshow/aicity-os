# Fix navigation spacing on all pages
import os

files = [
    'projects/Cauchemar/cauchemar.html',
    'projects/Cauchemar/crew.html',
]

# Better spacing structure for navigation
for filepath in files:
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix spacing - add proper gaps and padding
    # Replace cramped Member section
    content = content.replace(
        '<div class="flex items-center gap-4 border-r border-white/10 pr-6 mr-2">',
        '<div class="hidden sm:flex items-center gap-3 border-r border-white/10 pr-6">'
    )
    
    # Fix Crew section spacing  
    content = content.replace(
        '<div class="flex items-center gap-4 mr-2">',
        '<div class="hidden sm:flex items-center gap-3 pl-6">'
    )
    
    # Ensure proper gap between buttons
    content = content.replace(
        '<div class="flex gap-5 text-sm font-bold">',
        '<div class="flex gap-4 text-sm font-bold">'
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed spacing in {filepath}")

print("\n✅ Navigation spacing updated!")
