# Add data-i18n to all expertise section descriptions and features

with open('projects/Cauchemar/cauchemar.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We need to find each expertise card and add data-i18n to:
# 1. Description paragraphs (<p class="text-gray-400">)
# 2. Feature list items (<li>)

# Map for easier replacement
replacements = [
    # 3D Item Production
    ('의상(상/하의), 신발, 헤어, 액세서리, 체형 등 제페토 내부에서 착용 가능한 모든 3D 아이템을 고퀄리티로 제작합니다.', 
     ' data-i18n="expertise.item_desc">의상(상/하의), 신발, 헤어, 액세서리, 체형 등 제페토 내부에서 착용 가능한 모든 3D 아이템을 고퀄리티로 제작합니다.'),
    
    # Live Streaming & PPL  
    ('제페토 공식 라이브 크리에이터들이 방송 중 브랜드 아이템을 착용하거나 직접 소개하여 실시간 소통 마케팅을 진행합니다.',
     ' data-i18n="expertise.live_desc">제페토 공식 라이브 크리에이터들이 방송 중 브랜드 아이템을 착용하거나 직접 소개하여 실시간 소통 마케팅을 진행합니다.'),
    
    # Video Creative
    ('영상 전문 크리에이터들이 브랜드 스토리를 담은 숏폼 콘텐츠를 제작하여 제페토 피드 및 외부 채널 확산을 이끕니다.',
     ' data-i18n="expertise.video_desc">영상 전문 크리에이터들이 브랜드 스토리를 담은 숏폼 콘텐츠를 제작하여 제페토 피드 및 외부 채널 확산을 이끕니다.'),
    
    # World Construction
    ('브랜드의 아이덴티티를 담은 몰입형 메타버스 월드를 기획하고 제작합니다. 단순한 공간을 넘어 유저 경험(UX) 중심의 가상 공간을',
     ' data-i18n="expertise.world_desc">브랜드의 아이덴티티를 담은 몰입형 메타버스 월드를 기획하고 제작합니다. 단순한 공간을 넘어 유저 경험(UX) 중심의 가상 공간을'),
    
    # SNS Marketing
    ('Instagram, 틱톡, YouTube 등 주요 SNS 채널을 통해 제페토 작품을 홍보하고 바이럴 마케팅을 진행합니다.',
     ' data-i18n="expertise.sns_desc">Instagram, 틱톡, YouTube 등 주요 SNS 채널을 통해 제페토 작품을 홍보하고 바이럴 마케팅을 진행합니다.'),
]

content = ''.join(lines)

for old, new in replacements:
    content = content.replace('>' + old, new)

with open('projects/Cauchemar/cauchemar.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added data-i18n to expertise descriptions")
print("   Now page should fully translate!")
print("\n🔄 Refresh http://localhost:8000/cauchemar.html")
