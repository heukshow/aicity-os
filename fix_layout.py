# Fix the cauchemar.html by removing duplicate cards and fixing structure
with open('projects/Cauchemar/cauchemar.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the incorrectly added section (SNS Marketing and Brand Partnership that appear to be in wrong place)
# Find and remove the duplicate cards section
import re

# Pattern to find the incorrectly placed cards
pattern = r'                <!-- SNS 마케팅 \(NEW\) -->.*?<!-- 브랜드 협업 \(NEW\) -->.*?</div>\s+</div>\s+</div>\s+</section>'

content = re.sub(pattern, '            </div>\n        </div>\n    </section>', content, flags=re.DOTALL)

with open('projects/Cauchemar/cauchemar.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Removed duplicate cards")
