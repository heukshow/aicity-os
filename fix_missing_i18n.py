# Fix missing data-i18n attributes in cauchemar.html

with open('projects/Cauchemar/cauchemar.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix hero subtitle (it was incorrectly added before)
content = content.replace(
    'Cauchemar Crew는 15명의 정예 멤버로 구성된 제페토 크리에이터 크루입니다.\n                    공식 크리에이터 15명의 영향력과 3D 기술력으로 브랜드의 가치를 가상 세계에 구현합니다.',
    'Cauchemar has 15 world-class elite creators. Experience trusted and verified professional business solutions.'
)

# Fix the search pattern for subtitle
import re
content = re.sub(
    r'class="text-xl text-gray-400 max-w-xl leading-relaxed"(?: data-i18n="hero\.subtitle")?>\s*Cauchemar[^<]+<',
    'class="text-xl text-gray-400 max-w-xl leading-relaxed" data-i18n="hero.subtitle">Cauchemar has 15 world-class elite creators. Experience trusted and verified professional business solutions.<',
    content
)

print("✅ Fixed hero subtitle with data-i18n")
print("\n다음 단계: Expertise 섹션의 설명과 기능 목록도 수정 필요")

with open('projects/Cauchemar/cauchemar.html', 'w', encoding='utf-8') as f:
    f.write(content)
