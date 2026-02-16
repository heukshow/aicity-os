# DIRECT FIX - Replace the entire inquiry form section with proper data-i18n

with open('projects/Cauchemar/inquiry.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all the old data-ko/data-en attributes to data-i18n
replacements = [
    # Page headers
    ('data-i18n="inquiry.title">비즈니스 문의', 'data-i18n="inquiry.title">Business Inquiry'),
    
    # Remove all data-ko and data-en attributes and replace with proper Korean defaults
    ('data-ko="클라이언트 정보"\r\n                        data-en="Client Information">클라이언트 정보', 'data-i18n="inquiry.section_client">클라이언트 정보'),
    ('data-ko="이름 *" data-en="Name *">이름 *', 'data-i18n="inquiry.name">이름 *'),
    ('data-ko="이메일 *" data-en="Email *">이메일 *', 'data-i18n="inquiry.email">이메일 *'),
    ('data-ko="회사명" data-en="Company Name">회사명', 'data-i18n="inquiry.company">회사명'),
    ('data-ko="연락처" data-en="Phone">연락처', 'data-i18n="inquiry.phone">연락처'),
    ('data-ko="프로젝트 정보" data-en="Project Information">프로젝트 정보', 'data-i18n="inquiry.section_project">프로젝트 정보'),
    ('data-ko="프로젝트 제목 *" data-en="Project Title *">프로젝트 제목 *', 'data-i18n="inquiry.project_title">프로젝트 제목 *'),
    ('data-ko="예산 범위" data-en="Budget Range">예산 범위', 'data-i18n="inquiry.budget">예산 범위'),
    ('data-ko="프로젝트 시작 희망일" data-en="Preferred Start Date">프로젝트 시작 희망일', 'data-i18n="inquiry.start_date">프로젝트 시작 희망일'),
    ('data-ko="프로젝트 상세 설명 *" data-en="Project Description *">프로젝트 상세 설명 *', 'data-i18n="inquiry.description">프로젝트 상세 설명 *'),
    ('data-ko="문의 제출" data-en="Submit Inquiry">문의 제출', 'data-i18n="inquiry.submit">문의 제출'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Now need to add inquiry translations to translations.js for these new keys
with open('projects/Cauchemar/inquiry.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed inquiry.html with proper data-i18n attributes!")
print("🔍 Now updating translations.js...")
