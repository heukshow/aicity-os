# Complete inquiry.html form labels translation in one go

with open('projects/Cauchemar/inquiry.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

content = ''.join(lines)

# Add data-i18n to all form labels and elements
replacements = {
    '>COMPANY NAME<': ' data-i18n="inquiry.company_name">회사명<',
    '>YOUR NAME<': ' data-i18n="inquiry.your_name">담당자명<',
    '>EMAIL ADDRESS<': ' data-i18n="inquiry.email">이메일 주소<',
    '>TARGET SERVICE<': ' data-i18n="inquiry.target_service">문의 서비스<',
    '>MESSAGE<': ' data-i18n="inquiry.message">프로젝트 설명<',
    'placeholder="Tell us about your project..."': 'placeholder="프로젝트에 대해 알려주세요..." data-i18n-placeholder="inquiry.message_placeholder"',
    '>Send Inquiry<': ' data-i18n="inquiry.send">문의 보내기<',
    '>3D Item Collaboration<': ' data-i18n="inquiry.services.item">3D 아이템 협업<',
    '>Live Streaming<': ' data-i18n="inquiry.services.live">라이브 스트리밍<',
    '>Video Production<': ' data-i18n="inquiry.services.video">영상 제작<',
    '>World Construction<': ' data-i18n="inquiry.services.world">월드 제작<',
    '>SNS Marketing<': ' data-i18n="inquiry.services.sns">SNS 마케팅<',
    '>Brand Partnership<': ' data-i18n="inquiry.services.brand">브랜드 파트너십<',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('projects/Cauchemar/inquiry.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed inquiry.html - ALL form labels now translate")
