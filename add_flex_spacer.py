# Add flex-1 spacer between navigation links and login sections
with open('projects/Cauchemar/cauchemar.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the opening div of the navigation items container
# Add a flex-1 spacer div after PARTNERSHIP link
import re

# Find the section with gap-8 navigation links and add flex-1 after
pattern = r'(<div class="hidden lg:flex gap-8 text-sm font-semibold text-gray-400 flex-1">.*?</div>)'
replacement = r'\1\n        <div class="flex-1"></div>'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Also remove the ml-8 since we're using flex-1 now
content = content.replace(' ml-8">', '">')

with open('projects/Cauchemar/cauchemar.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added flex-1 spacer in cauchemar.html")

# Do the same for crew.html
with open('projects/Cauchemar/crew.html', 'r', encoding='utf-8') as f:
    content = f.read()

# For crew.html, add flex-1 after the navigation links div
pattern = r'(<div class="hidden lg:flex gap-8 text-sm font-semibold text-gray-400">.*?</div>)'
replacement = r'\1\n        <div class="flex-1"></div>'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Remove ml-8
content = content.replace(' ml-8">', '">')

with open('projects/Cauchemar/crew.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added flex-1 spacer in crew.html")
print("\n✅ Navigation sections now clearly separated!")
