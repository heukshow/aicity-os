# Add data-i18n attributes to cauchemar.html

with open('projects/Cauchemar/cauchemar.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Navigation translations
content = content.replace(
    '>WHO WE ARE (CREW)<',
    ' data-i18n="nav.crew">WHO WE ARE (CREW)<'
)
content = content.replace(
    '>SERVICES<',
    ' data-i18n="nav.services">SERVICES<'
)
content = content.replace(
    '>PARTNERSHIP<',
    ' data-i18n="nav.partnership">PARTNERSHIP<'
)
content = content.replace(
    '>Member<',
    ' data-i18n="nav.member">Member<'
)
content = content.replace(
    '>LOGIN<',
    ' data-i18n="nav.login">LOGIN<'
)
content = content.replace(
    '>JOIN<',
    ' data-i18n="nav.join">JOIN<'
)
content = content.replace(
    '>INQUIRY<',
    ' data-i18n="nav.inquiry">INQUIRY<'
)

# Hero section - badge
content = content.replace(
    '>Elite Zepeto Creator Crew<',
    ' data-i18n="hero.badge">Elite Zepeto Creator Crew<'
)

# Hero - title (note: handling the neon-purple span separately)
content = content.replace(
    '>Dream <span class="neon-purple">Realized</span><br>Inside Meta.<',
    '><span data-i18n="hero.title1">Dream</span> <span class="neon-purple" data-i18n="hero.title2">Realized</span><br><span data-i18n="hero.title3">Inside Meta.</span><'
)

# Hero - subtitle
content = content.replace(
    '>Cauchemar Crew는 15명의 정예 멤버로 구성된 제페토 크리에이터 크루입니다.\n                    공식 크리에이터 15명의 영향력과 3D 기술력으로 브랜드의 가치를 가상 세계에 구현합니다.<',
    ' data-i18n="hero.subtitle">Cauchemar Crew는 15명의 정예 멤버로 구성된 제페토 크리에이터 크루입니다.\n                    공식 크리에이터 15명의 영향력과 3D 기술력으로 브랜드의 가치를 가상 세계에 구현합니다.<'
)

# Hero - CTAs
content = content.replace(
    '>협업 문의하기<',
    ' data-i18n="hero.cta_inquiry">협업 문의하기<'
)
content = content.replace(
    '>크루 만나기<',
    ' data-i18n="hero.cta_crew">크루 만나기<'
)

# Expertise section title
content = content.replace(
    '>OUR EXPERTISE<',
    ' data-i18n="expertise.title">OUR EXPERTISE<'
)
content = content.replace(
    '>최고 수준의 제페토 크리에이션 서비스<',
    ' data-i18n="expertise.subtitle">최고 수준의 제페토 크리에이션 서비스<'
)

# 3D Item Production
content = content.replace(
    '>3D Item Production<',
    ' data-i18n="expertise.item_title">3D Item Production<'
)

# Live Streaming
content = content.replace(
    '>Live Streaming & PPL<',
    ' data-i18n="expertise.live_title">Live Streaming & PPL<'
)

# Video Creative
content = content.replace(
    '>Video Creative<',
    ' data-i18n="expertise.video_title">Video Creative<'
)

# World Construction
content = content.replace(
    '>World Construction<',
    ' data-i18n="expertise.world_title">World Construction<'
)

# SNS Marketing
content = content.replace(
    '>SNS Marketing<',
    ' data-i18n="expertise.sns_title">SNS Marketing<'
)

# Brand Partnership
content = content.replace(
    '>Brand Partnership<',
    ' data-i18n="expertise.brand_title">Brand Partnership<'
)

with open('projects/Cauchemar/cauchemar.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added data-i18n attributes to cauchemar.html")
print("   - Navigation links")
print("   - Hero section (badge, title, subtitle, CTAs)")
print("   - Expertise section titles")
